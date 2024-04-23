from typing import Dict
import requests
from app.data.classhash import CLASS_HASH


API_ROOT_PATH = "https://www.bungie.net/Platform"


class BungieApi:
    __HEADERS: Dict[str, str]

    def __init__(self, api_key: str):
        self.__HEADERS = {"X-API-Key": api_key}
        pass

    def getProfile(self, membershipType, destinyMembershipId, components=[100]):
        params = {}
        if components is not None: params["components"] = components

        api_call = requests.get(f'{API_ROOT_PATH}/Destiny2/{membershipType}/Profile/{destinyMembershipId}', headers=self.__HEADERS, params=params)

        return (api_call.json())['Response']

    def getAccountStats(self, membershipType, destinyMembershipId):
        params = {}

        api_call = requests.get(f'{API_ROOT_PATH}/Destiny2/{membershipType}/Account/{destinyMembershipId}/Stats', headers=self.__HEADERS, params=params)

        return (api_call.json())['Response']

    def getActivities(self, membershipType, destinyMembershipId, characterId, page=0, count=250, mode=None):
        params = {}
        if page is not None: params["page"] = page
        if count is not None: params["count"] = count
        if mode is not None: params["mode"] = mode

        api_call = requests.get(f'{API_ROOT_PATH}/Destiny2/{membershipType}/Account/{destinyMembershipId}/Character/{characterId}/Stats/Activities/', headers=self.__HEADERS, params=params)
        json_ = (api_call.json())
        if ("Response" not in json_):
            print(json_)
        return json_['Response']

    def getPGCR(self, activityId):
        params = {}

        try:
            api_call = requests.get(f'{API_ROOT_PATH}/Destiny2/Stats/PostGameCarnageReport/{activityId}/', headers=self.__HEADERS, params=params, timeout=(10, 10))
        except:
            return None
        return (api_call.json())['Response']

    def getItem(self, itemReferenceId):
        pass
    
    def getCharacterClass(self, membershipType, destinyMembershipId, characterId):
        params = {}
        params['components'] = 200

        try:
            api_call = requests.get(f'{API_ROOT_PATH}/Destiny2/{membershipType}/Profile/{destinyMembershipId}/Character/{characterId}', headers=self.__HEADERS, params=params, timeout=(10, 10))
        except:
            return None
        
        classHash = (api_call.json())['Response']['character']['data']['classHash']

        return CLASS_HASH[classHash]