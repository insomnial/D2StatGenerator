from app.Director import Director
from app.bungiemanifest import DestinyManifest
from app.PgcrCollector import PGCRCollector
from app.Zipper import Zipper
from app.bungieapi import BungieApi
from app.reports.ActivityCountReport import ActivityCountReport
from app.reports.ActivityLocationTimeReport import ActivityLocationTimeReport
from app.reports.ActivityLocationWeaponReport import ActivityLocationWeaponReport
from app.reports.ActivityTypeRaceReport import ActivityTypeRaceReport
from app.reports.ActivityWinrateReport import ActivityWinrateReport
from app.reports.FireteamActivityReport import FireteamActivityReport
from app.reports.FireteamRace import FireteamRaceReport
from app.reports.KDReport import KDReport
from app.reports.KillsDeathsAssistsReport import KillsDeathsAssistsReport
from app.reports.LightLevelReport import LightLevelReport
from app.reports.PlaytimeCharacterReport import PlaytimeCharacterReport
from app.reports.PlaytimeReport import PlaytimeReport
from app.reports.WeaponKillTreeReport import WeaponKillTreeReport
from app.reports.WeaponRaceReport import WeaponRaceReport
from app.reports.WeaponReport import WeaponReport
from app.reports.WeekdayReport import WeekdayReport

###############################################################################
#
# main()
#
###############################################################################
if __name__ == '__main__':
    import pathos, argparse, os

    # build argument parsing
    descriptionString = """Get and compile stats for a Destiny 2 user.
    example: main.py -p 3 -id 4611686018482684809"""
    platformString = """    Xbox     1
    Psn      2
    Steam    3
    Blizzard 4
    Stadia   5
    Egs      6"""
    parser = argparse.ArgumentParser(prog='main.py', description=f'{descriptionString}', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--platform', '-p', type=int, required=False, help=f'{platformString}')
    parser.add_argument('--membership_id', '-id', type=int, required=False, help='Bungie ID')
    args = vars(parser.parse_args())
    platform = args['platform']
    id = args['membership_id']

    if platform != None and id != None:
        USED_MEMBERSHIP = (platform, id)
    else:
        MIJAGO = (3, 4611686018482684809)
        # You can easily set your own ID here:
        MYCOOLID = (3, 1234567890123456789)
        USED_MEMBERSHIP = MIJAGO

    from pathos.multiprocessing import ProcessPool, ThreadPool, ThreadingPool
    pathos.helpers.freeze_support()  # required for windows
    pool = ProcessPool()
    # You could also specify the amount of threads. Note that this DRASTICALLY speeds up the process but takes serious computation power.
    # pool = ProcessPool(40)

    # check manifest
    manifest = DestinyManifest().update()

    # You can also set an api key manually, if you do not want to use environment variables.
    API_KEY = os.getenv('BUNGIE_API_KEY')
    # API_KEY = "123456789"
    
    api = BungieApi(API_KEY)
    # "gif by default, "mp4" if you installed ffmpeg which you should; see README.d
    VIDEO_TYPE = "mp4"

    Director.CreateDirectoriesForUser(*USED_MEMBERSHIP)
    Director.ClearResultDirectory(*USED_MEMBERSHIP)
    Director.CreateDirectoriesForUser(*USED_MEMBERSHIP)
    pc = PGCRCollector(*USED_MEMBERSHIP, api, pool)
    pc.getCharacters().getActivities(limit=None).getPGCRs()  # .combineAllPgcrs()
    data = pc.getAllPgcrs()

    pool.close()

    reports = [
        ActivityCountReport(*USED_MEMBERSHIP, manifest),
        ActivityLocationTimeReport(*USED_MEMBERSHIP, manifest),
        ActivityLocationWeaponReport(*USED_MEMBERSHIP, manifest),
        ActivityTypeRaceReport(*USED_MEMBERSHIP, manifest, video_type=VIDEO_TYPE),
        ActivityWinrateReport(*USED_MEMBERSHIP, manifest),
        FireteamActivityReport(*USED_MEMBERSHIP, manifest),
        FireteamRaceReport(*USED_MEMBERSHIP, manifest, video_type=VIDEO_TYPE),
        KDReport(*USED_MEMBERSHIP, manifest),
        KillsDeathsAssistsReport(*USED_MEMBERSHIP, manifest),
        LightLevelReport(*USED_MEMBERSHIP, manifest),
        PlaytimeCharacterReport(*USED_MEMBERSHIP, manifest),
        PlaytimeReport(*USED_MEMBERSHIP, manifest),
        WeaponKillTreeReport(*USED_MEMBERSHIP, manifest),
        WeaponRaceReport(*USED_MEMBERSHIP, manifest, video_type=VIDEO_TYPE),
        WeaponReport(*USED_MEMBERSHIP, manifest),
        WeekdayReport(*USED_MEMBERSHIP, manifest)
    ]
    for report in reports:
        report.generate(data).save()

    Zipper.zip_directory(Director.GetResultDirectory(*USED_MEMBERSHIP), Director.GetZipPath(*USED_MEMBERSHIP))
    print("Generated ZIP:", Director.GetZipPath(*USED_MEMBERSHIP))
