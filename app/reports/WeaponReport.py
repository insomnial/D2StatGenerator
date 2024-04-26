import dateutil.parser
import pandas as pd
from datetime import datetime

from app.Director import Director
from app.data.activities import PVP_ACTIVITIES
import plotly.express as px

from app.reports.ReportBase import Report
from pretty_html_table import build_table


class WeaponReport(Report):

    def save(self):
        with open("%s/%s.html" % (Director.GetResultDirectory(self.displayName), "[ALL] table - weapons used per activity type"), "w") as f:
            f.write("This table shows every weapon you ever used - in any activity. "
                    "Sort order: Type > Weapon Name > Weapon ID > Kills."
                    "<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>")
            f.write(build_table(self.df, 'blue_light'))
        with open("%s/%s.csv" % (Director.GetResultDirectory(self.displayName), "[ALL] table - weapons used per activity type"), "w") as f:
            self.df.to_csv(f, index=False)

        super().save()

    def getName(self) -> str:
        return "[ALL] chart_bar - weapons used over time; per activity type "

    def __init__(self, membershipType, membershipId, displayName, manifest) -> None:
        super().__init__(membershipType, membershipId, displayName, manifest)
        self.df = None

    def generate(self, data) -> Report:
        self.df = self.generateListDataframe(data)
        df2 = self.generateChartDataframe(data)

        fig = px.bar(df2, x='Date', y="kills",
                     title="Weapon kills per Week, grouped by weapon type<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>",
                     color="type_name",
                     color_discrete_sequence=px.colors.qualitative.Light24,
                     template="plotly_dark",
                     facet_col="mode_name", facet_col_wrap=3, facet_row_spacing=0
                     )
        fig.update_traces(hovertemplate="%{y}")
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(matches=None)
        fig.update_yaxes(showticklabels=True)
        fig.update_xaxes(matches='x')

        self.fig = fig
        return self

    def generateRawDataframe(self, data):
        from tqdm import tqdm

        starttime = []
        endtime = []
        weapon = []
        name = []
        type_name = []
        bucket = []
        kills = []
        mode = []
        mode_name = []
        kills_precision = []

        for datapoint in tqdm(data, desc=self.getName()):
            if "entries" not in datapoint: continue
            timestamp = dateutil.parser.parse(datapoint["period"]).timestamp()
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue
                starts = entry["values"]["startSeconds"]["basic"]["value"]
                ends = starts + entry["values"]["timePlayedSeconds"]["basic"]["value"]
                if "weapons" not in entry["extended"]: continue
                for wp in entry["extended"]["weapons"]:
                    starttime.append(datetime.fromtimestamp(timestamp + starts).strftime("%Y-%m-%d %H:%M"))
                    endtime.append(datetime.fromtimestamp(timestamp + ends).strftime("%Y-%m-%d %H:%M"))
                    weapon.append(wp["referenceId"])
                    name.append(self.manifest.ItemDefinitions[str(wp["referenceId"])]["displayProperties"]["name"])
                    type_name.append(self.manifest.ItemDefinitions[str(wp["referenceId"])]["itemTypeDisplayName"])
                    bucket.append(self.manifest.ItemDefinitions[str(wp["referenceId"])]["inventory"]["bucketTypeHash"])

                    kills.append(1 * wp["values"]["uniqueWeaponKills"]["basic"]["value"])
                    kills_precision.append(1 * wp["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"])

                    mode.append(str(datapoint["activityDetails"]["mode"]))
                    mode_name.append(self.manifest.ActivityTypeNames[datapoint["activityDetails"]["mode"]])

        df = pd.DataFrame({
            "start": starttime,
            "end": endtime,
            "weapon": weapon,
            "name": name,
            "bucket": bucket,
            "type_name": type_name,
            "kills": kills,
            "mode": mode,
            "mode_name": mode_name,
            "kills_precision": kills_precision
        })
        df["is_pvp"] = df["mode"].astype("int32").isin(PVP_ACTIVITIES) * 1

        return df

    def generateChartDataframe(self, data):
        df = self.generateRawDataframe(data)

        df['Date'] = pd.to_datetime(df['start']) - pd.to_timedelta(7, unit='d')
        # dfx = df[df["bucket"] == 953998645] # heavy only
        df2 = df.groupby(['type_name', pd.Grouper(key='Date', freq='W-MON'), "mode", "mode_name"])['kills'] \
            .sum().reset_index().sort_values('type_name')

        df2 = df2[df2["mode"].isin(["2", "3", "4", "6", "37", "84", "48", "43", "82", "73", "63", "75"])]

        return df2

    def generateListDataframe(self, data):
        df = self.generateRawDataframe(data)

        dfy = df.groupby(["type_name", "weapon", "name", "mode_name"])[["kills", "kills_precision"]].sum() \
            .reset_index().sort_values(["type_name", "name", "weapon", "kills"])

        dfy["kills"] = dfy["kills"].astype("int32")
        dfy["kills_precision"] = dfy["kills_precision"].astype("int32")
        dfy["precision_ratio"] = (dfy["kills_precision"] / dfy["kills"]).round(2)

        return dfy
