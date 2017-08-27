from .test import TwitterTest, TwitterTestGroup
from time import sleep
from matrix_client.errors import MatrixRequestError
import logging

logger = logging.getLogger(__name__)


class AliasesTestGroup(TwitterTestGroup):
    def __init__(self):
        TwitterTestGroup.__init__(self, "Aliases")
        self.addTest(AliasesTestBadTimeline())
        self.addTest(AliasesTestGoodTimeline())
        self.addTest(AliasesTestProtectedTimeline())
        self.addTest(AliasesTestGoodHashtag())
        self.addTest(AliasesTestBadHashtag())

    def before_each(self):
        TwitterTestGroup.before_each(self, "config.min", clearDB=True)


class AliasTest(TwitterTest):
    def __init__(self, name):
        TwitterTest.__init__(self, name)
        self.npm.start(
            self.state["root"],
            self.state["cmd"],
            noRead=True,
        )
        sleep(self.state["bridge_startup_wait"])
        self.client = self.matrix.getClient()
        self.fail = None


class AliasesTestBadTimeline(AliasTest):
    def __init__(self):
        AliasTest.__init__(self, "bad timeline screen name")

    def run(self):
        AliasTest.__init__(self)
        try:
            self.client.join_room("#_twitter_@abadsa-_4asdfasd<>ds:localhost")
        except MatrixRequestError as e:
            self.fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        assert self.fail is not None, "the room should not exist"
        assert self.fail.code == 404, "room should not be found. But got %s" % self.fail.content
        assert "M_NOT_FOUND" in self.fail.content, "room error should be M_NOT_FOUND, But got %s" % self.fail.content
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


class AliasesTestGoodTimeline(AliasTest):
    def __init__(self):
        AliasTest.__init__(self, "good timeline screen name")

    def run(self):
        AliasTest.__init__(self)
        room = None
        try:
            room = self.client.join_room("#_twitter_@foobar:localhost")
        except Exception as e:
            self.fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        self.client.listen_for_events()
        assert self.fail is None, "the room should exist, but got %s" % self.fail
        events = room.get_events()
        self.add_var("events", room.get_events())
        name = next((ev["content"]["name"] for ev in events if ev["type"] == "m.room.name"), None)
        self.add_var("name", name)
        assert name == "[Twitter] FooBar", "name is wrong, got '%s'" % name
        topic = next((ev["content"]["topic"] for ev in events if ev["type"] == "m.room.topic"), None)
        self.add_var("topic", topic)
        assert topic == "The foo to your bar | https://twitter.com/foobar", "topic is wrong, got '%s'" % topic
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


class AliasesTestProtectedTimeline(AliasTest):
    def __init__(self):
        AliasTest.__init__(self, "protected timeline")

    def before_test(self):
        self.state["proxy_state"] = {"user.protected": True}
        super().before_test()

    def run(self):
        AliasTest.__init__(self)
        try:
            self.client.join_room("#_twitter_@foobar:localhost")
        except MatrixRequestError as e:
            self.fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        log = self.getLog()
        assert self.fail is not None, "the room should not exist"
        assert self.fail.code == 404, "room should not be found. But got %s" % self.fail.content
        assert "M_NOT_FOUND" in self.fail.content, "room error should be M_NOT_FOUND, But got %s" % self.fail.content
        assert "User is protected, can't create timeline." in log
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


class AliasesTestBadHashtag(AliasTest):
    def __init__(self):
        AliasTest.__init__(self, "bad hashtag")

    def run(self):
        AliasTest.__init__(self)
        try:
            self.client.join_room("#_twitter_#foo bar:localhost")
        except MatrixRequestError as e:
            self.fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        assert self.fail is not None, "the room should not exist"
        assert self.fail.code == 404, "room should not be found. But got %s" % self.fail.content
        assert "M_NOT_FOUND" in self.fail.content, "room error should be M_NOT_FOUND, But got %s" % self.fail.content
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)


class AliasesTestGoodHashtag(AliasTest):
    def __init__(self):
        AliasTest.__init__(self, "good hashtag")

    def run(self):
        AliasTest.__init__(self)
        room = None
        try:
            room = self.client.join_room("#_twitter_#foobar:localhost")

        except Exception as e:
            self.fail = e
        timedOut, returnCode, output = self.npm.stop_process(kill_after=1)
        self.client.listen_for_events()
        events = room.get_events()
        assert self.fail is None, "the room should exist, but got %s" % self.fail
        self.add_var("events", events)
        name = next((ev["content"]["name"] for ev in events if ev["type"] == "m.room.name"), None)
        self.add_var("name", name)
        assert name == "[Twitter] #foobar", "name is wrong, got '%s'" % name
        topic = next((ev["content"]["topic"] for ev in events if ev["type"] == "m.room.topic"), None)
        self.add_var("topic", topic)
        assert topic == "Twitter feed for #foobar", "topic is wrong, got '%s'" % topic
        self.state["output"] = output
        self._assert_startup(timedOut, returnCode)
