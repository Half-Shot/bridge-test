from bridgetest.common import Test, TestGroup
from shutil import copyfile
from os import unlink
from os.path import join, exists
import logging
import contextlib

logger = logging.getLogger(__name__)


class TwitterTestGroup(TestGroup):
    def __init__(self, name):
        TestGroup.__init__(self, name)

    def before_test(self):
        logger.debug("before_test (%s)", self.name)
        root = self.state["git"].get_copy(
            self.state["repo"],
            self.state["branch"]
        )
        new_config = join(root, "config.yaml")
        new_reg = join(root, "twitter-registration.yaml")
        self.set_state({
            "root": root,
            "config_path": new_config,
            "registration_path": new_reg,
            "room_store_path": join(root, "room-store.db"),
            "user_store_path": join(root, "user-store.db"),
            "bearer_path": join(root, "bearer.tok"),
            "log_path": join(root, "bridge.log"),
            "db_path": join(root, "twitter.db"),
        })

    def after_test(self):
        logger.debug("after_test (%s)", self.name)
        self.state["git"].delete(
            self.state["repo"],
            self.state["branch"],
            True
        )

    def before_each(self, cfgFile, clearDB=False):
        logger.debug("before_each (%s) -> copying files", self.name)
        try:
            copyfile(self.state[cfgFile], self.state["config_path"])
            copyfile(self.state["registration"], self.state["registration_path"])
        except FileNotFoundError as e:
            logger.error("Couldn't create config file because the source does not exist")
            raise Exception("Fatal problem in before_each.", e)


    def after_each(self):
        logger.debug("after_each (%s) -> deleting files", self.name)
        for f in [
            self.state["config_path"],
            self.state["registration_path"],
            self.state["log_path"]
                ]:
            try:
                unlink(f)
            except FileNotFoundError as e:
                logger.debug("Couldn't delete %s because it doesn't exist", f)


class TwitterTest(Test):
    def __init__(self, name):
        Test.__init__(self, name)

    def set_state(self, new_state):
        super().set_state(new_state)
        if "npm" in self.state:
            self.npm = self.state["npm"]
        if "git" in self.state:
            self.git = self.state["git"]
        if "matrix" in self.state:
            self.matrix = self.state["matrix"]

    def clear_data(self):
        with contextlib.suppress(FileNotFoundError):
            unlink(self.state["room_store_path"])
            unlink(self.state["user_store_path"])
            unlink(self.state["db_path"])

    def _assert_startup(self, timedOut, returnCode):
        log = self.getLog()
        assert log is not None, "log file not found."
        assert timedOut, "should not exit premuturely"
        assert "Existing token OK" in log, "should use old token."
        assert exists(self.state["db_path"]), "database should exist"
        assert exists(self.state["bearer_path"]), "bearer token should exist"
        assert log.find("Created user 'twitbot'")

    def after_test(self):
        self.npm.stop_process() # Make sure the process has exited
