import globals
from helpers import calculate_distance, object_to_screen, foreground_batch, background_batch, LabelPanel, OFFSETS
from Modules import DisplayObject
from Classes import Barrel, Player


class BarrelsModule(DisplayObject):

    def __init__(self, actor_id, address, raw_name, my_coords):
        # Initialize our super-class
        super().__init__()

        self.actor_id = actor_id
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name

        # Generate our Barrel's info
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)
        self.storage_container_component = Barrel.storage_container_component(self.address)
        globals.barrels_shared[self.storage_container_component] = ""

        # All of our actual display information & rendering
        self.text_str = self._built_text_string()
        self.text_render = self._build_text_render()

        # Used to track if the display object needs to be removed
        self.to_delete = False

    def _built_text_string(self) -> str:
        return f"Barrel ({self.distance}m)"

    def _build_text_render(self) -> LabelPanel:
        if self.screen_coords:
            return LabelPanel(self.text_str,
                         x=self.screen_coords[0],
                         y=self.screen_coords[1], multiline=True, width=1000)

        return LabelPanel(self.text_str, x=0, y=0, multiline=True, width=1000)

    def update(self, my_coords: dict):
        if self._get_actor_id(self.address) != self.actor_id:
            self.to_delete = True
            self.text_render.delete()

            with globals.barrels_lock:
                del globals.barrels_shared[self.storage_container_component]

            return

        if globals.local_player_activity != 6 or Player.local_player_handles == None:
            self.text_render.visible = False
            return

        if not (barrels_content := globals.barrels_shared[self.storage_container_component]):
            self.text_render.visible = False
            return
        

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)

        new_distance = calculate_distance(self.coords, self.my_coords)
        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        if self.screen_coords:
            self.text_render.visible= True
            self.text_render.x = self.screen_coords[0]
            self.text_render.y = self.screen_coords[1]

            self.distance = new_distance      
            self.text_render.text = f"Barrel ({self.distance}m)"
            self.text_render.text += barrels_content

        else:
            # if it isn't on our screen, set it to invisible to save resources
            self.text_render.visible = False

    def _delete(self):
        self.text_render.delete()
        with globals.barrels_lock:
            del globals.barrels_shared[self.storage_container_component]
