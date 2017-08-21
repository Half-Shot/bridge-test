from .test import TwitterTest, TwitterTestGroup
from shutil import copyfile
from os import unlink
from os.path import join, exists
from time import sleep
from matrix_client.errors import MatrixRequestError
from bridgetest.twitter.proxy.handlers.users import TUsersHandler
import logging

logger = logging.getLogger(__name__)


class BotTestGroup(TwitterTestGroup):
    def __init__(self):
        TwitterTestGroup.__init__(self, "Bot")
        # self.addTest(ProfileTestUser())

    def before_each(self):
        TwitterTestGroup.before_each(self, "config.min", clearDB=True)
