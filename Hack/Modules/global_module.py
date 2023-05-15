import globals
from helpers import OFFSETS, CONFIG
from Modules import DisplayObject
from Classes import Player


class GlobalModule(DisplayObject):

    def __init__(self):
        super().__init__()

        self.local_player = Player.local_player_pawn
        self.old_player_state = globals.rm.read_ptr(self.local_player + OFFSETS.get("AthenaCharacter.OldPlayerState"))
        self.to_delete = False

        globals.rm.write_float(globals.smr.player_camera_manager + OFFSETS.get("PlayerCameraManager.DefaultFOV") + 4, CONFIG.get("FOV"))


    def update(self):
        globals.local_player_activity = int.from_bytes(globals.rm.read_bytes(self.old_player_state + OFFSETS.get("AthenaPlayerState.PlayerActivity"), 1), byteorder='little')
        globals.barrels_should_update[0] = globals.local_player_activity == 6 and Player.local_player_handles == "BP_MerchantCrate_AnyItemCrate_Wieldable_C"
            

    def _delete(self):
        ...
