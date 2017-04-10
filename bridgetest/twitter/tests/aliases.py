from .test import TwitterTest, TwitterTestGroup
from shutil import copyfile
from os import unlink
from os.path import join, exists
from time import sleep
from matrix_client.errors import MatrixRequestError
import logging

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("tornado").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


class AliasesTestGroup(TwitterTestGroup):
    def __init__(self):
        TwitterTestGroup.__init__(self, "Aliases Test")
        self.addTest(AliasesTestBadTimeline())
        self.addTest(AliasesTestGoodTimeline())
        self.addTest(AliasesTestProtectedTimeline())

    def before_each(self):
        TwitterTestGroup.before_each(self, "config.min")


class AliasesTestBadTimeline(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "bad timeline name")

    def run(self):
        self.npm.start(
            self.state["root"],
            self.state["cmd"],
            noRead=True,
        )
        sleep(4)
        client = self.matrix.getClient()
        fail = None
        try:
            client.join_room("#_twitter_@abadsa-_4asdfasd<>ds:localhost")
        except MatrixRequestError as e:
            fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        assert fail is not None, "the room should not exist"
        assert fail.code == 404, "room should not be found. But got %s" % fail.content
        assert "M_NOT_FOUND" in fail.content, "room error should be M_NOT_FOUND, But got %s" % fail.content
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


class AliasesTestGoodTimeline(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "good timeline name")

    def run(self):
        self.npm.start(
            self.state["root"],
            self.state["cmd"],
            noRead=True,
        )
        sleep(4)
        client = self.matrix.getClient()
        fail = None
        room = None
        try:
            room = client.join_room("#_twitter_@foobar:localhost")

        except Exception as e:
            fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        client.listen_for_events()
        assert fail is None, "the room should exist, but got %s" % fail
        assert room.name is "[Twitter] FooBar", "room name is wrong, got '%s'" % room.name
        assert room.topic is "The foo to your bar | https://twitter.com/foobar`", "room topic is wrong, got '%s'" % room.topic
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


class AliasesTestProtectedTimeline(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "protected timeline name")

    def run(self):
        self.npm.start(
            self.state["root"],
            self.state["cmd"],
            noRead=True,
        )
        sleep(4)
        client = self.matrix.getClient()
        fail = None
        try:
            client.join_room("#_twitter_@foobarprotect:localhost")
        except MatrixRequestError as e:
            fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        log = self.getLog()
        assert fail is not None, "the room should not exist"
        assert fail.code == 404, "room should not be found. But got %s" % fail.content
        assert "M_NOT_FOUND" in fail.content, "room error should be M_NOT_FOUND, But got %s" % fail.content
        assert "User is protected, can't create timeline." in log
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)
