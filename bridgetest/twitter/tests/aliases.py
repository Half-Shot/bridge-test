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
        sleep(10)
        client = self.matrix.getClient()
        fail = None
        try:
            client.join_room("#twitter_@$QW$$QRWQ£:localhost")
        except MatrixRequestError as e:
            fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=5)
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
        sleep(5)
        client = self.matrix.getClient()
        room = client.join_room("#twitter_@foobar:localhost")
        print(room)
        timedOut, returnCode, output = self.npm.stop_process(kill_after=5)
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)
