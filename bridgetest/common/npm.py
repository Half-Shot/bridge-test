import subprocess
import shutil
import tempfile
import logging
from time import sleep

logger = logging.getLogger(__name__)


class Npm:
    def __init__(self):
        self.process = None
        pass

    def install(self, path):
        logger.info("Installing npm packages...")
        process = subprocess.Popen(
            ["npm", "install"],
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        try:
            return_code = process.wait()
        except subprocess.TimeoutExpired:
            return True
        if return_code is not 0:
            raise Exception("Return code was non-zero")
        logger.info("Done.")
        return True

    def stop_process(self, kill_after=None):
        if self.process is None:
            return

        outS, errS, timedOut = self.__read_process_stream(self.process, kill_after=kill_after)
        rc = self.process.returncode
        self.process = None
        return (timedOut, rc, (outS, errS))

    def start(self, path, cmd, kill_after=None, noRead=False):
        if self.process and noRead:
            logger.warn("Opening a process while a current one is running.")
        process = subprocess.Popen(
            ["node"] + cmd,
            cwd=path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if noRead:
            self.process = process
        else:
            outS, errS, timedOut = self.__read_process_stream(process, kill_after)
            return (timedOut, process.returncode, (outS, errS))

    def __read_process_stream(self, proc, kill_after=None):
        timedOut = False
        outS = ""
        errS = ""
        try:
            outs, errs = proc.communicate(timeout=kill_after)
            outS = outs.decode()
            errS = errs.decode()
        except subprocess.TimeoutExpired as e:
            proc.terminate()
            proc.wait()
            if e.stdout is not None:
                outS = e.stdout.decode()
            if e.stderr is not None:
                errS = e.stderr.decode()
            timedOut = True
        logger.debug("%s was terminated", str(" ".join(proc.args)))
        return (outS, errS, timedOut)
