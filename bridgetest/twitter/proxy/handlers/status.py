from tornado.web import RequestHandler
from .users import TUsersHandler
import logging
from json import dumps
logger = logging.getLogger(__name__)


class TStatusHandler(RequestHandler):
    def post(self, path):
        logger.warn("No handler for %s", path)
        self.set_status(404)

    def get_posts_profile_change(self):
        posts = []
        posts.append({
            "created_at": "Wed Aug 27 13:08:45 +0000 2008",
            "entities":
            {
                "hashtags": [],
                "urls": [],
                "user_mentions": [],
            },
            "favorite_count": 1138,
            "id": 1,
            "id_str": "1",
            "retweet_count": 1585,
            "text": "Hello from foobar. Number #1",
            "user": TUsersHandler.dummy_user(),
        })
        user = TUsersHandler.dummy_user_2()
        user.id = TUsersHandler.dummy_user().id
        user.id_str = TUsersHandler.dummy_user().id_str
        posts.append({
            "created_at": "Wed Aug 27 13:08:46 +0000 2008",
            "entities":
            {
                "hashtags": [],
                "urls": [],
                "user_mentions": [],
            },
            "favorite_count": 1138,
            "id": 2,
            "id_str": "2",
            "retweet_count": 1585,
            "text": "Hello from foobar. Number #2",
            "user": user,
        })
        return posts

    def user_timeline(self):
        # TODO: Validate UserID?
        if self.settings["test_state"].get("timeline.profilechange", False):
            posts = self.get_posts_profile_change()
        else:
            posts = []
            i = 100
            posts.append({
                "created_at": "Wed Aug 27 13:08:45 +0000 2008",
                "entities":
                {
                    "hashtags": [],
                    "urls": [],
                    "user_mentions": [],
                },
                "favorite_count": 1138,
                "id": i,
                "id_str": str(i),
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
