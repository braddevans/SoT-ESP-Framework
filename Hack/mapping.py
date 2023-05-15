"""
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-ESP-Framework
"""


ships = {
    # ------------ SHIPS / AI SHIPS ------------
    "BP_SmallShipTemplate_C": {
        "Name": "Sloop (Near)",
    },
    "BP_SmallShipNetProxy_C": {
        "Name": "Sloop",
    },

    "BP_MediumShipTemplate_C": {
        "Name": "Brig (Near)",
    },
    "BP_MediumShipNetProxy_C": {
        "Name": "Brig",
    },

    "BP_LargeShipTemplate_C": {
        "Name": "Galleon (Near)",
    },
    "BP_LargeShipNetProxy_C": {
        "Name": "Galleon",
    },

    "BP_AISmallShipTemplate_C": {
        "Name": "Skeleton Sloop (Near)",
    },
    "BP_AISmallShipNetProxy_C": {
        "Name": "Skeleton Sloop",
    },
    "BP_AILargeShipTemplate_C": {
        "Name": "Skeleton Galleon (Near)",
    },
    "BP_AILargeShipNetProxy_C": {
        "Name": "Skeleton Galleon",
    },
    # "BP_AggressiveGhostShip_C": {
    #     "Name": "Flameheart Galleon",
    # },  # To implement, must modify ship.py's update method for visibility
}

world_events = {
    "BP_Seagull01_32POI_Circling_Shipwreck_C": {
        "Name": "Shipwreck loot",
        "Color": (255, 255, 255, 200)
    },
    "BP_Shipwreck_01_a_NetProxy_C": {
        "Name": "Shipwreck",
        "Color": (255, 255, 255, 200)
    },
    "BP_Seagull01_8POI_C": {
        "Name": "Cargo Shipwreck",
        "Color": (255, 255, 255, 200)
    },
    "BP_Seagull01_8POI_LostShipments_C": {
        "Name": "Shipwreck LostShipments",
        "Color": (255, 255, 255, 200)
    },
    "BP_SkellyFort_RitualSkullCloud_C": {
        "Name": "Fort of the Damned",
        "Color": (255, 255, 255, 200)
    },
    "BP_LegendSkellyFort_SkullCloud_C": {
        "Name": "Fort of Fortune",
        "Color": (255, 255, 255, 200)
    },
    "BP_GhostShips_Signal_Flameheart_NetProxy_C": {
        "Name": "Ghost Fleet",
        "Color": (0, 212, 4, 200)
    },
    "BP_SkellyFort_SkullCloud_C": {
        "Name": "Skeleton Fort",
        "Color": (0, 153, 3, 200)
    },
    "BP_SkellyShip_ShipCloud_C": {
        "Name": "Skeleton Fleet",
        "Color": (0, 196, 3, 200)
    },
    "BP_AshenLord_SkullCloud_C": {
        "Name": "Ashen Lord",
        "Color": (255, 255, 255, 200)
    },
}

world_events_keys = set(world_events.keys())
ship_keys = set(ships.keys())
