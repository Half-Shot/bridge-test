import tornado.ioloop
from tornado.web import RequestHandler, Application
import logging
from threading import Thread
import bridgetest.twitter.proxy.handlers as handlers

logger = logging.getLogger(__name__)

CONSUMERKEY = "CONSUMERKEYFOO"
CONSUMERSECRET = "CONSUMERSECRETBAR"
BEARERTOKEN = "ABCDEF"
API_URL = "https://api.twitter.com/1.1/"


class TwitterProxy(Thread):
    def __init__(self):
        super(TwitterProxy, self).__init__()
        self.name = "TwitterProxy"
        self.app = None

    def run(self):
        tornado.ioloop.IOLoop.current().start()

    def stop(self):
        if self.isAlive():
            tornado.ioloop.IOLoop.current().stop()
            self.join()

    def start(self, port=8086):
        self.app = Application([
            (r"https://api.twitter.com/oauth2/(.*)", handlers.TOAuthHandler),
            (API_URL + "application/(.*)", handlers.TApplicationHandler),
            (API_URL + "users/(.*)", handlers.TUsersHandler),
            (API_URL + "statuses/(.*)", handlers.TStatusHandler),
            (r"https://api.twitter.com/(.*)", handlers.TDummyHandler),
        ])
        logger.info("Started listening on twitter proxy.")
        self.app.listen(port)
        super(TwitterProxy, self).start()

    def apply_state(self, test_state):
        logger.debug("Applying proxy state to proxy.")
        self.app.settings["test_state"] = test_state
