"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""

import struct
import abc
from utils.helpers import OFFSETS
from utils.memory_helper import ReadMemory


class DisplayObject(metaclass=abc.ABCMeta):

    def __init__(self, memory_reader: ReadMemory):
        self.rm = memory_reader
        self.coord_offset = OFFSETS.get('SceneComponent.ActorCoordinates')

    def _get_actor_id(self, address: int) -> int:
        return self.rm.read_int(
            address + OFFSETS.get('Actor.actorId')
        )

    def _get_root_comp_address(self, address: int) -> int:
        return self.rm.read_ptr(
            address + OFFSETS.get("Actor.rootComponent")
        )

    def _coord_builder(self, root_comp_ptr: int, offset: int) -> dict:
        actor_bytes = self.rm.read_bytes(root_comp_ptr + offset, 24)
        unpacked = struct.unpack("<ffffff", actor_bytes)

        coordinate_dict = {"x": unpacked[0] / 100, "y": unpacked[1] / 100,
                           "z": unpacked[2] / 100}
        return coordinate_dict

    @abc.abstractmethod
    def update(self, my_coords):
        """
        Required implementation method that we can call to update
        the objects data in a quick fashion vs scanning every actor.
        """
