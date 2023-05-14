"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please contact me on Discord: DougTheDruid#2784
"""
import pyglet
import globals
import time
import struct
import win32gui
import win32con
import multiprocessing
from base64 import b64decode
from win32gui import GetWindowText, GetForegroundWindow
from pyglet.text import Label
from pyglet.gl import Config
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, foreground_batch, background_batch, \
    version, logger, LabelOutline, OFFSETS
from mapping import ship_keys, world_events_keys
from sot_hack import SoTMemoryReader, ActorsReader, MemoryReaderOnly
from Classes.players import Player
from Modules import (
    ShipModule,
    CrewsModule,
    WorldEventsModule,
    PlayerEspModule,
    BarrelsModule,
    GlobalModule
)

# The FPS __Target__ for the program.
FPS_TARGET = 165

# See explanation in Main, toggle for a non-graphical debug
DEBUG = False

# Pyglet clock used to track time via FPS
clock = pyglet.clock.Clock()


def generate_all(_shared_dict_new: dict, _shared_list_to_delete: list, lock):
    """
    Triggers an entire read_actors call in our SoT Memory Reader. Will
    re-populate all of the display objects if something entered the screen
    or render distance.
    """

    actors_reader = ActorsReader() 

    while 1:
        actors_reader.read_actors()

        with lock:
            for actor_id, args in actors_reader.to_be_shared["new"].items():
                _shared_dict_new.update({actor_id: args})
            for actor_id in actors_reader.to_be_shared["to_delete"]:
                _shared_list_to_delete.append(actor_id)

        time.sleep(5.0)
        

def update_barrels(_barrels_shared, _barrels_should_update, _fps_target, lock):
    def get_item_short_name(name):
        if "cannon_ball" in name:
            return "Cannon Ball"
        if "cannonball_chain_shot" in name:
            return "Cannon Chain"
        if "cannonball_Grenade" in name:
            return "Dispersion Ball"
        if "cannonball_cur_fire" in name:
            return "Fire Ball"
        if "cannonball_cur" in name:
            return "Cursed Cannon Ball"
        if "repair_wood" in name:
            return "Wood"
        if "PomegranateFresh" in name:
            return "Granate"
        if "CoconutFresh" in name:
            return "Coconut" 
        if "BananaFresh" in name:
            return "Banana"
        if "PineappleFresh" in name:
            return "Pineapple"
        if "MangoFresh" in name:
            return "Mango"
        if "GrubsFresh" in name:
            return "Grubs"
        if "LeechesFresh" in name:
            return "Leeches"
        if "EarthwormsFresh" in name:
            return "Earthworms"
        if "fireworks_flare" in name:
            return "Flare"
        if "fireworks_rocket" in name:
            return "Fireworks S"
        if "fireworks_cake" in name:
            return "Fireworks M"
        if "fireworks_living" in name:
            return "Fireworks L"
        if "MapInABarrel" in name:
            return "Scroll"
    
    reader = MemoryReaderOnly()
    items_map = {}

    while 1:
        if _barrels_should_update[0]:
            if _barrels_shared:
                actors = list(_barrels_shared.keys())
                for actor in actors:
                    ret_value = ""

                    container_nodes = struct.unpack("<Qii", reader.rm.read_bytes(
                        actor + OFFSETS.get("StorageContainerComponent.ContainerNodes") + OFFSETS.get("StorageContainerBackingStore.ContainerNodes"), 16
                    ))

                    if container_nodes[1] > 0:
                        for i in range(0, container_nodes[1]):
                            node = (container_nodes[0] + i * OFFSETS.get("StorageContainerNode.Size"))
                            ItemDesc = reader.rm.read_ptr(node + OFFSETS.get("StorageContainerNode.ItemDesc"))
                            actor_id = reader.rm.read_int(ItemDesc + OFFSETS.get('Actor.actorId'))

                            if actor_id not in items_map:
                                gname = reader.rm.read_gname(actor_id)
                                items_map[actor_id] = get_item_short_name(gname)
                        
                            item_name = items_map[actor_id]
                            item_count = reader.rm.read_int(node + OFFSETS.get("StorageContainerNode.NumItems"))
                            ret_value += f'\n- {item_count} {item_name}'

                    if actor in _barrels_shared:
                        _barrels_shared[actor] = ret_value
            

        time.sleep(1/_fps_target)
    


def update_globals(_, global_module: GlobalModule):
    global_module.update()


def update_graphics(_):
    """
    Our main graphical loop which updates all of our "interesting" items.
    During a "full run" (update_all()), a list of the objects near us and we
    care about is generated. Each of those objects has a ".update()" method
    we use to re-poll data for that item (required per display_object.py)
    """
    # Update our players coordinate information
    smr.update_my_coords()

    # Delete old objects
    if shared_list_to_delete:
        for display_ob in smr.display_objects:
            if display_ob.actor_id in shared_list_to_delete:
                smr.display_objects.remove(display_ob)
                display_ob.delete()

        while shared_list_to_delete:
            key = shared_list_to_delete.pop()
            raw_name = key.split('__')[1]
            if raw_name.startswith('local_handler_'):
                Player.local_player_handles = None

    # If we have something new
    if shared_dict_new:

        # To be sure that main_shared_dict won't be changed during iteration
        dict_keys = list(shared_dict_new.keys())
        dict_values = list(shared_dict_new.values())

        # We saved all what we need, so we can clear shared dict now
        shared_dict_new.clear()

        # Creating new objects
        while dict_keys:
            key = dict_keys.pop()
            args = dict_values.pop()

            # We won't check if config enabled for each actor type, since we have already did this in read_actors
            # args[-1] == raw_name
            # key = actor_id

            if args[-1] in ship_keys:
                ship = ShipModule(*args, smr.my_coords)
                smr.display_objects.append(ship)

            elif args[-1] == "CrewService":
                smr.crew_data = CrewsModule(*args)

            elif args[-1] in world_events_keys:
                world_event = WorldEventsModule(*args, smr.my_coords)
                smr.display_objects.append(world_event)

            elif args[-1] == "BP_PlayerPirate_C" and not Player.is_local_player(args[1]):
                world_event = PlayerEspModule(*args, smr.my_coords)
                smr.display_objects.append(world_event)

            elif "BP_IslandStorageBarrel" in args[-1] or "gmp_bar" in args[-1]:
                barrel = BarrelsModule(*args, smr.my_coords)
                smr.display_objects.append(barrel)

            elif args[-1].startswith("local_handler_"):
                raw_name = args[-1].replace("local_handler_", '')
                Player.local_player_handles = raw_name

    # Initialize a list of items which are no longer valid in this loop
    to_remove = []

    # For each actor that is stored from the most recent run of read_actors
    for actor in smr.display_objects:
        # Call the update function within the actor object
        actor.update(smr.my_coords)

        # If the actor isn't the actor we expect (per .update), prepare to nuke
        if actor.to_delete:
            to_remove.append(actor)

    # Clean up any items which arent valid anymore
    for removable in to_remove:
        removable.delete()
        smr.display_objects.remove(removable)



if __name__ == '__main__':
    # Initialize our SoT Hack object, and do a first run of reading actors
    smr = SoTMemoryReader()

    # Custom Debug mode for using a literal python interpreter debugger
    # to validate our fields. Does not generate a GUI.
    if DEBUG:
        while True:
            smr.read_actors()

    # You may want to add/modify this custom config per the pyglet docs to
    # disable vsync or other options: https://tinyurl.com/45tcx6eu
    config = Config(double_buffer=True, depth_size=24, alpha_size=8)

    # Create an overlay window with Pyglet at the same size as our SoT Window
    window = pyglet.window.Window(SOT_WINDOW_W, SOT_WINDOW_H,
                                  vsync=True, style='overlay', config=config,
                                  caption="DougTheDruid's ESP Framework")
    hwnd = window._hwnd  # pylint: disable=protected-access

    # Move our window to the same location that our SoT Window is at
    window.set_location(SOT_WINDOW[0], SOT_WINDOW[1])

    # Trick to hide the window from alt-tab menu
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                                   win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_TOOLWINDOW)

    @window.event
    def on_draw():
        """
        The event which our window uses to determine what to draw on the
        screen. First clears the screen, then updates our player count, then
        draws both our batch (think of a canvas) & fps display
        """
        window.clear()

        if GetWindowText(GetForegroundWindow()) == "Sea of Thieves":
            # Update our player count Label & crew list
            if smr.crew_data:
                for x in range(0, len(smr.crew_data.crew_strings)):
                    crew_list[x].color = smr.crew_data.crew_strings[x][1]
                    crew_list[x].text = smr.crew_data.crew_strings[x][0]
                    if x == 0:
                        crew_list[x].y = (SOT_WINDOW_H-25) * 0.9
                    else:
                        crew_list[x].y = crew_list[x-1].y - 40 - ((20 * (crew_list[x-1].text.count('\n') - 1)) if x > 0 else 0 )
            
                for x in range(len(smr.crew_data.crew_strings), 6):
                    crew_list[x].text = ""

            # Batches
            background_batch.draw()
            foreground_batch.draw()
            fps_display.draw()

    # Shared data for multiprocessing `read_actors`
    multiprocess_manager = multiprocessing.Manager()
    multiprocess_lock = multiprocess_manager.Lock()
    shared_dict_new = multiprocess_manager.dict()
    shared_list_to_delete = multiprocess_manager.list()

    # Shared data for barrels reading
    barrels_manager = multiprocessing.Manager()
    barrels_lock = barrels_manager.Lock()
    barrels_shared = barrels_manager.dict()
    barrels_shared.keys()
    barrels_should_update = barrels_manager.list()
    barrels_should_update.append(False)
    globals.barrels_should_update = barrels_should_update
    globals.barrels_lock = barrels_lock
    globals.barrels_shared = barrels_shared

    # We schedule an "update all" to scan all actors every 5seconds
    # pyglet.clock.schedule_interval(generate_all, 5)
    multiprocessing.Process(target=generate_all, 
                            args=(shared_dict_new, shared_list_to_delete, multiprocess_lock),
                            daemon=True).start()
    
    multiprocessing.Process(target=update_barrels, 
                            args=(barrels_shared, barrels_should_update, 20, barrels_lock),
                            daemon=True).start()

    # We schedule a check to make sure the game is still running every 3 seconds
    pyglet.clock.schedule_interval_soft(globals.rm.check_process_is_active, 3)

    # We schedule a basic graphics load which is responsible for updating
    # the actors we are interested in (from our generate_all). Runs as fast as possible
    pyglet.clock.schedule_interval_soft(update_graphics, 1/FPS_TARGET)

    # We don't want to update global things on the same fps_target
    global_module = GlobalModule()
    pyglet.clock.schedule_interval_soft(update_globals, 1/30, global_module)

    # Adds an FPS counter at the bottom left corner of our pyglet window
    # Note: May not translate to actual FPS, but rather FPS of the program
    fps_display = pyglet.window.FPSDisplay(window)

    # The label for showing all players on the server under the count
    # This purely INITIALIZES it does not inherently update automatically
    crew_list: list[Label] = list()

    for x in range(6):
        crew_list.append(LabelOutline("", x=SOT_WINDOW_W * 0.85, multiline=True, width=1000,
                            y=(SOT_WINDOW_H-25) * 0.9 + 25 * x, batch=foreground_batch, shadows_batch=background_batch, color=(0, 0, 0, 255)))

    pyglet.app.run()
