import pandas as pd
from app.Director import Director
from app.reports.ReportBase import Report
import bar_chart_race as bcr
from dateutil import parser


class ActivityTypeRaceReport(Report):
    def save(self):
        super().save()

    def getName(self) -> str:
        return "[ALL] race - activity type playtime"

    def __init__(self, membershipType, membershipId, manifest, video_type="gif") -> None:
        super().__init__(membershipType, membershipId, manifest)
        self.video_type = video_type

    def save(self):
        pass

    def generate(self, data):
        df = self.generateData(data)
        bcr.bar_chart_race(
            df=df,
            filename=Director.GetResultDirectory(self.membershipType, self.membershipId) + "/"
                     + "[ALL] race - activity type playtime." + self.video_type,
            orientation='h',
            sort='desc',
            n_bars=20,
            fixed_order=False,
            fixed_max=True,
            steps_per_period=10,
            period_length=200,
            interpolate_period=False,
            perpendicular_bar_func='median',
            title="Top 20 activities played over time, numbers represent hours\nGenerated by Mijago's PgcrReport Generator",
            period_summary_func=lambda v, r: {'x': .98, 'y': .2,
                                              's': f'Total hours: {v.sum():,.0f}',
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
        return self

    def generateData(self, datap):  # pve, pvp, gambit
        from tqdm import tqdm
        import warnings
        warnings.simplefilter("ignore")

        eps = []

        for data in tqdm(datap):
            if "entries" not in data: continue
            date = parser.parse(data["period"])
            # find own user entry
            entry = [e for e in data["entries"] if e["player"]["destinyUserInfo"]["membershipId"] == str(self.membershipId)][0]
            if "weapons" not in entry["extended"]: continue
            eps.append(
                (
                    date,
                    self.manifest.ActivityTypeNames[data["activityDetails"]["mode"]],
                    entry["values"]["activityDurationSeconds"]["basic"]["value"] / 60 / 60
                )
            )

        df = pd.DataFrame(eps, columns=["date", "name", "hours"])
        df2 = df.groupby([df.date.dt.to_period('W'), "name"]).sum(numeric_only=True).reset_index()
        df2["cumsum"] = df2.groupby(["name"]).cumsum(numeric_only=True)
        df3 = df2.pivot(index="date", columns="name", values="cumsum")

        df3 = df3.fillna(method='ffill')
        return df3
