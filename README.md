# bridge-test
A utility to run integration tests on bridges.

This tool is used to test my bridges for the Matrix platform,
in particular the integration between a homeserver and the
bridge.


## Bridges

### Current
 - Twitter

### Planned bridges
 - ~~Twitter~~
 - Discord

## Required packages

This tool requires Python 3.2 or greater, and the following packages.

* tornado
* matrix_client
* PyYAML

## Setup Instructions:

* Install synapse into the ``synapse`` directory, or point the config to a synapse install.
 * In order to have good quality tests, the synapse database and media files are **ERASED** per bridge root test.
 * Set the regisration secret token to the matching one in config so bridge-test
   can create users on the fly.
 * Config and registration files have been provided in the test directories, please make sure synapse is
   configured to use these.
 * The tool will automate the starting and stopping the HS, so **DO NOT USE**
   a live server.

## Running

Run ``python3 -m bridge-test -h`` for help.
A sample configuration file has also been provided.
