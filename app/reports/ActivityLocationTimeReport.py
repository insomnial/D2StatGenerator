import dateutil.parser
from datetime import datetime
import pandas as pd
from app.reports.ReportBase import Report
import plotly.express as px


class ActivityLocationTimeReport(Report):

    def save(self):
        super().save()

    def getName(self) -> str:
        return "[ALL] chart_tree - activity playtime; by type and location"

    def __init__(self, membershipType, membershipId, manifest) -> None:
        super().__init__(membershipType, membershipId, manifest)

    def generate(self, data) -> Report:
        df = self.generateData(data)
        fig = px.treemap(df, path=[px.Constant("all"), "category", "activity", "directorActivityHash"], values='playtime', template="plotly_dark",
                         branchvalues="total", labels=["playtime"],
                         title="Time wasted in specific activities and destinations"
                               "<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>"
                         )
        fig.update_traces(texttemplate=('%{label}<br>%{value:.2f}h (%{percentParent:.1%})'))
        self.fig = fig

        return self

    def generateData(self, data):
        category = []
        playtime = []
        activity = []
        directorActivity = []

        for datapoint in data:
            if "entries" not in datapoint: continue
            timestamp = dateutil.parser.parse(datapoint["period"]).timestamp()
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue

                starts = entry["values"]["startSeconds"]["basic"]["value"]
                ends = starts + entry["values"]["timePlayedSeconds"]["basic"]["value"]

                start_date = datetime.fromtimestamp(timestamp + starts)

                typus = "PvE"
                if datapoint["activityDetails"]["mode"] in [91, 90, 89, 84, 81, 80, 74, 73, 72, 71, 68, 65, 62, 61, 60, 59, 50, 48, 43, 45, 44, 41, 42, 37, 38, 31, 25, 15]:
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
                playtime.append(entry["values"]["timePlayedSeconds"]["basic"]["value"] / 60 / 60)

        df = pd.DataFrame({
            "category": category,
            "activity": activity,
            "directorActivityHash": directorActivity,
            "playtime": playtime,
        })
        return df
