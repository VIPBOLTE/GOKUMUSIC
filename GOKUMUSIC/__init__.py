import json
import os
import config
import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from GOKUMUSIC.core.bot import GOKUBOT
from GOKUMUSIC.core.dir import dirr
from GOKUMUSIC.core.git import git
from GOKUMUSIC.core.userbot import Userbot
from GOKUMUSIC.misc import dbb, heroku, sudo

from .logging import LOGGER

#time zone
TIME_ZONE = pytz.timezone(config.TIME_ZONE)
scheduler = AsyncIOScheduler(timezone=TIME_ZONE)

dirr()

git()

dbb()

heroku()

sudo()

app = GOKUBOT()

userbot = Userbot()

from .platforms import PlaTForms

Platform = PlaTForms()
HELPABLE = {}
