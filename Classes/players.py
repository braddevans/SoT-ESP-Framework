import struct
import globals
from helpers import OFFSETS

class Player:
    tracker = dict()

    def __init__(self, address):
        self.address = address
        self._name = ""
        self._name_initted = False

    @property
    def name(self):
        if not self._name_initted:
            name_ptr = globals.rm.read_ptr(self.address + OFFSETS.get("PlayerState.PlayerName"))
            self._name = globals.rm.read_string(name_ptr)
            if not self._name:
                self._name = 'Player'
            else:
                self._name_initted = True
            
        return self._name


class Crew:
    tracker = dict()

    def __init__(self, address, guid, size: int, color: tuple[int], players: list[Player], ship: str = "Ship"):
        self.address = address
        self.guid = guid
        self.size = size
        self.color = color
        self.ship = ship
        self.players = players

        Crew.tracker[guid] = self


class Ship:
    def __init__(self, address):
        self.address = address

    def get_crew(self) -> Crew:
        crew_onwership_ptr = globals.rm.read_ptr(self.address + OFFSETS.get("Ship.CrewOwnershipComponent"))
        guid = globals.rm.read_bytes(crew_onwership_ptr + OFFSETS.get("CrewOwnershipComponent.CachedCrewId"), 16)
        guid = struct.unpack("<iiii", guid)

        if guid in Crew.tracker:
            return Crew.tracker[guid]
        else:
            return None