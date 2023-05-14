import struct
import globals
from helpers import OFFSETS


class Crew:
    tracker = dict()

    class CrewPlayer:
        """Playerstate for crew players tracking."""

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

    def __init__(self, address, guid, size: int, color: tuple[int], players: list[CrewPlayer], ship: str = "Ship"):
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


class Player:
    """Player class based on BP_PlayerPirate_C."""

    # Sets on SotMemoryReader initialization
    local_player_pawn = None
    
    @classmethod
    def is_local_player(cls, actor) -> bool:
        return cls.local_player_pawn == actor
    
    @classmethod
    def get_name(cls, actor) -> str:
        player_state = globals.rm.read_ptr(actor + OFFSETS.get("Pawn.PlayerState"))
        name_ptr = globals.rm.read_ptr(player_state + OFFSETS.get("PlayerState.PlayerName"))
        return globals.rm.read_string(name_ptr)
    
    @classmethod
    def get_crew(cls, actor) -> Crew:
        for crew in Crew.tracker:
            for player in Crew.tracker[crew].players:
                if player._name == cls.get_name(actor):
                    return Crew.tracker[crew]
        return None
    
    @classmethod
    def get_old_player_state(cls, actor) -> int:
        return globals.rm.read_ptr(actor + OFFSETS.get("AthenaCharacter.OldPlayerState"))
