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
        "Name": "Shipwreck",
    },
    "BP_SkellyFort_RitualSkullCloud_C": {
        "Name": "Fort of the Damned",
    },
    "BP_LegendSkellyFort_SkullCloud_C": {
        "Name": "Fort of Fortune",
    },
    "BP_GhostShips_Signal_Flameheart_NetProxy_C": {
        "Name": "Ghost Fleet",
    },
    "BP_SkellyFort_SkullCloud_C": {
        "Name": "Skeleton Fort",
    },
    "BP_SkellyShip_ShipCloud_C": {
        "Name": "Skeleton Fleet",
    },
    "BP_AshenLord_SkullCloud_C": {
        "Name": "Ashen Lord",
    },
}

world_events_keys = set(world_events.keys())
ship_keys = set(ships.keys())
