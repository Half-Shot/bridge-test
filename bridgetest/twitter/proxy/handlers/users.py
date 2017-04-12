from tornado.web import RequestHandler
import logging
logger = logging.getLogger(__name__)


class TUsersHandler(RequestHandler):
    def post(self, path):
        logger.warn("No handler for %s", path)

    def show(self):
        sn = self.get_query_argument("screen_name")
        if sn not in ["foobar", "foobarprotect"]:
            self.write({"error": {
                "code": 404,
                "message": "User not found",
                }
            })
            return 404
        new_user = TUsersHandler.dummy_user()
        new_user["screen_name"] = sn
        new_user["protected"] = sn == "foobarprotect"
        self.write(new_user)
        return 200

    def get(self, path):
        if path == "show.json":
            self.set_status(self.show())
        else:
            logger.warn("No handler for %s", path)
            self.set_status(404)

    def dummy_user():
        return {
            "id": 12345,
            "id_str": "12345",
            "name": "FooBar",
            "screen_name": "foobar",
            "description": "The foo to your bar",
            "url": "https://matrix.org",
            "protected": "foobar",
            "profile_image_url_https": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/SMPTE_Color_Bars.svg/672px-SMPTE_Color_Bars.svg.png",
        }
