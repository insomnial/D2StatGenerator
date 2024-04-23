import dateutil.parser
import pandas as pd
from app.reports.ReportBase import Report
import plotly.express as px


class ActivityWinrateReport(Report):
    def save(self):
        super().save()

    def getName(self) -> str:
        return "[PVP] chart_tree - activity winrate; per mode and map"

    def __init__(self, membershipType, membershipId, displayName, manifest, video_type="gif") -> None:
        super().__init__(membershipType, membershipId, displayName, manifest)
        self.video_type = video_type

    def generate(self, data) -> Report:
        df = self.generateData(data)

        fig = px.treemap(
            df, path=[px.Constant("all"), "type", "mode", "directorActivity", "wintype"], values='count', template="plotly_dark",
            branchvalues="total", labels=["count"],
            title="PvP Winrate; per activity and map"
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
        wintype = []

        for datapoint in tqdm(data):
            if "entries" not in datapoint: continue
            timestamp = dateutil.parser.parse(datapoint["period"]).timestamp()
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue
                if datapoint["activityDetails"]["mode"] in [92, 91, 90, 89, 84, 81, 80, 74, 73, 72, 71, 68, 65, 62, 61, 60, 59, 50, 48, 43, 45, 44, 41, 42, 37, 38, 31, 25, 15]:
                    typus = "PvP"
                elif datapoint["activityDetails"]["mode"] in [75, 63]:
                    typus = "Gambit"
                else:
                    continue

                win = -1
                if "team" in entry["values"]:
                    team = [tm for tm in datapoint["teams"] if tm["teamId"] == int(entry["values"]["team"]["basic"]["value"])]
                    if len(team) > 0:
                        if team[0]["standing"]["basic"]["value"] == 1:
                            win = "loss"
                        else:
                            win = "win"

                if win == -1:
                    continue

                wintype.append(win)
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

        print("done")

        df = pd.DataFrame({
            "type": typ,
            "mode": mode,
            "directorActivity": directorActivity,
            "wintype": wintype,
        })

        df = df.groupby(["type", "mode", "directorActivity", "wintype"]).size().reset_index(name='count')
        return df
