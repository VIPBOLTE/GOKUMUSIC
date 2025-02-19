from GOKUMUSIC.core.bot import GOKU
from GOKUMUSIC.core.dir import dirr
from GOKUMUSIC.core.git import git
from GOKUMUSIC.core.userbot import Userbot
from GOKUMUSIC.music import dbb, heroku

from .logging import LOGGER
EMOJIS = ["PPLAY_1", "PPLAY_2", "PPLAY_3", "PPLAY_4", "PPLAY_5",
          "PPLAY_6", "PPLAY_7", "PPLAY_8", "PPLAY_9", "PPLAY_10",
          "PPLAY_11", "PPLAY_12", "PPLAY_13", "PPLAY_14", "PPLAY_15",
          "PPLAY_16", "PPLAY_17"]

dirr()
git()
dbb()
heroku()

app = GOKU()
userbot = Userbot()


from Platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

HELPABLE = {}
