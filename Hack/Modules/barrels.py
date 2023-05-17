import globals
from helpers import calculate_distance, object_to_screen, OFFSETS
from Graphics.elements import LabelPanel
from Modules import DisplayObject
from Classes import Barrel


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
        self.prev_sum = 0

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
                         y=self.screen_coords[1], multiline=True, width=500)

        return LabelPanel(self.text_str, x=0, y=0, multiline=True, width=500)

    def update(self, my_coords: dict):
        if self._get_actor_id(self.address) != self.actor_id:
            self.to_delete = True
            self.text_render.delete()
            return

        if not globals.barrels_should_update:
            self.text_render.visible = False
            return

        self.my_coords = my_coords
        new_distance = calculate_distance(self.coords, self.my_coords)
        self.screen_coords = object_to_screen(self.my_coords, self.coords)

        if self.screen_coords:
            new_barrels_content = ""
            nodes = list()
            items_count = list()

            container_nodes = Barrel.container_nodes(self.storage_container_component)
            for i in range(0, container_nodes[1]):
                node = (container_nodes[0] + i * OFFSETS.get("StorageContainerNode.Size"))
                nodes.append(node)
                items_count.append(Barrel.node_count(node))

            total_items_count = sum(items_count)

            # If barrel is empty
            if total_items_count == 0:
                self.text_render.visible = False
                return

            # Should we update barrel's content
            if total_items_count != self.prev_sum:
                self.prev_sum = total_items_count

                for i, node in enumerate(nodes):
                    item_name = Barrel.node_name(node)
                    new_barrels_content += f"\n- {items_count[i]} {item_name}"

            self.text_render.visible = True
            self.text_render.x = self.screen_coords[0]
            self.text_render.y = self.screen_coords[1]
  
            # If barrel's content have been updated
            if new_barrels_content != "":
                self.text_render.text = f"Barrel ({self.distance}m)"
                self.text_render.text += new_barrels_content
            else:
                self.text_render.label.text.replace(f'{self.distance}m', f'{new_distance}m')
            
            self.distance = new_distance

        else:
            self.text_render.visible = False

    def _delete(self):
        self.text_render.delete()
