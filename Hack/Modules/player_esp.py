from helpers import calculate_distance, object_to_screen, LabelPanel
from Modules import DisplayObject
from Classes import Player, Crew


class PlayerEspModule(DisplayObject):

    def __init__(self, actor_id, address, raw_name, my_coords):
        # Initialize our super-class
        super().__init__()

        self.actor_id = actor_id
        self.address = address
        self.actor_root_comp_ptr = self._get_root_comp_address(address)
        self.my_coords = my_coords
        self.raw_name = raw_name

        # Generate our Player's info
        self.name = Player.get_name(self.address)
        self.crew = Player.get_crew_guid(self.address)
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.distance = calculate_distance(self.coords, self.my_coords)

        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        # All of our actual display information & rendering
        self.text_str = self._built_text_string()
        self.text_render = self._build_text_render()

        # Used to track if the display object needs to be removed
        self.to_delete = False

    def _built_text_string(self) -> str:
        return f"{self.name} ({self.distance}m)"

    def _build_text_render(self) -> LabelPanel:
        if self.screen_coords:
            return LabelPanel(self.text_str,
                         x=self.screen_coords[0],
                         y=self.screen_coords[1],
                         line_color=(0, 0, 0, 0))

        return LabelPanel(self.text_str, x=0, y=0, line_color=(0, 0, 0, 0))

    def update(self, my_coords: dict):
        if self._get_actor_id(self.address) != self.actor_id:
            self.to_delete = True
            self.text_render.delete()
            return

        if not self.name:
            self.name = Player.get_name(self.address)

        if not self.crew:
            self.crew = Player.get_crew_guid(self.address)

        self.my_coords = my_coords
        self.coords = self._coord_builder(self.actor_root_comp_ptr,
                                          self.coord_offset)
        self.coords["z"] += 1.1

        new_distance = calculate_distance(self.coords, self.my_coords)
        self.screen_coords = object_to_screen(self.my_coords, self.coords)
        if self.screen_coords:
            self.screen_coords = (self.screen_coords[0] - self.text_render.content_width / 2, self.screen_coords[1])
            
        if self.screen_coords:
            self.text_render.visible = True

            # Update the position of our circle and text
            self.text_render.x = self.screen_coords[0]
            self.text_render.y = self.screen_coords[1]
            
            if self.crew and self.crew in Crew.tracer:
                self.text_render.color = Crew.tracker[self.crew].color

            # Update our text to reflect out new distance
            self.distance = new_distance
            self.text_str = self._built_text_string()
            self.text_render.text = self.text_str

        else:
            # if it isn't on our screen, set it to invisible to save resources
            self.text_render.visible = False

    def _delete(self):
        self.text_render.delete()
