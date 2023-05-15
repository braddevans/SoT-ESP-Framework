"""
Script that is responsible for looking through our SDK and determining
all of the offsets we specify automatically. Can that pass the output file
into the SoT ESP Framework
@Author https://github.com/DougTheDruid
@Source https://github.com/DougTheDruid/SoT-Python-Offset-Finder
@Framework https://github.com/DougTheDruid/SoT-ESP-Framework
For community support, please contact me on Discord: DougTheDruid#2784
"""
import json


ATHENA = "SDKs\\JSON-SDK\\Athena_Classes.json"
ENGINE = "SDKs\\JSON-SDK\\Engine_Classes.json"
ATHENA_AI = "SDKs\\JSON-SDK\\AthenaAI_Classes.json"
ENGINE_STRUCT = "SDKs\\JSON-SDK\\Engine_Structs.json"
ATHENA_STRUCT = "SDKs\\JSON-SDK\\Athena_structs.json"
SESSIONS_STRUCT = "SDKs\\JSON-SDK\\Sessions_Structs.json"


def get_offset(file_name, title, memory_object):
    """
    Opens the file the offset lives within, then reads through the lines within
    the file until we find the offset in hex.
    :param file_name: The file name where the offset lives within
    :param title: The title of the primary object which contains the value we
    want to pull data from
    :param memory_object: The data name from a parent object we want to pull
    the offset from
    :return: The int-converted version of the offset for a specific data field
    out of a parent object
    """
    offset = "Not Found"
    with open(file_name) as file_to_check:
        json_sdk_file = json.load(file_to_check)
        components = json_sdk_file.get(title, None)
        if components:
            attributes = components.get('Attributes', None)
            for attribute in attributes:
                if attribute['Name'] == memory_object:
                    offset = int(attribute.get('Offset'), 16)
    return offset


def get_size(file_name, title):
    """
    Determines the size of a struct or class given a specific file to look in
    :param file_name: The file name where the class or struct lives
    :param title: The class or struct name we want the size of
    :return: The int-converted version of the size for a class or struct
    """
    offset = "Not Found"
    with open(file_name) as file_to_check:
        json_sdk_file = json.load(file_to_check)
        components = json_sdk_file.get(title, None)
        if components:
            return int(components.get('ClassSize'), 16)
    return offset


if __name__ == '__main__':
    """
    We build a dictionary which contains all offset data, then save the 
    information into an offset file.
    """

    output = {
        "Actor.actorId": 24,  # The ID number associated with an actor type
        "SceneComponent.ActorCoordinates": 0x12c,  # Currently located at SceneComponent.RelativeScale3D+0xC

        "Actor.Owner": get_offset(ENGINE, "Actor", "Owner"),
        "CrewService.Crews":  get_offset(ATHENA, "CrewService", "Crews"),
        "Crew.Players": get_offset(ATHENA_STRUCT, "Crew", "Players"),
        "Crew.Size": get_size(ATHENA_STRUCT, "Crew"),
        "PlayerState.Size": get_size(ENGINE, "PlayerState"),
        "PlayerState.PlayerName": get_offset(ENGINE, "PlayerState", "PlayerName"),
        "Crew.CrewSessionTemplate": get_offset(ATHENA_STRUCT, "Crew", "CrewSessionTemplate"),
        "CrewSessionTemplate.MaxMatchmakingPlayers": get_offset(SESSIONS_STRUCT, "CrewSessionTemplate", "MaxMatchmakingPlayers"),
        "Actor.rootComponent": get_offset(ENGINE, "Actor", "RootComponent"),
        "CameraCacheEntry.MinimalViewInfo": get_offset(ENGINE_STRUCT, "CameraCacheEntry", "POV"),
        "GameInstance.LocalPlayers": get_offset(ENGINE, "GameInstance", "LocalPlayers"),
        "LocalPlayer.PlayerController": get_offset(ENGINE, "Player", "PlayerController"),
        "PlayerCameraManager.CameraCache": get_offset(ENGINE, "PlayerCameraManager", "CameraCache"),
        "PlayerCameraManager.DefaultFOV": get_offset(ENGINE, "PlayerCameraManager", "DefaultFOV"),
        "PlayerController.CameraManager": get_offset(ENGINE, "PlayerController", "PlayerCameraManager"),
        "PlayerController.AcknowledgedPawn": get_offset(ENGINE, "PlayerController", "AcknowledgedPawn"),
        "Pawn.PlayerState": get_offset(ENGINE, "Pawn", "PlayerState"),
        "World.OwningGameInstance": get_offset(ENGINE, "World", "OwningGameInstance"),
        "World.PersistentLevel": get_offset(ENGINE, "World", "PersistentLevel"),
        "World.Levels": get_offset(ENGINE, "World", "Levels"),
        "Ship.CrewOwnershipComponent": get_offset(ATHENA, "Ship", "CrewOwnershipComponent"),
        "CrewOwnershipComponent.CachedCrewId": get_offset(ATHENA, "CrewOwnershipComponent", "CachedCrewId"),
        "AthenaCharacter.OldPlayerState": get_offset(ATHENA, "AthenaCharacter", "OldPlayerState"),
        "AthenaPlayerState.PlayerActivity": get_offset(ATHENA, "AthenaPlayerState", "PlayerActivity"),
        "Barrel.StorageContainerComponent": get_offset("SDKs\\JSON-SDK\\BP_IslandStorageBarrel_Outpost_Classes.json", "BP_IslandStorageBarrel_Outpost_C", "StorageContainer"),
        "StorageContainerComponent.ContainerNodes": get_offset(ATHENA, "StorageContainerComponent", "ContainerNodes"),
        "StorageContainerBackingStore.ContainerNodes": get_offset(ATHENA_STRUCT, "StorageContainerBackingStore", "ContainerNodes"),
        "StorageContainerNode.Size": get_size(ATHENA_STRUCT, "StorageContainerNode"),
        "StorageContainerNode.ItemDesc": get_offset(ATHENA_STRUCT, "StorageContainerNode", "ItemDesc"),
        "StorageContainerNode.NumItems": get_offset(ATHENA_STRUCT, "StorageContainerNode", "NumItems"),
    }
    with open("../offsets.json", "w+") as outfile:
        outfile.write(json.dumps(output, indent=2, sort_keys=True))
