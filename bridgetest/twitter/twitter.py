#!/usr/bin/python3
from bridgetest.common import TestGroup, Git, Npm, MatrixHelper
from bridgetest.twitter.proxy.proxy import TwitterProxy
from traceback import format_exc
import bridgetest.twitter.tests as tests
import logging
from os.path import abspath, dirname, join

GIT_REPO = "https://github.com/Half-Shot/matrix-appservice-twitter"
GIT_BRANCH = "proxy"

# Setup logger
logger = logging.getLogger(__name__)


class TwitterTest:
    def run_tests(self, cfg=None, args=None):
        root_dir = abspath(dirname(__file__))
        git = Git()
        npm = Npm()
        proxy = TwitterProxy()
        if "synapse" in cfg:
            if "path" in cfg["homeserver"]:
                matrix = MatrixHelper(cfg["homeserver"])

        exitCode = 0
        results = None
        try:
            # Create temp directory and clone
            location = git.clone(GIT_REPO, GIT_BRANCH)
            # Install NPM packages
            npm.install(location)
            root = TestGroup("Twitter AS")
            matrix.refreshSynapse()
            matrix.start()
            proxy.start()
        except Exception as e:
            logger.error("Exception during init stage.")
            tb = format_exc()
            logger.error("%s", tb)
            exitCode = 1
        if exitCode is 0:
            root.set_state({
                'repo': GIT_REPO,
                'branch': GIT_BRANCH,
                'npm': npm,
                'git': git,
                'matrix': matrix,
                'proxy': proxy,
                'proxy_state': {},
                'cmd': ["twitter-as.js", "-p", "9000", "-c", "config.yaml"],
                'config': join(root_dir, "configs", "config.yaml"),
                'config.min': join(root_dir, "configs", "config.min.yaml"),
                'config.profile.displayname': join(root_dir, "configs", "config.profile.displayname.yaml"),
                'registration': join(root_dir, "configs", "registration.yaml"),
            })
            root.addTest(tests.StartBridgeTestGroup())
            root.addTest(tests.AliasesTestGroup())
            root.addTest(tests.ProfileTestGroup())
            results = root.run_all(testNumbers=args.testgroups)
        matrix.stop()
        proxy.stop()
        git.delete(GIT_REPO, GIT_BRANCH, leaveRoot=True)
        return (results, exitCode)
