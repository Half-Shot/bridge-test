import subprocess
import requests
import logging
import json
import hashlib
import hmac
import contextlib
from os import unlink
from matrix_client.client import MatrixClient
from os.path import join
from shutil import rmtree
HS_URL = "http://localhost:8008"
HS_USERNAME = "bridge-test"
HS_PASSWORD = "bridgetester"
HS_SECRET = b"thisisntverysecret"
logger = logging.getLogger(__name__)


class MatrixHelper():
    def __init__(self, location):
        self.location = location
        self.accessToken = None
        self.client = None
        pass

    def isRunning(self):
        try:
            r = requests.get(HS_URL + "/_matrix/client/versions")
        except requests.exceptions.ConnectionError as e:
            return False
        return r.status_code == 200

    def refreshSynapse(self):
        self.stop()
        with contextlib.suppress(FileNotFoundError):
            rmtree(join(self.location, "media_store"))
            rmtree(join(self.location, "uploads"))
            unlink(join(self.location, "homeserver.db"))
            unlink(join(self.location, "homeserver.log"))
        # Create testing user
        self.start()
        self.__register_user()
        self.stop()

    def start(self):
        if self.isRunning():
            logger.info("synapse is already running")
            return
        logger.info("starting synapse")
        process = subprocess.Popen(
            "/bin/bash -c 'source bin/activate; synctl start'",
            cwd=self.location,
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
        return MatrixClient(HS_URL, token=self.accessToken, user_id=self.userId)

    def stop(self):
        if not self.isRunning():
            logger.info("synapse is not running")
            return
        logger.info("stopping synapse.")
        process = subprocess.Popen(
            "/bin/bash -c 'source bin/activate; synctl stop'",
            cwd=self.location,
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

        logger.info("attempting to register user")
        try:
            req = requests.post(
                "%s/_matrix/client/api/v1/register" % (HS_URL),
                data=json.dumps(data),
            )
            if req.ok:
                logger.info("succeeded")
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
            key=HS_SECRET,
            digestmod=hashlib.sha1,
        )
        mac.update(HS_USERNAME.encode('utf-8'))
        mac.update(b"\x00")
        mac.update(HS_PASSWORD.encode('utf-8'))
        mac.update(b"\x00")
        mac.update("admin".encode('utf-8'))
        mac = mac.hexdigest()
        return mac
