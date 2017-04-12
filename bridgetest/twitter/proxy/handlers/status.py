from tornado.web import RequestHandler
from .users import TUsersHandler
import logging
from json import dumps
logger = logging.getLogger(__name__)


class TStatusHandler(RequestHandler):
    def post(self, path):
        logger.warn("No handler for %s", path)
        self.set_status(404)

    def user_timeline(self):
        # TODO: Validate UserID?
        posts = []
        for i in range(0, 100):
            id = 10000000000000+i
            posts.append({
                "created_at": "Wed Aug 27 13:08:45 +0000 2008",
                "entities":
                {
                    "hashtags": [],
                    "urls": [],
                    "user_mentions": [],
                },
                "favorite_count": 1138,
                "id": id,
                "id_str": str(id),
                "retweet_count": 1585,
                "text": "Hello from foobar. Number #"+str(i),
                "user": TUsersHandler.dummy_user(),
            })
        self.write(dumps(posts))
        return 200

    def get(self, path):
        if path == "user_timeline.json":
            self.set_status(self.user_timeline())
            return
        logger.warn("No handler for %s", path)
        self.set_status(404)
