import win32api
import globals
import time
from helpers import OFFSETS, CONFIG
from Modules import DisplayObject
from Classes import Player

TOTAL_SCOPE_TIME = 0.4

class GlobalModule(DisplayObject):
    items_map = {}

    def __init__(self):
        super().__init__()

        self.local_player = Player.local_player_pawn
        self.old_player_state = globals.rm.read_ptr(self.local_player + OFFSETS.get("AthenaCharacter.OldPlayerState"))
        self._weilded_component = globals.rm.read_ptr(self.local_player + OFFSETS.get("AthenaCharacter.WieldedItemComponent"))
        self.to_delete = False

        self._desired_fov = CONFIG.get("FOV")
        self._desired_scope_fov = CONFIG.get("SCOPE_FOV")
        self.scope_time = 0
        self.last_recorded_scope_time = 0
        self.last_fov_value = self._desired_fov
        self.last_fov_state = -1  # 0 = decreasing, 1 = increasing
        globals.rm.write_float(globals.smr.player_camera_manager + OFFSETS.get("PlayerCameraManager.DefaultFOV") + 4, self._desired_fov)
        globals.fov = self.last_fov_value


    def update_fov(self):
        self.currently_weilded_item = globals.rm.read_ptr(self._weilded_component + OFFSETS.get("WieldedItemComponent.CurrentlyWieldedItem"))
        self.currently_weilded_item_id = globals.rm.read_int(self.currently_weilded_item + OFFSETS.get('Actor.actorId'))
        if self.currently_weilded_item_id not in GlobalModule.items_map:
            GlobalModule.items_map[self.currently_weilded_item_id] = globals.rm.read_gname(self.currently_weilded_item_id)
        
        should_lower_fov = GlobalModule.items_map[self.currently_weilded_item_id].startswith('BP_Spyglass') and win32api.GetKeyState(0x01) < 0 or \
                           GlobalModule.items_map[self.currently_weilded_item_id].startswith('BP_wpn_sniper_rifle') and win32api.GetKeyState(0x02) < 0

        if should_lower_fov and self.scope_time < TOTAL_SCOPE_TIME:
            if self.last_fov_state != 1:
                self.last_recorded_scope_time = time.time()
                self.last_fov_state = 1

            self.scope_time += time.time() - self.last_recorded_scope_time
            if self.scope_time > TOTAL_SCOPE_TIME:
                self.scope_time = TOTAL_SCOPE_TIME


        elif not should_lower_fov and self.scope_time > 0:
            if self.last_fov_state != 0:
                self.last_recorded_scope_time = time.time()
                self.last_fov_state = 0

            self.scope_time -= time.time() - self.last_recorded_scope_time
            if self.scope_time < 0:
                self.scope_time = 0
   
        if self.last_fov_state != -1:
            self.last_recorded_scope_time = time.time()   
            self.last_fov_value = self._desired_scope_fov + (self._desired_fov - self._desired_scope_fov) * (1 - self.scope_time / TOTAL_SCOPE_TIME)
            globals.rm.write_float(globals.smr.player_camera_manager + OFFSETS.get("PlayerCameraManager.DefaultFOV") + 4, self.last_fov_value)

            if self.scope_time == TOTAL_SCOPE_TIME or self.scope_time == 0:
                self.last_fov_state == -1
        
            globals.fov = self.last_fov_value
    

    def update(self):
        globals.local_player_activity = int.from_bytes(globals.rm.read_bytes(self.old_player_state + OFFSETS.get("AthenaPlayerState.PlayerActivity"), 1), byteorder='little')
        globals.barrels_should_update = globals.local_player_activity == 6 and Player.local_player_handles == "BP_MerchantCrate_AnyItemCrate_Wieldable_C"

        if self._desired_fov != self._desired_scope_fov and self._desired_fov > 0:
            self.update_fov()
        

    def _delete(self):
        pass
