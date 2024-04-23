import json, urllib.request, os, shutil

from app.data.activities import ACTIVITY_NAMES
from app.data.classhash import CLASS_HASH

BUNGIE_BASE = "https://bungie.net/"
BUNGIE_API_BASE = "https://bungie.net/Platform/"

class DestinyManifest():
    def __init__(self):
        self.ActivityNames = None
        self.ActivityTypeNames = None
        self.ItemDefinitions = None
        self.CacheFolder = None

    def update(self):
        self.CacheFolder = GetCacheFolder()
        self.ActivityTypeNames = GetActivityTypeNames()
        self.VersionNumber = GetVersionNumber()
        self.ItemDefinitions = GetInventoryItemDefinitions()
        self.ActivityNames = GetActivityNames()
        self.ClassHash = GetClassDefinition()

        return self
    

def GetCacheFolder():
    # get current file path and go up two directories
    path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    path = os.path.join(path, 'cache')
    os.makedirs(path, exist_ok=True)
    return path


def GetVersionNumber():
    print("Check version number")
    # get version from manifest file
    manifestPaths = json.loads(urllib.request.urlopen(BUNGIE_API_BASE + "/Destiny2/Manifest/").read())["Response"]
    version = manifestPaths['version']
    cacheRoot = GetCacheFolder()

    # if version file exists and matches response, continue
    if os.path.exists(os.path.join(cacheRoot, version)):
        print("Version check passed")
        return

    # if version file does not exist or does not match
    print("Version check failed, deleting cache")
    # delete existing cache folder
    shutil.rmtree(cacheRoot, ignore_errors=True)
    print("Updating version")
    # create cache folder
    GetCacheFolder()
    versionFilePath = os.path.join(cacheRoot, version)
    # create new version file
    with open(file=versionFilePath, mode='w', encoding='utf-8') as f:
        f.write(version)


def SaveToCache(aDefinition, aJsonBlob):
    # set root path
    filePath = os.path.join(GetCacheFolder(), aDefinition)
    with open(file=filePath, mode='w', encoding='utf-8') as f:
        json.dump(aJsonBlob, f, ensure_ascii=False, indent=4)


def LoadFromCache(aDefinition):
    filePath = os.path.join(GetCacheFolder(), aDefinition)
    exists = os.path.exists(filePath)
    if not exists:
        return None, False
    with open(file=filePath, mode='r', encoding='utf-8') as f:
        blob = json.load(f)
    return blob, True


def GetManifestDefinitions(definition):
    print("Get %s" % definition)
    print("Check %s saved in cache" % definition)
    blob, exists = LoadFromCache(definition)
    if exists:
        print("Found %s in cache" % definition)
        return blob
    
    manifestPaths = json.loads(urllib.request.urlopen(BUNGIE_API_BASE + "/Destiny2/Manifest/").read())["Response"]
    manifestPath = manifestPaths["jsonWorldComponentContentPaths"]["en"][definition]
    print("Get %s from '%s'" % (definition, BUNGIE_BASE + manifestPath))
    DefinitionQuery = urllib.request.urlopen(BUNGIE_BASE + manifestPath).read()
    print("Unpack and parse %s" % definition)

    DefinitionQuery = json.loads(DefinitionQuery)
    print("Json'd %s and cache'd" % definition)
    SaveToCache(definition, DefinitionQuery)

    return DefinitionQuery


def GetInventoryItemDefinitions():
    return GetManifestDefinitions("DestinyInventoryItemDefinition")


def GetClassDefinition():
    return CLASS_HASH

def GetActivityNames():
    data = GetManifestDefinitions("DestinyActivityDefinition")

    result = {str(data[k]["hash"]): data[k]["displayProperties"]["name"] for k in data.keys()}
    return result


def GetActivityTypeNames():
    # data = GetManifestDefinitions("DestinyActivityTypeDefinition")
    #result = {str(data[k]["index"]): data[k]["displayProperties"]["name"] for k in data.keys() if "name" in data[k]["displayProperties"]}
    return ACTIVITY_NAMES
