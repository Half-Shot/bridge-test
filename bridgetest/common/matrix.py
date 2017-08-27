import subprocess
import requests
import logging
import json
import hashlib
import hmac
import contextlib
from os import unlink
from matrix_client.client import MatrixClient
from matrix_client.user import User
from os.path import join
from shutil import rmtree
from urllib.parse import urljoin
HS_USERNAME = "bridge-test"
HS_PASSWORD = "bridgetester"
logger = logging.getLogger(__name__)


class MatrixHelper():
    def __init__(self, cfg):
        if cfg["type"] != "synapse":
            logger.critical("Currently the bridge only supports synapse. Bailing!")
        for key in ["path", "url", "registration_shared_secret"]:
            if key not in cfg:
                logger.critical("'homeserver.%s' is missing from config!" % key)
                raise Exception("Missing keys in config. Tests will not run.")
        self.cfg = cfg
        self.accessToken = None
        self.client = None
        pass

    def isRunning(self):
        try:
            r = requests.get(urljoin(self.cfg["url"], "/_matrix/client/versions"))
        except requests.exceptions.ConnectionError as e:
            return False
        return r.status_code == 200

    def refreshSynapse(self, killAfter=True):
        self.stop()
        with contextlib.suppress(FileNotFoundError):
            rmtree(join(self.cfg["path"], "media_store"))
            rmtree(join(self.cfg["path"], "uploads"))
            unlink(join(self.cfg["path"], "homeserver.db"))
            unlink(join(self.cfg["path"], "homeserver.log"))
        # Create testing user
        # Invalidate the client
        self.client = None
        self.start()
        self.__register_user()
        if killAfter:
            self.stop()

    def start(self):
        if self.isRunning():
            logger.debug("synapse is already running")
            return
        logger.info("starting synapse")
        process = subprocess.Popen(
            "/bin/bash -c 'source bin/activate; synctl start'",
            cwd=self.cfg["path"],
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        process.wait()
        if process.returncode != 0:
            raise Exception("Synapse start script didn't return 0")

    def getClient(self):
        if not self.isRunning():
            raise Exception("Synapse isn't running.")
        if self.client is None:
            self.client = MatrixClient(
                self.cfg["url"],
                token=self.accessToken,
                user_id=self.userId
            )
        return self.client

    def getUser(self, user_id):
        return User(self.client.api, user_id)

    def stop(self):
        if not self.isRunning():
            logger.debug("synapse is not running")
            return
        logger.info("stopping synapse.")
        process = subprocess.Popen(
            "/bin/bash -c 'source bin/activate; synctl stop'",
            cwd=self.cfg["path"],
            shell=True,
            stdout=None,
            stderr=None,
        )
        process.wait()
        if process.returncode != 0:
            raise Exception("Synapse start script didn't return 0")

    def __register_user(self):
        mac = self.__generate_mac()
        data = {
            "user": HS_USERNAME,
            "password": HS_PASSWORD,
            "mac": mac,
            "type": "org.matrix.login.shared_secret",
            "admin": True,
        }

        logger.debug("attempting to register user")
        try:
            req = requests.post(
                "%s/_matrix/client/api/v1/register" % (self.cfg["url"]),
                data=json.dumps(data),
            )
            if req.ok:
                data = req.json()
                self.accessToken = data["access_token"]
                self.userId = data["user_id"]
                logger.debug("/register returned %s", req.text)
                return
            else:
                raise Exception(req.text)
        except Exception as e:
            logger.error("call to /register failed, %s", str(e))
            raise e
        logger.warn("failed to register new user")

    def __generate_mac(self):
        mac = hmac.new(
            key=self.cfg["registration_shared_secret"].encode(),
            digestmod=hashlib.sha1,
        )
        mac.update(HS_USERNAME.encode('utf-8'))
        mac.update(b"\x00")
        mac.update(HS_PASSWORD.encode('utf-8'))
        mac.update(b"\x00")
        mac.update("admin".encode('utf-8'))
        mac = mac.hexdigest()
        return mac
