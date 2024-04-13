import dateutil.parser
import pandas as pd
from datetime import datetime
import plotly.express as px

from app.reports.ReportBase import Report


class KDReport(Report):

    def save(self):
        super().save()

    def getName(self) -> str:
        return "[PVP] chart_line - kd and kda ratio"

    def __init__(self, membershipType, membershipId, manifest) -> None:
        super().__init__(membershipType, membershipId, manifest)

    def generate(self, data) -> Report:
        df = self.generateDataframe(data)
        # Filter results with zero or only one entry entry
        df3 = df[["Date", "mode_name", "kd", "eff"]].melt(id_vars=["Date", "mode_name"], var_name="stat")

        fig = px.line(df3, x='Date', y="value",
                      title="KD and Efficiency per week, grouped by activity<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>",
                      color="stat",
                      color_discrete_sequence=px.colors.qualitative.Dark24,
                      template="plotly_dark",
                      facet_col="mode_name",
                      facet_col_wrap=3, facet_row_spacing=0,
                      )
        fig.update_traces(hovertemplate="%{y:.2f}")
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(matches=None)
        fig.update_yaxes(showticklabels=True)
        fig.update_xaxes(matches='x')
        self.fig = fig
        return self

    def generateRawDataframe(self, data):
        starttime = []
        starttime_str = []
        endtime_str = []
        mode = []
        mode_name = []
        opponentsDefeated = []
        assists = []
        deaths = []
        kills = []

        for datapoint in data:
            if "entries" not in datapoint: continue
            timestamp = dateutil.parser.parse(datapoint["period"]).timestamp()
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue

                starts = entry["values"]["startSeconds"]["basic"]["value"]
                ends = starts + entry["values"]["timePlayedSeconds"]["basic"]["value"]

                starttime.append(datetime.fromtimestamp(timestamp + starts).strftime("%Y-%m-%d %H:%M"))
                starttime_str.append(datetime.fromtimestamp(timestamp + starts).strftime("%Y-%m-%d %H:%M"))
                endtime_str.append(datetime.fromtimestamp(timestamp + ends).strftime("%Y-%m-%d %H:%M"))
                assists.append(entry["values"]["assists"]["basic"]["value"])
                deaths.append(entry["values"]["deaths"]["basic"]["value"])
                kills.append(entry["values"]["kills"]["basic"]["value"])
                opponentsDefeated.append(entry["values"]["opponentsDefeated"]["basic"]["value"])

                mode.append(datapoint["activityDetails"]["mode"])
                mode_name.append(self.manifest.ActivityTypeNames[datapoint["activityDetails"]["mode"]])

        df = pd.DataFrame({
            "start": starttime,
            "starttime_str": starttime_str,
            "endtime_str": endtime_str,
            "mode": mode,
            "mode_name": mode_name,
            "opponentsDefeated": opponentsDefeated,
            "kills": kills,
            "deaths": deaths,
            "assists": assists,
        })
        df["is_pvp"] = df["mode"].astype("int32").isin([91, 90, 89, 84, 81, 80, 74, 73, 72, 71, 68, 65, 62, 61, 60, 59, 50, 48, 43, 45, 44, 41, 42, 37, 38, 31, 25, 15]) * 1

        return df

    def generateDataframe(self, data):
        df = self.generateRawDataframe(data)

        df['Date'] = pd.to_datetime(df['start']) - pd.to_timedelta(7, unit='d')
        df = df[df["is_pvp"] == 1]
        # dfx = df[df["bucket"] == 953998645] # heavy only
        df = df.groupby(['mode', "mode_name", pd.Grouper(key='Date', freq='W-TUE')])[['kills', "deaths", "assists"]] \
            .sum().reset_index().sort_values('Date')

        df["kills_cul"] = df.groupby(["mode"])["kills"].cumsum()
        df["deaths_cul"] = df.groupby(["mode"])["deaths"].cumsum()
        df["assists_cul"] = df.groupby(["mode"])["assists"].cumsum()
        df["kd"] = df["kills_cul"] / df["deaths_cul"]
        df["eff"] = (df["kills_cul"] + df["assists_cul"] / 2) / df["deaths_cul"]

        return df
