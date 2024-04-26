import os
from itertools import zip_longest

from app.Director import Director
from app.bungieapi import BungieApi
import json

from app.internal_timer import Timer


class PGCRCollector:
    def __init__(self, membershipType, membershipId, api: BungieApi, pool) -> None:
        super().__init__()
        self.processPool = pool
        self.membershipType = membershipType
        self.membershipId = membershipId
        self.api = api
        self.characters = None
        self.activities = None
        self.displayName = None

    def getProfile(self):
        print("> Get profile")
        account_profile = self.api.getProfile(self.membershipType, self.membershipId)
        bungieGlobalDisplayName = account_profile['profile']['data']['userInfo']['bungieGlobalDisplayName']
        bungieGlobalDisplayNameCode = account_profile['profile']['data']['userInfo']['bungieGlobalDisplayNameCode']
        self.displayName = f'{bungieGlobalDisplayName}[{bungieGlobalDisplayNameCode}]'
        print(f"Found profile: {self.displayName}")
        return self
    
    def getDisplayName(self):
        return self.displayName

    def getCharacters(self):
        print("> Get Characters")
        account_stats = self.api.getAccountStats(self.membershipType, self.membershipId)
        allCharacters = account_stats['characters']
        self.characters = [c["characterId"] for c in allCharacters]
        print("Found characters: ", len(self.characters))
        for char in allCharacters:
            deleted = char['deleted']
            if deleted:
                className = None
            else:
                className = self.api.getCharacterClass(self.membershipType, self.membershipId, char['characterId'])
            print(f"{char['characterId']}{'' if className == None else ' | ' + className}")
        return self

    def getActivities(self, limit=None):
        print("> Get Activities")
        assert self.characters is not None
        assert len(self.characters) > 0

        existingPgcrList = [f[5:-5] for f in os.listdir(Director.GetPGCRDirectory(self.displayName))]

        self.activities = []
        for k, char_id in enumerate(self.characters):
            page = 0

            def downloadActivityPage(page):
                act = self.api.getActivities(self.membershipType, self.membershipId, char_id, page=page)
                if "activities" not in act:
                    return None
                return [e["activityDetails"]["instanceId"] for e in act["activities"] if e["activityDetails"]["instanceId"] not in existingPgcrList]

            while True:
                steps = 20
                print(k + 1, "/", len(self.characters), "|", char_id, "|", "pages", page + 1, "to", page + steps)
                activityGroups = self.processPool.amap(downloadActivityPage, range(page, page + steps)).get()
                realList = [e for e in activityGroups if e is not None]
                hasNull = len(realList) != steps
                for activityList in realList:
                    self.activities += activityList

                page += steps
                if hasNull:
                    break

                if limit is not None:
                    if len(self.activities) > limit:
                        break

            if limit is not None:
                if len(self.activities) > limit:
                    break
        print("Got ", len(self.activities), " activities that must be downloaded.")

        return self

    def getPGCRs(self):
        bungo = self.api

        def downloadPGCR(activity):
            id = activity
            tries = 0

            pgcr = None
            while pgcr == None and tries < 10:
                tries += 1
                pgcr = bungo.getPGCR(id)

            with open("%s/pgcr_%s.json" % (Director.GetPGCRDirectory(self.displayName), pgcr["activityDetails"]["instanceId"]), "w", encoding='utf-8') as f:
                f.write(json.dumps(pgcr))

        if len(self.activities) == 0:
            print("No activities to grab")
            return self

        from tqdm.auto import tqdm   
        list(tqdm(self.processPool.imap(downloadPGCR, self.activities), total=len(self.activities), desc="Downloading PGCRs"))
        return self

    def combineAllPgcrs(self):
        all = self.getAllPgcrs()
        with Timer("Write all PGCRs to one file"):
            with open(Director.GetAllPgcrFilename(self.displayName), "w", encoding='utf-8') as f:
                json.dump(all, f, ensure_ascii=False)
        return self

    def getAllPgcrs(self):

        def loadJson(fnameList):
            r = []
            for fname in fnameList:
                if fname is None:
                    continue
                with open(fname, "r", encoding='utf-8') as f:
                    try:
                        r.append(json.load(f))
                    except Exception:
                        print('Error on %s' % fname)
            return r

        with Timer("Get all PGCRs from individual files"):
            root = Director.GetPGCRDirectory(self.displayName)
            fileList = ["%s/%s" % (root, f) for f in os.listdir(root)]
            chunks = list(zip_longest(*[iter(fileList)] * 100, fillvalue=None))
            pgcrs = self.processPool.amap(loadJson, chunks).get()
            all = [item for sublist in pgcrs for item in sublist]
        return all
