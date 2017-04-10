from .test import TwitterTest, TwitterTestGroup
from os import unlink
from os.path import exists
import logging

logger = logging.getLogger(__name__)


class StartBridgeTestGroup(TwitterTestGroup):
    def __init__(self):
        TwitterTestGroup.__init__(self, "Start Bridge")
        self.addTest(StartBridgeMissingFiles())
        self.addTest(StartBridgeCold())
        self.addTest(StartBridgePrevious())

    def before_each(self):
        TwitterTestGroup.before_each(self, "config.min")


class StartBridgeMissingFiles(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "without config files")

    def run(self):
        unlink(self.state["config_path"])
        unlink(self.state["registration_path"])
        timedOut, returnCode, output = self.npm.start(self.state["root"], self.state["cmd"], 5)
        assert timedOut is False, "should close early"
        assert returnCode is 1, "should not exit cleanly"
        assert exists(self.state["db_path"]) is False, "database shouldn't exist"
        assert exists(self.state["bearer_path"]) is False, "bearer token shouldn't exist"


class StartBridgeCold(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "from clean")

    def run(self):
        timedOut, returnCode, output = self.npm.start(
            self.state["root"],
            self.state["cmd"],
            5
        )
        self.state["output"] = output

        log = self.getLog()
        assert log is not None, "log file not found."
        assert timedOut, "should not exit premuturely"
        assert "Token file not found or unreadable. Requesting new token." in log, "should request new token"
        assert "Existing token OK" in log, "token should verify okay."
        assert exists(self.state["db_path"]), "database should exist"
        assert exists(self.state["bearer_path"]), "bearer token should exist"
        assert log.find("Created user 'twitbot'")


class StartBridgePrevious(TwitterTest):
    def __init__(self):
        TwitterTest.__init__(self, "from previous state")

    def run(self):
        timedOut, returnCode, output = self.npm.start(self.state["root"], self.state["cmd"], 5)
        self.state["output"] = output

        log = self.getLog()
        assert log is not None, "log file not found."
        assert timedOut, "should not exit premuturely"
        assert "Token file not found or unreadable. Requesting new token." not in log, "should not request new token"
        assert "Existing token OK" in log, "should use old token."
        assert exists(self.state["db_path"]), "database should exist"
        assert exists(self.state["bearer_path"]), "bearer token should exist"
