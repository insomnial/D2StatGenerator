import pandas as pd
from app.reports.ReportBase import Report
import plotly.express as px


class ActivityCountReport(Report):
    def save(self):
        super().save()

    def getName(self) -> str:
        return "[ALL] chart_tree - activity count"

    def __init__(self, membershipType, membershipId, manifest) -> None:
        super().__init__(membershipType, membershipId, manifest)

    def generate(self, data) -> Report:
        df = self.generateData(data)

        fig = px.treemap(
            df,
            path=[px.Constant("all"), "type", "mode","directorActivity"], values='count', template="plotly_dark",
            branchvalues="total", labels=["count"],
            title="Times you entered a specific activity"
                  "<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>"
        )
        fig.update_traces(texttemplate=('%{label}<br>%{value} Activities (%{percentParent:.1%})'))
        self.fig = fig

        return self

    def generateData(self, data):
        from tqdm import tqdm

        typ = []
        mode = []
        directorActivity = []

        for datapoint in tqdm(data):
            if "entries" not in datapoint: continue
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue
                typus = "PvE"
                if datapoint["activityDetails"]["mode"] in [92, 91, 90, 89, 84, 81, 80, 74, 73, 72, 71, 68, 65, 62, 61,32, 60, 59, 32, 50, 48, 43, 45, 44, 41, 42, 37, 38, 31, 25, 15]:
                    typus = "PvP"
                elif datapoint["activityDetails"]["mode"] in [75, 63]:
                    typus = "Gambit"
                typ.append(typus)
                mode.append(self.manifest.ActivityTypeNames[datapoint["activityDetails"]["mode"]])

                key = str(datapoint["activityDetails"]["directorActivityHash"])
                key2 = str(datapoint["activityDetails"]["referenceId"])
                if key2 in self.manifest.ActivityNames:
                    directorActivity.append(self.manifest.ActivityNames[key2])
                elif key in self.manifest.ActivityNames:
                    directorActivity.append(self.manifest.ActivityNames[key])
                else:
                    directorActivity.append(key)

        df = pd.DataFrame({
            "type": typ,
            "mode": mode,
            "directorActivity": directorActivity,
        })

        df = df.groupby(["type", "mode", "directorActivity"]).size().reset_index(name='count')
        return df
    