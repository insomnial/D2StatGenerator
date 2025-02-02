# What is this?
This downloads all your PGCRs (Post Game Carnage Report) from the Bungie.net api and builds some graphs.
If you find a bug when you run it locally, feel free to open an issue and I'll look at it - I don't really give support for this, though.
I'll add some more charts over time!

Make sure to post your cool charts on Twitter and to mention me on them! 
I'd love to see what all of you get to see! 
My Twitter: https://twitter.com/MijagoCoding/

# How to Use?
3) Install all required packages
   1) `python3 -m pip install pandas plotly pathos requests pretty_html_table bar-chart-race tqdm`
   2) If you want to use mp4 instead of gif, also install `python3 -m pip install python-ffmpeg` and put a [ffmpeg](https://www.ffmpeg.org/download.html) in your PATH variable. Then set the `VIDEO_TYPE` in `main.py` to `mp4`. 
   
      **I highly encourage you to do this, as the gifs tend to be 40mb in size, whereas the mp4 is only around 1.5mb~2mb**.
   
      Download it here: [ffmpeg](https://github.com/BtbN/FFmpeg-Builds/releases) (for Windows, `ffmpeg-n5.0-latest-win64-gpl-5.0.zip`).
4) Set your API key as an environemnt variable `BUNGIE_API_KEY`.  Get the key [here](https://www.bungie.net/en/Application).
   1) Alternatively: Add your api key to `main.py`. For this, edit `# API_KEY = "123456789"`.
5) Edit your user info in `main.py`. Alternatively, you can also use command line parameters to set this later.
   ```py
   MEMBERSHIP_MIJAGO = (3, 4611686018482684809)
   MEMBERSHIP_MYCOOLID = (1, 1231231231231233353) # for example, add this
   USED_MEMBERSHIP = MEMBERSHIP_MYCOOLID
   ```
6) Run the script `python3 main.py`.
   1) Complete Example: `BUNGIE_API_KEY=123456789012345   python3 main.py -p 3 -id 4611686018482684809`
   2) Alternatively you can also specify the platform and user: `python3 main.py -p 3 -id 4611686018482684809`
   3) This may take a while. I need 35~45 seconds for 1000 PGCRs with a download speed of 4.5mb/s.

# Where do I get my user ID?
1) Go to https://www.d2checklist.com (or any other similar page)
2) Search for your user, open your page
3) Look at the URL: `https://www.d2checklist.com/3/4611686018482684809/milestones`
   In this case, `3` is your MEMBERSHIP_TYPE and `4611686018482684809` is the MEMBERSHIP_ID, so you'll do something like `MEMBERSHIP_MIJAGO = (3, 4611686018482684809)`.


# Known Issues
- Sometimes the PGCR-Download is stuck. This is an issue with the threading library. Just restart the whole script. This is not a big issue as it continues where it stopped.

# Examples
These examples are from the early stage:

![img_4.png](examples/img_4.png)
![img_1.png](examples/img_1.png)
![img_2.png](examples/img_2.png)
![img_3.png](examples/img_3.png)
![fireteam.gif](examples/fireteam.gif)
![weapons.gif](examples/weapons.gif)
