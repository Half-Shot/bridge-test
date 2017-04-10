from tornado.web import RequestHandler
import logging
logger = logging.getLogger(__name__)


CONSUMERKEY = "CONSUMERKEYFOO"
CONSUMERSECRET = "CONSUMERSECRETBAR"
BEARERTOKEN = "ABCDEF"


def check_auth(auth):
    return True


class TOAuthHandler(RequestHandler):
    def post(self, path):
        if path == "token":
            self.set_status(self._token())
            return

    def _token(self):
        auth = self.request.headers.get("Authorization")
        if auth is None:
            return 400
        # Todo: Check this!
        auth = auth[6:]
        if check_auth(auth) is False:
            return 403
        self.write({
                "token_type": "bearer",
                "access_token": BEARERTOKEN
        })
        return 200

    def get(self):
        self.set_status(404)
