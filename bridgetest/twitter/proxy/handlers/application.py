from tornado.web import RequestHandler
import logging
logger = logging.getLogger(__name__)


class TApplicationHandler(RequestHandler):
    # def post(self):
    #     print(self.request)

    def get(self, path):
        if path == "rate_limit_status.json":
            # TODO: Return more info.
            self.set_status(200)
