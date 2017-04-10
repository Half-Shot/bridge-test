import subprocess
import shutil
import tempfile
import logging
import os.path

logger = logging.getLogger(__name__)


class Git:
    def __init__(self):
        self.repos = {} # repo+#+branch => location
        self.copies = {} # repo+#+branch => [location]

    def get_copy(self, repo, branch="master"):
        location_index = repo+'#'+branch
        location = self.repos.get(location_index, None)
        counter = len(self.copies)
        if location is None:
            location = self.clone(repo, branch)
        new_location = location + "." + str(counter)
        logger.debug("Copying %s to %s.", location, new_location)
        if os.path.exists(new_location):
            logger.warn("%s already exists, deleting.", new_location)
            shutil.rmtree(new_location)
        shutil.copytree(location, new_location)
        self.copies[location_index].append(new_location)
        return new_location

    def clone(self, repo, branch="master"):
        location_index = repo+'#'+branch
        if self.repos.get(location_index) is not None:
            logger.debug("Repo %s already exists, reusing old." % location_index)
            return
        location = os.path.join(tempfile.gettempdir(), os.path.basename(location_index))
        if os.path.exists(location):
            logger.debug("Repo %s with branch %s already exists on disk, reusing and pulling." % (repo, branch))
            self.pull(location)
        else:
            logger.debug("Cloning %s with branch %s" % (repo, branch))
            result = subprocess.run(
                ["git", "clone", "-b", branch, repo, location],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            result.check_returncode()
        self.repos[location_index] = location
        self.copies[location_index] = []
        return location

    def pull(self, location):
        logger.debug("git pull %s." % location)
        process = subprocess.Popen(
            ["git", "pull"],
            cwd=location,
        )
        return process.wait() == 0

    def delete(self, repo, branch, leaveRoot=False):
        logger.debug("Deleting %s (#%s)" % (repo, branch))
        location_index = repo+'#'+branch
        location = self.repos.get(location_index, None)
        if location is not None:
            for i in range(0, len(self.copies[location_index])):
                copy = self.copies[location_index][i]
                logger.debug("rmtree %s", copy)
                shutil.rmtree(copy)
                del self.copies[location_index][i]
            if leaveRoot is False:
                logger.debug("rmtree %s", location)
                shutil.rmtree(location)
                del self.repos[location_index]
