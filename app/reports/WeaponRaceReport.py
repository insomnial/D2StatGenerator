import pandas as pd

from app.Director import Director
from app.reports.ReportBase import Report
import bar_chart_race as bcr
from dateutil import parser


class WeaponRaceReport(Report):
    def save(self):
        super().save()

    def getName(self) -> str:
        return "[ALL] race - weapon usage"

    def __init__(self, membershipType, membershipId, manifest, video_type="gif") -> None:
        super().__init__(membershipType, membershipId, manifest)
        self.video_type = video_type

    def save(self):
        pass

    def generate(self, data) -> Report:
        self.generateintern(data, "pve")
        self.generateintern(data, "pvp")

        return self

    def generateintern(self, data, type):
        df = self.generateData(data, type)
        bcr.bar_chart_race(
            df=df,
            filename=Director.GetResultDirectory(self.membershipType, self.membershipId) + "/"
                     + "[" + type.upper() + "] race - weapon usage." + self.video_type,
            orientation='h',
            sort='desc',
            n_bars=20,
            fixed_order=False,
            fixed_max=True,
            steps_per_period=10,
            period_length=200,
            interpolate_period=False,
            perpendicular_bar_func='median',
            title="Top 20 weapons used in " + type + " over time, numbers represent kills\nGenerated by Mijago's PgcrReport Generator",
            period_summary_func=lambda v, r: {'x': .98, 'y': .2,
                                              's': f'Total Kills: {v.sum():,.0f}',
                                              'ha': 'right', 'size': 11},
            bar_size=.90,
            shared_fontdict=None,
            scale='linear',
            fig=None,
            writer=None,
            bar_kwargs={'alpha': .7},
            filter_column_colors=True,
            cmap="dark24",
        )

    def generateData(self, datap, typ="pve"):  # pve, pvp, gambit
        eps = []

        for data in datap:
            if "entries" not in data: continue
            date = parser.parse(data["period"])
            # find own user entry
            entry = [e for e in data["entries"] if e["player"]["destinyUserInfo"]["membershipId"] == str(self.membershipId)][0]
            if "weapons" not in entry["extended"]: continue

            typus = "pve"
            if data["activityDetails"]["mode"] in [91, 90, 84, 81, 80, 74, 73, 72, 71, 68, 65, 62, 61, 60, 59, 50, 48, 32, 43, 45, 44, 41, 42, 37, 38, 31, 25, 15]:
                typus = "pvp"
            #elif data["activityDetails"]["mode"] in [75, 63]: #    typus = "gambit"
            if typus != typ:
                continue

            for wp in entry["extended"]["weapons"]:
                precision = 1 * wp["values"]["uniqueWeaponPrecisionKills"]["basic"]["value"]
                normal = 1 * wp["values"]["uniqueWeaponKills"]["basic"]["value"] - precision
                for idx, value in enumerate([normal, precision]):
                    eps.append(
                        (
                            date,
                            self.manifest.ItemDefinitions[str(wp["referenceId"])]["displayProperties"]["name"],
                            value
                        )
                    )

        df = pd.DataFrame(eps, columns=["date", "name", "kills"])
        df2 = df.groupby([df.date.dt.to_period('W'), "name"]).sum().reset_index()
        df2["cumsum"] = df2.groupby(["name"]).cumsum()
        df3 = df2.pivot(index="date", columns="name", values="cumsum")

        df3 = df3.fillna(method='ffill')
        return df3
