
import dateutil.parser
import pandas as pd
from datetime import datetime

import plotly.express as px

from app.reports.ReportBase import Report


class LightLevelReport(Report):

    def save(self):
        super().save()

    def getName(self) -> str:
        return "chart_all_lightlevel"

    def __init__(self, membershipType, membershipId) -> None:
        super().__init__(membershipType, membershipId)

    def generate(self, data) -> Report:
        df = self.generateDataframe(data)
        # Filter results with zero or only one entry entry
        fig = px.line(df, x='Date', y="lightlevel",
                      title="Maximum Light level per week and day<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>",
                      color_discrete_sequence=px.colors.qualitative.Dark24,
                      color="timespan",
                      template="plotly_dark")
        fig.update_traces(hovertemplate="%{y}")
        fig.update_layout(hovermode="x unified")
        fig.update_yaxes(matches=None)
        fig.update_yaxes(showticklabels=True)
        fig.update_xaxes(matches='x')
        self.fig = fig
        return self

    def generateRawDataframe(self, data):
        starttime = []
        endtime = []
        lightlevel = []

        for datapoint in data:
            if "entries" not in datapoint: continue
            timestamp = dateutil.parser.parse(datapoint["period"]).timestamp()
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue
                starts = entry["values"]["startSeconds"]["basic"]["value"]
                ends = starts + entry["values"]["timePlayedSeconds"]["basic"]["value"]

                starttime.append(datetime.fromtimestamp(timestamp + starts).strftime("%Y-%m-%d %H:%M"))
                endtime.append(datetime.fromtimestamp(timestamp + ends).strftime("%Y-%m-%d %H:%M"))
                lightlevel.append(entry["player"]["lightLevel"])

        df = pd.DataFrame({
            "start": starttime,
            "end": endtime,
            "lightlevel": lightlevel,
        })
        return df

    def generateDataframe(self, data):
        df = self.generateRawDataframe(data)
        dataframes = []

        df['Date'] = pd.to_datetime(df['start'])  # - pd.to_timedelta(7, unit='d')
        df_day_max = df[df["lightlevel"] > 10]
        df_day_max = df_day_max.sort_values('Date').groupby([pd.Grouper(key='Date', freq='d')])["lightlevel"].max().reset_index().sort_values('Date').dropna()
        df_day_max["timespan"] = "day"
        dataframes.append(df_day_max)

        df['Date'] = pd.to_datetime(df['start']) - pd.to_timedelta(7, unit='d')
        df_week_max = df_day_max[df_day_max["lightlevel"] > 10]
        df_week_max = df_week_max.sort_values('Date').groupby([pd.Grouper(key='Date', freq='W-tue')])["lightlevel"].max().reset_index().sort_values('Date').dropna()
        df_week_max["timespan"] = "week"
        dataframes.append(df_week_max)

        df_combined = pd.concat(dataframes)

        return df_combined


