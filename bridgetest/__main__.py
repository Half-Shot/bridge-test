#!/usr/bin/python3
from argparse import ArgumentParser
from bridgetest.twitter.twitter import TwitterTest
import yaml
import logging
import sys
import os.path as path
import json


TESTS = {
    "twitter": TwitterTest
}


def get_args():
    parser = ArgumentParser(
        prog="bridge-test",
        description="Test bridges for the matrix platform."
    )
    parser.add_argument(
        "--config", "-c",
        help="config file path",
        default="config.yaml",
        type=str,
    )
    actionGroup = parser.add_mutually_exclusive_group()
    parser.add_argument(
        "--testgroups", "-g",
        help="select subtest(s) of a test to run, or leave off for all",
        default=[],
        type=int,
        nargs="+",
    )
    actionGroup.add_argument(
        "--test", "-t",
        help="test to run",
        default=None,
        type=str,
    )
    actionGroup.add_argument(
        "--list", "-l",
        help="list tests",
        action="store_true",
    )
    parser.add_argument('-v', '--verbose', action='count', default=0)
    return parser.parse_args()


args = get_args()
logging.basicConfig(format='%(levelname)s:%(name)s:%(message)s', level=20 - (args.verbose*10))
logger = logging.getLogger(__file__)
cfg = None
try:
    with open(args.config, 'r') as f:
        cfg = yaml.load(f)
except Exception as e:
    logger.error("Could not load config file. Reason: %s", str(e))
    sys.exit(1)
if args.list:
    print("\n ".join(TESTS.keys()))
    sys.exit(0)
if args.test is None:
    logger.error("You must specify a test as a argument.")
    sys.exit(2)
if args.test not in TESTS.keys():
    logger.error("You must specify a test that exists in this version.")
    sys.exit(3)
else:
    test = TESTS[args.test]()
    results, exitCode = test.run_tests(cfg, args)
    if "output_directory" in cfg:
        res_path = path.join(cfg["output_directory"], args.test + ".json")
        with open(res_path, "w") as f:
            json.dump(results, f, indent=2)
        if results["result"] is True:
            logger.info("Tested OK.")
        else:
            logger.error("Some tests failed. Please unfail them :)")
    sys.exit(0 if exitCode is 0 else exitCode+10)
