# E2ES Orchestrator Documentation

## Prequisites

The orchestator requires just a standard installation of
[Python 3.10](https://www.python.org/downloads/release/python-3100/) to work.

## Installation

To install the orchestrator it is sufficient to put the orchestrator.py file is
a directory like `script` (like a processor) and to create a directory named
`log` at the same level of the directory that contains the orchestrator itself.

Below there is a sample installation script

```
mkdir C:\Orchestrator
cd C:\Orchestrator
mkdir script log
move <path to orchestrator.py> script
```

## Usage

Assuming you have installed the Python interpreter correctly it is sufficient
to run the `py orchestrator.py` command to lauch the orchestrator (of this
command have to be launched from the directory in wich `orchestrator.py` is
contained).

Upon the first execution the orchestrator is going to emit two errors because it
did not found the *previous state* file and the configuration file. This is not
a fatal error, you are going to get the default for both. The previous state
file is just needed to remember the state of the UI from one execution to
another. The configuration file needs to be edited by pressing the `Settings`
button, doing the necessary changes, and the pressing `Save`, if this button is
not pressed the configuration is still going to be used by the orchestrator but
is not going to be saved on the main drive and therefore is not going to be
loaded we you reopen the orchestrator.

Once a simulation is started (by pressing the `Run!` button) the
orchestrator's window is going to become unresponsive until the end of the
simulation, you can see the progress of the simulation by looking at the
messages in the console.

## Troubleshoot

There are some known problems some of which the orchestrator cannot do much
about.
