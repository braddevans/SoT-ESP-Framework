"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

from pyglet.shapes import Circle
from pyglet.text import Label

from Data.mapping import everything
from Modules.display_object import DisplayObject
from utils.helpers import calculate_distance, object_to_screen, main_batch, \
    TEXT_OFFSET_X, TEXT_OFFSET_Y

CIRCLE_COLOR = (100, 100, 100)  # The color we want the indicator circle to be
CIRCLE_SIZE = 3  # The size of the indicator circle we want


class ALL_ESP(DisplayObject):
    def __init__(self, memory_reader, actor_id, address, my_coords, raw_name):
        # Initialize our super-class
        super().__init__(memory_reader)

        self.actor_id = actor_id
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name

        # Generate our BP info
        self.name = everything.get(self.raw_name).get("Name")
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        # All of our actual display information & rendering
        self.color = CIRCLE_COLOR
        self.text_str = self._built_text_string()
        self.text_render = self._build_text_render()
        self.icon = self._build_circle_render()

        # Used to track if the display object needs to be removed
        self.to_delete = False

    def _build_circle_render(self) -> Circle:
        if self.screen_coords:
            return Circle(self.screen_coords[0], self.screen_coords[1],
                          CIRCLE_SIZE, color=self.color, batch=main_batch)

        return Circle(0, 0, 10, color=self.color, batch=main_batch)

    def _built_text_string(self) -> str:
        return f"{self.name} - {self.distance}m"

    def _build_text_render(self) -> Label:
        if self.screen_coords:
            return Label(self.text_str,
                         x=self.screen_coords[0] + TEXT_OFFSET_X,
                         y=self.screen_coords[1] + TEXT_OFFSET_Y,
                         font_size=9,
                         batch=main_batch)

        return Label(self.text_str, x=0, y=0, batch=main_batch)

    def update(self, my_coords: dict):
        if self._get_actor_id(self.address) != self.actor_id:
            self.to_delete = True
            self.icon.delete()
            self.text_render.delete()
            return

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        new_distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        if self.screen_coords:
            self.text_render.visible = True
            self.icon.visible = True

            # Update the position of our circle and text
            self.icon.x = self.screen_coords[0]
            self.icon.y = self.screen_coords[1]
            self.text_render.x = self.screen_coords[0] + TEXT_OFFSET_X
            self.text_render.y = self.screen_coords[1] + TEXT_OFFSET_Y

            # Update our text to reflect out new distance
            self.distance = new_distance
            self.text_str = self._built_text_string()
            self.text_render.text = self.text_str

        else:
            # if it isn't on our screen, set it to invisible to save resources
            self.text_render.visible = False
            self.icon.visible = False
