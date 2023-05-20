import struct
import globals
from helpers import OFFSETS

def get_item_short_name(name):
    if "cannon_ball" in name:
        return "Cannon Ball"
    if "cannonball_chain_shot" in name:
        return "Cannon Chain"
    if "cannonball_Grenade" in name:
        return "Dispersion Ball"
    if "cannonball_cur_fire" in name:
        return "Fire Ball"
    if "cannonball_cur" in name:
        return "Cursed Cannon Ball"
    if "repair_wood" in name:
        return "Wood"
    if "PomegranateFresh" in name:
        return "Granate"
    if "CoconutFresh" in name:
        return "Coconut" 
    if "BananaFresh" in name:
        return "Banana"
    if "PineappleFresh" in name:
        return "Pineapple"
    if "MangoFresh" in name:
        return "Mango"
    if "GrubsFresh" in name:
        return "Grubs"
    if "LeechesFresh" in name:
        return "Leeches"
    if "EarthwormsFresh" in name:
        return "Earthworms"
    if "fireworks_flare" in name:
        return "Flare"
    if "fireworks_rocket" in name:
        return "Fireworks S"
    if "fireworks_cake" in name:
        return "Fireworks M"
    if "fireworks_living" in name:
        return "Fireworks L"
    if "MapInABarrel" in name:
        return "Scroll"


class Barrel:
    """BP_IslandStorageBarrel_"""
    items_map = {}

    @staticmethod
    def get_item_short_name(name):
        if "cannon_ball" in name:
            return "Cannon Ball"
        if "cannonball_chain_shot" in name:
            return "Cannon Chain"
        if "cannonball_Grenade" in name:
            return "Dispersion Ball"
        if "cannonball_cur_fire" in name:
            return "Fire Ball"
        if "cannonball_cur" in name:
            return "Cursed Cannon Ball"
        if "repair_wood" in name:
            return "Wood"
        if "PomegranateFresh" in name:
            return "Granate"
        if "CoconutFresh" in name:
            return "Coconut" 
        if "BananaFresh" in name:
            return "Banana"
        if "PineappleFresh" in name:
            return "Pineapple"
        if "MangoFresh" in name:
            return "Mango"
        if "GrubsFresh" in name:
            return "Grubs"
        if "LeechesFresh" in name:
            return "Leeches"
        if "EarthwormsFresh" in name:
            return "Earthworms"
        if "fireworks_flare" in name:
            return "Flare"
        if "fireworks_rocket" in name:
            return "Fireworks S"
        if "fireworks_cake" in name:
            return "Fireworks M"
        if "fireworks_living" in name:
            return "Fireworks L"
        if "MapInABarrel" in name:
            return "Scroll"

    @staticmethod
    def storage_container_component(actor):
        return globals.rm.read_ptr(actor + OFFSETS.get("Barrel.StorageContainerComponent"))
    
    @staticmethod
    def container_nodes(actor):
        container_nodes = globals.rm.read_bytes(
            actor + OFFSETS.get("StorageContainerComponent.ContainerNodes") + OFFSETS.get("StorageContainerBackingStore.ContainerNodes"), 16
        )
        return struct.unpack("<Qii", container_nodes)
    
    @classmethod
    def node_name(cls, actor):
        ItemDesc = globals.rm.read_ptr(actor + OFFSETS.get("StorageContainerNode.ItemDesc"))
        actor_id = globals.rm.read_int(ItemDesc + OFFSETS.get('Actor.actorId'))
        if actor_id not in cls.items_map:
            gname = globals.rm.read_gname(actor_id)
            cls.items_map[actor_id] = get_item_short_name(gname)
    
        return cls.items_map[actor_id]
    
    @staticmethod
    def node_count(actor):
        return globals.rm.read_int(actor + OFFSETS.get("StorageContainerNode.NumItems"))