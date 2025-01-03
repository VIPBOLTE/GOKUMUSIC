from config import OWNER_ID
from GOKUMUSIC.misc import SUDOERS
from GOKUMUSIC.utils.welcome.support_db import SUPPORTS


async def load_support_users():
    support = SUPPORTS()
    for i in OWNER_ID:
        support.insert_support_user(int(i),"dev")
    for i in SUDOERS:
        support.insert_support_user(int(i),"sudo")
    return

def get_support_staff(want = "all"):
    """
    dev, sudo, whitelist, dev_level, sudo_level, all
    """
    support = SUPPORTS()
    devs = support.get_particular_support("dev")
    sudo = support.get_particular_support("sudo")

    if want in ["dev","dev_level"]:
        wanted = devs
    elif want == "sudo":
        wanted = sudo
    elif want == "sudo_level":
        wanted = sudo + devs
    else:
        wanted = list(set([int(OWNER_ID)] + devs + sudo))

    return wanted
