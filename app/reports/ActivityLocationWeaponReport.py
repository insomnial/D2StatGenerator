import dateutil.parser
import pandas as pd
from app.reports.ReportBase import Report
import plotly.express as px


class ActivityLocationWeaponReport(Report):
    def save(self):
        super().save()

    def getName(self) -> str:
        return "[ALL] chart_tree - weapons per activity type and location"

    def __init__(self, membershipType, membershipId, manifest) -> None:
        super().__init__(membershipType, membershipId, manifest)

    def generate(self, data) -> Report:
        df = self.generateData(data)

        fig = px.treemap(
            df,
            path=[px.Constant("all"), "category", "activity", "directorActivityHash", "weapon"], values='kills', template="plotly_dark",
            branchvalues="total", labels=["kills"],
            title="Weapon kills in specific activity types"
                  "<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>"
        )
        fig.update_traces(texttemplate=('%{label}<br>%{value} Kills (%{percentParent:.1%})'))
        self.fig = fig

        return self

    def generateData(self, data):

        category = []
        kills = []
        activity = []
        weapon = []
        directorActivity = []

        for datapoint in data:
            if "entries" not in datapoint: continue
            timestamp = dateutil.parser.parse(datapoint["period"]).timestamp()
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue

                if "weapons" not in entry["extended"]: continue
                for wp in entry["extended"]["weapons"]:

                    typus = "PvE"
                    if datapoint["activityDetails"]["mode"] in [91, 90, 89, 84, 81, 80, 74, 73, 72, 71, 68, 65, 62, 61, 60, 59, 50, 48, 32, 43, 45, 44, 41, 42, 37, 38, 31, 25, 15]:
                        typus = "PvP"
                    elif datapoint["activityDetails"]["mode"] in [75, 63]:
                        typus = "Gambit"
                    category.append(typus)
                    activity.append(self.manifest.ActivityTypeNames[datapoint["activityDetails"]["mode"]])
                    key = str(datapoint["activityDetails"]["directorActivityHash"])
                    key2 = str(datapoint["activityDetails"]["referenceId"])
                    if key2 in self.manifest.ActivityNames:
                        directorActivity.append(self.manifest.ActivityNames[key2])
                    elif key in self.manifest.ActivityNames:
                        directorActivity.append(self.manifest.ActivityNames[key])
                    else:
                        directorActivity.append(key)
                    weapon.append(self.manifest.ItemDefinitions[str(wp["referenceId"])]["displayProperties"]["name"])
                    kills.append(1 * wp["values"]["uniqueWeaponKills"]["basic"]["value"])

        df = pd.DataFrame({
            "category": category,
            "activity": activity,
            "directorActivityHash": directorActivity,
            "weapon": weapon,
            "kills": kills,
        })
        return df
