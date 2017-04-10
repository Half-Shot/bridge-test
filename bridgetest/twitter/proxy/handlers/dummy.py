from tornado.web import RequestHandler
import logging
logger = logging.getLogger(__name__)


class TDummyHandler(RequestHandler):
    def post(self, path):
        logger.warn("No handler for %s", path)
        self.set_status(404)

    def get(self, path):
        logger.warn("No handler for %s", path)
        self.set_status(404)
