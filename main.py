"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please contact me on Discord: DougTheDruid#2784
"""
import pyglet
import globals
import time
import multiprocessing
from base64 import b64decode
from win32gui import GetWindowText, GetForegroundWindow
from pyglet.text import Label
from pyglet.gl import Config
from helpers import SOT_WINDOW, SOT_WINDOW_H, SOT_WINDOW_W, foreground_batch, background_batch, \
    version, logger, LabelOutline
from mapping import ship_keys, world_events_keys
from sot_hack import SoTMemoryReader, ActorsReader
from Modules import (
    ShipModule,
    CrewsModule,
    WorldEventsModule
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

        shared_list_to_delete.clear()

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
                ship = ShipModule(key, *args, smr.my_coords)
                smr.display_objects.append(ship)

            elif args[-1] == "CrewService":
                smr.crew_data = CrewsModule(key, *args)

            elif args[-1] in world_events_keys:
                world_event = WorldEventsModule(key, *args, smr.my_coords)
                smr.display_objects.append(world_event)


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
    logger.info(
        b64decode("RG91Z1RoZURydWlkJ3MgRVNQIEZyYW1ld29yayBTdGFydGluZw==").decode("utf-8")
    )
    logger.info(f"Hack Version: {version}")

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

            # Draw our main batch & FPS counter at the bottom left
            background_batch.draw()
            foreground_batch.draw()
            fps_display.draw()

    # Shared data for multiprocessing
    multiprocess_manager = multiprocessing.Manager()
    multiprocess_lock = multiprocess_manager.Lock()
    shared_dict_new = multiprocess_manager.dict()
    shared_list_to_delete = multiprocess_manager.list()

    # We schedule an "update all" to scan all actors every 5seconds
    # pyglet.clock.schedule_interval(generate_all, 5)
    multiprocessing.Process(target=generate_all, 
                            args=(shared_dict_new, shared_list_to_delete, multiprocess_lock),
                            daemon=True).start()

    # We schedule a check to make sure the game is still running every 3 seconds
    pyglet.clock.schedule_interval(globals.rm.check_process_is_active, 3)

    # We schedule a basic graphics load which is responsible for updating
    # the actors we are interested in (from our generate_all). Runs as fast as possible
    pyglet.clock.schedule(update_graphics)

    # Adds an FPS counter at the bottom left corner of our pyglet window
    # Note: May not translate to actual FPS, but rather FPS of the program
    fps_display = pyglet.window.FPSDisplay(window)

    # The label for showing all players on the server under the count
    # This purely INITIALIZES it does not inherently update automatically
    crew_list: list[Label] = list()

    for x in range(6):
        crew_list.append(LabelOutline("", x=SOT_WINDOW_W * 0.85, multiline=True, width=1000,
                            y=(SOT_WINDOW_H-25) * 0.9 + 25 * x, batch=foreground_batch, shadows_batch=background_batch, color=(0, 0, 0, 255)))
        
    # Note: The width of 300 is the max pixel width of a single line
    # before auto-wrapping the text to the next line. Updated in on_draw()

    # Runs our application, targeting a specific refresh rate (1/60 = 60fps)
    pyglet.app.run()
    # Note - ***Nothing past here will execute as app.run() is a loop***
