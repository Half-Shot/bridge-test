from tornado.web import RequestHandler
import logging
logger = logging.getLogger(__name__)


class TUsersHandler(RequestHandler):
    def post(self, path):
        logger.warn("No handler for %s", path)

    def show(self):
        sn = self.get_query_argument("screen_name")
        if sn not in ["foobar"]:
            self.write({"error": {
                "code": 404,
                "message": "User not found",
                }
            })
            return 404
        new_user = TUsersHandler.dummy_user()
        new_user["protected"] = self.settings["test_state"].get("user.protected", False)
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
            "protected": False,
            "profile_image_url_https": "https://placeholdit.imgix.net/~text?txtsize=12&txt=128%C3%97128&w=128&h=128&txt=avatar",
        }

    def dummy_user_2():
        return {
            "id": 54321,
            "id_str": "54321",
            "name": "BarBaz",
            "screen_name": "barbaz",
            "description": "The bar to your baz",
            "url": "https://matrix.org",
            "protected": False,
            "profile_image_url_https": "https://placeholdit.imgix.net/~text?txtsize=12&txt=128%C3%97128&w=128&h=128&txt=changed",
        }
