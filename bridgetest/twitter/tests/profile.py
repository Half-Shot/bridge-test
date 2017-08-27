from .test import TwitterTest, TwitterTestGroup
from shutil import copyfile
from os import unlink
from os.path import join, exists
from time import sleep
from matrix_client.errors import MatrixRequestError
from bridgetest.twitter.proxy.handlers.users import TUsersHandler
from shutil import copyfile
import logging

logger = logging.getLogger(__name__)


class ProfileTestGroup(TwitterTestGroup):
    def __init__(self):
        TwitterTestGroup.__init__(self, "Profile")
        self.addTest(ProfileTestUser())
        self.addTest(ProfileChangeTest())
        self.addTest(ProfileCustomName())

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
        assert user.get_avatar_url() is not None, "avatar url was not set"
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


# Is twitter profile ok
class ProfileCustomName(TwitterTest):
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
        assert dn == "%s foobar (@%s)" % (dummy["name"], dummy["screen_name"]), "display name is wrong, got %s" % dn
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


# Is twitter profile ok
class ProfileChangeTest(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "User Profile Change")

    def before_test(self):
        unlink(self.state["config_path"])
        copyfile(self.state["config.profile.displayname"], self.state["config_path"])
        self.state["proxy_state"] = {"timeline.profilechange": True}
        super().before_test()

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
        dummy2 = TUsersHandler.dummy_user_2()
        oldName = "%s (@%s)" % (dummy["name"], dummy["screen_name"])
        newName = "%s (@%s)" % (dummy2["name"], dummy2["screen_name"])
        room = client.join_room("#_twitter_@foobar:localhost")
        print(room)
        retries = 0
        while retries < 5:
            try:
                user = self.matrix.getUser("@_twitter_%s:localhost" % dummy["id"])
            except MatrixRequestError as e:
                if e.code != 404:
                    raise e
                logger.info("User was not found, retrying (%d/5)" % retries)
            if user:
                if user.get_display_name() != oldName:
                    break
            retries += 1
            sleep(1)
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        dn = user.get_display_name()
        assert user.get_display_name() == newName, "display name is wrong, got '%s'" % dn
        assert user.get_avatar_url() is not None, "avatar url was not set"
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)