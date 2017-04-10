from time import time
from os.path import exists
from traceback import format_exc
import logging
MAX_OUTPUT_LEN = 32
logger = logging.getLogger(__name__)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class TestResults(dict):
    def __init__(self, test, results, result):
        dict.__init__(self)
        self["test"] = test.toDict()
        self["results"] = results
        self["result"] = result


class TestFailureException(Exception):
    def __init__(self, message, assertion=None, output=("","")) :
        Exception.__init__(self, message)
        self.assertion = assertion
        self.output = output

    def toDict(self):
        return {
            "message": str(self),
            "assertion": str(self.assertion) if self.assertion is not None else None,
            "out": self.output[0].split("\n"),
            "err": self.output[1].split("\n"),
        }


class Test:
    def __init__(self, name):
        self.name = name
        self.depth = 0
        self.state = {}
        pass

    def run(self):
        print("Ran test")
        return True

    def increment_depth(self):
        self.depth += 1

    def before_test(self):
        pass

    def after_test(self):
        pass

    def after_testgroup_insert(self):
        pass

    def set_state(self, new_state):
        self.state = {**self.state, **new_state}

    def toDict(self):
        return {
            "name": self.name,
        }

    def getLog(self):
        logpath = self.state.get("log_path", None)
        if logpath is not None:
            if exists(logpath):
                with open(logpath, 'r') as f:
                    return f.read()
        return None


class TestGroup(Test):
    def __init__(self, name):
        Test.__init__(self, name)
        self.subtests = []

    def __test_single(self, test):
        error = None
        timer = 0
        result = False
        try:
            test.before_test()
            timer = time()
            try:
                test.run()
                result = True
            except AssertionError as e:
                raise TestFailureException(
                    str(e),
                    assertion=e,
                    output=test.state.get("output", ("", ""))
                    )
            except Exception as e:
                raise TestFailureException(message=e)
        except TestFailureException as te:
            logger.debug("Test exception details: %s", format_exc())
            error = te.toDict()
        timer = time() - timer
        test.after_test()
        logpath = test.state.get("log_path", None)
        log = None
        if logpath is not None:
            if exists(logpath):
                with open(logpath, 'r') as f:
                    log = f.read().split("\n")
            else:
                log = ["Log file expected but not found."]
        return {
            "test": test.toDict(),
            "log": log,
            "time": round(timer, 3),
            "result": result,
            "error": error,
        }

    def run_all(self, testNumbers=[]):
        results = []
        print(bcolors.HEADER + self.name + bcolors.ENDC)
        didPass = True
        self.before_test()
        i = 0
        for test in self.subtests:
            i += 1
            if len(testNumbers) > 0 and i not in testNumbers:
                continue
            if isinstance(test, TestGroup):
                test_result = test.run_all()
            else:
                self.before_each()
                logger.debug("Running test %s", test.name)
                test_result = self.__test_single(test)
                self.after_each()
                print(pretty_format_test(test, test_result))
            results.append(test_result)
            if test_result["result"] is not True:
                didPass = False
        self.after_test()
        return TestResults(
            self,
            results,
            didPass,
        )

    def run(self):
        return self.run_all()["result"]

    def increment_depth(self):
        for test in self.subtests:
            test.increment_depth()
        self.depth += 1

    def addTest(self, test):
        test.increment_depth()
        self.subtests.append(test)
        test.set_state(self.state)
        test.after_testgroup_insert()

    def set_state(self, new_state):
        self.state = {**self.state, **new_state}
        for test in self.subtests:
            test.set_state(new_state)

    def before_each(self):
        pass

    def after_each(self):
        pass


def pretty_format_test(test, result):
    if result["result"]:
        res = bcolors.OKGREEN + "PASS" + bcolors.ENDC
    else:
        res = bcolors.FAIL + "FAIL" + bcolors.ENDC
    strResult = test.depth*"  " + "{0} :: {1}".format(
        test.name,
        res,
    )
    if result["error"] is not None:
        strResult += "\n{0} Error: {1}".format(
            (test.depth+1)*"  ",
            result["error"]["message"],
        )
        if isinstance(result["error"], TestFailureException):
            strResult += "\n{0}See JSON output for details".format(
                (test.depth+1)*"  "
            )
    return strResult
