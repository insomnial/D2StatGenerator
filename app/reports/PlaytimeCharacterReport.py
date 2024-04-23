import dateutil.parser
import pandas as pd
from datetime import datetime
import plotly.express as px
from app.reports.ReportBase import Report


class PlaytimeCharacterReport(Report):

    def save(self):
        super().save()

    def getName(self) -> str:
        return "[ALL] chart_area - playtime, split per character"

    def __init__(self, membershipType, membershipId, displayName, manifest) -> None:
        super().__init__(membershipType, membershipId, displayName, manifest)

    def generate(self, data) -> Report:
        df = self.generateDataframe(data)
        fig = px.area(df, x='Date', y="playtime",
                      title="Playtime per Character Class, in hours<br><sup>Generated by <a href='https://twitter.com/MijagoCoding/'>Mijago</a></sup>",
                      color_discrete_sequence=px.colors.qualitative.Dark24,
                      template="plotly_dark",
                      color="class", line_group="character",
                      color_discrete_map={
                          "Hunter": "#588689",
                          "Titan": "#A93E3C",
                          "Warlock": "#BAA046",
                      }
                      # facet_col="mode_name", facet_col_wrap=4,
                      # facet_col="mode_name",
                      # facet_col_wrap=3, facet_row_spacing=0,
                      )
        fig.update_traces(hovertemplate="%{y:.2f}h")
        fig.update_yaxes(matches=None)
        fig.update_yaxes(showticklabels=True)
        fig.update_xaxes(matches='x')
        self.fig = fig
        return self

    def generateRawDataframe(self, data):
        from tqdm import tqdm

        starttime_str = []
        starttime = []
        playtime = []
        clazz = []
        character = []

        for datapoint in tqdm(data):
            if "entries" not in datapoint: continue
            timestamp = dateutil.parser.parse(datapoint["period"]).timestamp()
            for entry in datapoint["entries"]:
                if entry["player"]["destinyUserInfo"]["membershipId"] != str(self.membershipId): continue
                if entry["player"]["classHash"] == 0: continue
                starts = entry["values"]["startSeconds"]["basic"]["value"]
                ends = starts + entry["values"]["timePlayedSeconds"]["basic"]["value"]

                strtime = datetime.fromtimestamp(timestamp + starts).strftime("%Y-%m-%d %H:00")
                starttime.append(pd.Timestamp(strtime))
                starttime_str.append(strtime)
                playtime.append(entry["values"]["timePlayedSeconds"]["basic"]["value"] / 60)
                if entry["player"]["classHash"] == 3655393761:
                    clazz.append("Titan")
                elif entry["player"]["classHash"] == 671679327:
                    clazz.append("Hunter")
                elif entry["player"]["classHash"] == 2271682572:
                    clazz.append("Warlock")
                character.append(entry["characterId"])

        df = pd.DataFrame({
            "start": starttime,
            "starttime_str": starttime_str,
            "playtime": playtime,
            "class": clazz,
            "character": character,
        })


        return df

    def generateDataframe(self, data):
        df = self.generateRawDataframe(data)
        df2 = df
        df2["Date"] = pd.to_datetime(df2['starttime_str']) - pd.to_timedelta(7, unit='d')
        df2 = df2.groupby(["class", "character", pd.Grouper(key='Date', freq='d')])["playtime"] \
            .sum().reset_index().sort_values('Date')

        lastDate = df2["Date"].tail(1).values[0]
        characterIds = df2["character"].unique()

        lastForChar = {k: 0 for k in characterIds}

        starttime_str = []
        starttime = []
        playtime = []
        clazz = []
        character = []

        for charId in characterIds:
            datax = df2[df2["character"] == charId]
            charClazz = datax.head(1)["class"].values[0]
            firstDate = datax.head(1)["Date"].values[0] + 0
            Dates = datax["Date"].unique()
            while firstDate < lastDate:
                if firstDate in Dates:
                    lastForChar[charId] += datax[datax["Date"] == firstDate]["playtime"].values[0]

                strtime = datetime.fromtimestamp(pd.Timestamp(firstDate).timestamp()).strftime("%Y-%m-%d %H:00")
                starttime.append(pd.Timestamp(strtime))
                starttime_str.append(strtime)
                playtime.append(lastForChar[charId])
                clazz.append(charClazz)
                character.append(charId)

                firstDate += 24 * 60 * 60 * 1000000000

        df2 = pd.DataFrame({
            "start": starttime,
            "starttime_str": starttime_str,
            "playtime": playtime,
            "class": clazz,
            "character": character,
        })

        df2["Date"] = pd.to_datetime(df2['starttime_str']) - pd.to_timedelta(7, unit='d')
        df2 = df2.groupby(["class", "character", pd.Grouper(key='Date', freq='d')])["playtime"] \
            .sum().reset_index().sort_values(["class", 'Date', "character", "playtime"])

        df2["playtime"] /= 60

        return df2
