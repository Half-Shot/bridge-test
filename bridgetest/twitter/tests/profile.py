from .test import TwitterTest, TwitterTestGroup
from shutil import copyfile
from os import unlink
from os.path import join, exists
from time import sleep
from matrix_client.errors import MatrixRequestError
from bridgetest.twitter.proxy.handlers.users import TUsersHandler
import logging

logger = logging.getLogger(__name__)


class ProfileTestGroup(TwitterTestGroup):
    def __init__(self):
        TwitterTestGroup.__init__(self, "Profile")
        self.addTest(ProfileTestUser())

    def before_each(self):
        TwitterTestGroup.before_each(self, "config.min", clearDB=True)


# Is twitter profile ok
class ProfileTestUser(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "User Profile")

    def run(self):
        self.npm.start(
            self.state["root"],
            self.state["cmd"],
            noRead=True,
        )
        sleep(4)
        client = self.matrix.getClient()
        user = None
        dummy = TUsersHandler.dummy_user()
        client.join_room("#_twitter_@foobar:localhost")
        retries = 0
        while retries < 5:
            try:
                user = self.matrix.getUser("@_twitter_%s:localhost" % dummy["id"])
                retries = 5
            except MatrixRequestError as e:
                if e.code != 404:
                    raise e
                logger.info("User was not found, retrying (%d/5)" % retries)
                retries += 1
                sleep(1)
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        dn = user.get_display_name()
        assert dn == "%s (@%s)" % (dummy["name"], dummy["screen_name"]), "display name is wrong, got %s" % dn
        avatar = user.get_avatar_url()
        assert avatar is not None, "avatar url was not set"
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


 # Name
 # Avatar should be set
# Is the custom display name correct
