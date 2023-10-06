"""This module contains the code for the GUI and the logic to operate and run
the orchestrator.

In the code we made use of two lesser known Python functionalities to make the
code more succint. This two functionalities are the way in which the boolean
operator "or" evalutates its arguments and the way in which default arguments
are assigned. The reader who is less familiar can find more information about
them following this two URLs below.

https://docs.python.org/3/reference/expressions.html#boolean-operations
https://docs.python.org/3/reference/compound_stmts.html#function-definitions

On some installations of tkinter, like the one on Windows Server 2019, the
arguments passed to its functions, which are supposed to be integers, are
converted to strings in the function (on macOS Ventura and Windows 10 this does
not happen). This creates problem if you pass as aguments instances of
enum.IntEnum, because its __str__ method is different from the one of int. To
solve this always use the .value attribute of enum.IntEnum when passing its
instances to tkinter functions.

This module suffers from time-of-check to time-of-use "vulnerabilities", and
various it file system atomicity problems, it expects to be the only one to
operate on the various files and directories. Solving this problem is hard and
since this orchestrator is meant to be executed in trusted environments we did
not tackle it.

Things that I would do better next time:
  * Do not rely too much on Python's shutil for archives since for validation
    and custom insertion logic I still have to write my own functions;
  * Do not nest functions definitions.
  * Use a global logger object.
  * Move around directories this shortens a lot of paths and at least makes sure
    that the directory that I'm in can't be deleted.
  * Parse an in memory CSV of the various conf defaults etc... And generate at
    startup the various lists, since the "inpact on startup performance" is
    really negligible.
  * use pathlib.Path to give a type to pats that is different from str.
  * create an enum for HydroGNSS-1 or HydroGNSS-2??
"""

# TODO: add a VERSION global so that it can be displayed in the window.

import enum
import glob
import inspect
import io
import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk
import typing
import zipfile

# We do not know if this is really needed for high DPI screens.
# import ctypes
# ctypes.windll.shcore.SetProcessDpiAwareness(1)

if __debug__:
    # A few functions usefull in assertions.
    implies = lambda A, B: not A or B
    iff = lambda A, B: bool(A) == bool(B)
    xor = lambda A, B: bool(A) != bool(B)

################################################################################
# Data                                                                         #
################################################################################

# Processors ###################################################################
class Proc(enum.IntEnum):
    """The processors that the orchestrator manages."""
    L1A  = 0           # HSAVERS
    L1B  = enum.auto() # ???
    L2FB = enum.auto() # Forest Biomass
    L2FT = enum.auto() # Freeze/Thaw state
    L2SI = enum.auto() # Surface Inundation
    L2SM = enum.auto() # Soil Moisture

# The PAM (Performance Assesment Module) expects the names with this format.
PROC_NAMES_PAM = ["L1_A", "L1_B", "L2_FB", "L2_FT", "L2_SI", "L2_SM",]
assert len(Proc) == len(PROC_NAMES_PAM)

# Where the various processors should put their outputs.
PROC_OUTPUT_DIRS = [
    "L1A_L1B",
    "L1A_L1B",
    "L2OP-FB",
    "L2OP-FT",
    "L2OP-SI",
    "L2OP-SSM",
]
assert len(Proc) == len(PROC_OUTPUT_DIRS)

# Configuration of the variuous processors #####################################
# Here we define a big table (the lists here defined are its rows) with all the
# usefull information about the paths that are needed by the various processors.

class Conf(enum.IntEnum):
    """All the paths that can be configured. The name in the enumaration is also
    the key in the JSON object used for serialization."""
    BACKUP_DIR      = 0
    DATA_DIR        = enum.auto()
    L1A_EXE         = enum.auto()
    L1B_EXE         = enum.auto()
    L1B_MM_EXE      = enum.auto()
    L1B_CX_EXE      = enum.auto()
    L1B_CC_EXE      = enum.auto()
    L2FB_EXE        = enum.auto()
    L2FT_EXE        = enum.auto()
    L2SI_EXE        = enum.auto()
    L2SM_EXE        = enum.auto()
    PAM_EXE         = enum.auto()

class ConfKind(enum.Enum):
    """Which kind of path to expect in the configuration option."""
    EXE = enum.auto()
    DIR = enum.auto()

# Names of the configuration options to be displayed in the GUI.
CONF_NAMES = [
    "Backup Directory",
    "Data Directory",
    "L1A Executable",
    "L1B Executable",
    "L1BMM Executable",
    "L1BCX Executable",
    "L1BCC Executable",
    "L2FB Executable",
    "L2FT Executable",
    "L2SI Executable",
    "L2SM Executable",
    "PAM Executable",
]
assert len(CONF_NAMES) == len(Conf)

# What kind of path the configuration options want.
CONF_KINDS = [
    ConfKind.DIR,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
    ConfKind.EXE,
]
assert len(CONF_KINDS) == len(Conf)

CONF_VALUES_DEFAULT = [
    "C:\\E2ES_backups",
    "C:\\PDGS_NAS_folder",
    "C:\\L1A\\bin\\HSAVERS.exe",
    "C:\\L1BOP\\scripts\\Run_L1b_Processor_with_dates.py",
    "C:\\L1OP-MM\\scripts\\Run_L1Merge_with_dates.py",
    "C:\\L2OP-SI\\bin\\L1B_CX_DR.exe",
    "C:\\L2OP-SI\\bin\\L1B_CC_DR.exe",
    "C:\\L2OP-FB\\bin\\L2OP_FB.exe",
    "C:\\L2OP-FT\\bin\\L2PPFT_mainscript.exe",
    "C:\\L2OP-SI\\bin\\L2OP_SI_DR.exe",
    "C:\\L2OP-SSM\\bin\\SML2OP_start.exe",
    "C:\\PAM\\bin\\PAM_start.exe",
]
assert len(CONF_VALUES_DEFAULT) == len(Conf)

CONF_DIALOG_TITLES = [
    "Choose the backup directory",
    "Choose the main input output directory",
    "Choose the L1A executable",
    "Choose the L1B executable",
    "Choose the L1B merge module executable",
    "Choose the L1B CX executable",
    "Choose the L1B CC executable",
    "Choose the L2FB executable",
    "Choose the L2FT executable",
    "Choose the L2SI executable",
    "Choose the L2SM executable",
    "Choose the PAM executable",
]
assert len(CONF_DIALOG_TITLES) == len(Conf)

class ConfGroup(enum.IntEnum):
    IO_DIR  = 0
    L1A     = enum.auto()
    L1B     = enum.auto()
    L2FB    = enum.auto()
    L2FT    = enum.auto()
    L2SI    = enum.auto()
    L2SM    = enum.auto()
    PAM     = enum.auto()

CONF_GROUP_NAME = [
    "Input/Output Directories",
    "HSAVERS",
    "L1B Processors",
    "Forest Biomass",
    "Freeze/Thaw state",
    "Surface Inundation",
    "Soil Moisture",
    "Performance Assesment Module",
]
assert len(ConfGroup) == len(CONF_GROUP_NAME)

CONF_GROUP = [
    ConfGroup.IO_DIR,
    ConfGroup.IO_DIR,
    ConfGroup.L1A,
    ConfGroup.L1B,
    ConfGroup.L1B,
    ConfGroup.L1B,
    ConfGroup.L1B,
    ConfGroup.L2FB,
    ConfGroup.L2FT,
    ConfGroup.L2SI,
    ConfGroup.L2SM,
    ConfGroup.PAM,
]
assert len(Conf) == len(CONF_GROUP)

# NOTE: can I delete this?
# The directories that should always be in DataRelease.
DATA_RELEASE_SUBDIRS = [
    "L1A_L1B",
    "L1A-SW-RX",
    "L2OP-FB",
    "L2OP-FT",
    "L2OP-SI",
    "L2OP-SSM",
    "L2-FDI",
]

# Log Levels ###################################################################

class LogLevel(enum.IntEnum):
    DEBUG = 0
    INFO = enum.auto()
    WARN = enum.auto()
    ERROR = enum.auto()

# The selectable levels are specified in the ICD document.
LOG_LEVELS_FOR_DISPLAY = ["DEBUG", "INFO", "WARN",    "ERROR"]
LOG_LEVELS_IEEC       = ["DEBUG", "INFO", "WARNING", "ERROR"]
LOG_LEVELS_IFAC       = ["yes",   "yes",  "no",      "no"]

# Arguments ####################################################################

class Args(typing.TypedDict):
    """The arguments needed to run the orchestration. Not all combination of
    arguments are valid."""
    start: Proc
    end: Proc
    pam: bool
    backup: str
    log_level: LogLevel

ARGS_DEFAULT: Args = {
    "start": Proc.L1A,
    "end": Proc.L1A,
    "pam": False,
    "backup": "",
    "log_level": LogLevel.INFO,
}

################################################################################
# Code                                                                         #
################################################################################

# Utilities ####################################################################

@typing.no_type_check
def _enum_members_as_strings(e: enum.Enum) -> list[str]:
    return list(e.__members__)

def _escape_string(s: str) -> str:
    # f"{s!r}"[2:-2]
    return s.encode("unicode_escape").decode("utf-8")

_experiment_name_format = re.compile(
    "_[0-9]{2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{2}$"
)


# Windows ######################################################################

if os.name == 'nt':
    import ctypes.wintypes

    _In_, _Out_ = 1, 2

    # https://learn.microsoft.com/en-us/windows/win32/api/shellapi/ns-shellapi-shfileopstructa
    class SHFILEOPSTRUCTA(ctypes.Structure):
        _fields_ = [
            ("hwnd",                  ctypes.wintypes.HWND),
            ("wFunc",                 ctypes.wintypes.UINT),
            ("pFrom",                 ctypes.wintypes.LPCSTR), # PCZZSTR
            ("pTo",                   ctypes.wintypes.LPCSTR), # PCZZSTR
            ("fFlags",                ctypes.wintypes.UINT), # FILEOP_FLAGS
            ("fAnyOperationsAborted", ctypes.wintypes.BOOL),
            ("hNameMappings",         ctypes.wintypes.LPVOID),
            ("lpszProgressTitle",     ctypes.wintypes.LPCSTR), # PCSTR
       ]

    # https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shfileoperationa
    SHFileOperationA_prototype = ctypes.WINFUNCTYPE( # type: ignore
        ctypes.c_int,
        ctypes.POINTER(SHFILEOPSTRUCTA)
    )
    SHFileOperationA = SHFileOperationA_prototype(
        ("SHFileOperationA", ctypes.cdll.shell32),
        (
            (_In_, "lpFileOp"),
        )
    )
    def _check_SHFileOperationA_err(result, func, args):
        if result != 0:
            raise OSError()
        return args
    SHFileOperationA.errcheck = _check_SHFileOperationA_err
    FO_DELETE = 0x3
    FOF_ALLOWUNDO = 0x40
    FOF_NOCONFIRMATION = 0x10

    def _recycle(path: str) -> None:
        path_bytes = (path + "\0").encode()
        # Some errors are written in fAnyOperationsAborted, but we do not check
        # them...
        file_op = SHFILEOPSTRUCTA(
            None,
            FO_DELETE,
            ctypes.c_char_p(path_bytes),
            None,
            FOF_ALLOWUNDO | FOF_NOCONFIRMATION,
            False,
            None,
            None
        )
        SHFileOperationA(ctypes.pointer(file_op))

# if os.mkdir ever creates problems:
# https://learn.microsoft.com/en-us/windows/win32/api/shlobj_core/nf-shlobj_core-shcreatedirectoryexa

# Implementation ###############################################################

def validate_arguments(args: Args) -> bool:
    start = args["start"]
    end = args["end"]
    pam = args["pam"]
    backup = args["backup"]

    if start > end:
        return False
    if start > Proc.L1B and start != end:
        return False
    if backup and start == Proc.L1A:
        return False
    if pam and end < Proc.L1B:
        return False

    # NOTE: does it make sense to keep the spec?
    assert start <= end
    assert implies(start > Proc.L1B, start == end)
    assert implies(backup, start > Proc.L1A)
    assert implies(pam, end > Proc.L1A)

    return True

assert validate_arguments(ARGS_DEFAULT)

# NOTE: more than 'conf' the name should be 'conf_paths'
def run(logger: logging.Logger, args: Args, conf: list[str]) -> None:
    """If anything goes wrong this function throws an exception with an
    explenation of what went wrong."""

    assert validate_arguments(args)
    assert len(conf) == len(Conf)

    data_dir = conf[Conf.DATA_DIR]
    auxiliary_data_dir = os.path.join(data_dir, "Auxiliary_Data")
    hydrognss_1_dir = os.path.join(data_dir, "HydroGNSS-1")
    hydrognss_2_dir = os.path.join(data_dir, "HydroGNSS-2")

    # This is used later to create the backup name and to give input to the PAM
    # and it is set either when loading a backup or when running HSAVERS.
    experiment_name = ""

    # Assigned later
    which_hydrognss = "" # will be either "HydroGNSS-1" or "HydroGNSS-2"
    hydrognss_dir = lambda: os.path.join(data_dir, which_hydrognss)
    data_release_dir = lambda: os.path.join(hydrognss_dir(), "DataRelease")
    l1a_l1b_dir = lambda: os.path.join(data_release_dir(), "L1A_L1B")
    experiment_name_file = lambda: os.path.join(data_release_dir(), "experiment_name.txt")

    start = args["start"]
    end = args["end"]
    pam = args["pam"]
    backup = args["backup"]
    should_clean = bool(start == Proc.L1A or backup)
    # Given the fact that Python allows you to create custom error levels here
    # we just ignore the ones in between and the ones above and below them.
    # Maybe we should throw an exception if we detect extraneous log levels.
    log_level = args["log_level"]

    # We convert our log level number to Python's standard library log level number.
    logger.setLevel((log_level+1)*10)

    # Doing some minimal validation here.

    if os.name != "nt":
        logger.info("skipping the run because we are not on windows")
        return

    for file, kind in zip(conf, CONF_KINDS):
        if not os.path.exists(file):
            raise FileNotFoundError(file)
        if kind == ConfKind.DIR and not os.path.isdir(file):
            raise NotADirectoryError(file)
        if kind == ConfKind.EXE and not os.path.isfile(file):
            raise IsADirectoryError(file)
    del file, kind

    if backup and not os.path.isfile(backup):
        raise FileNotFoundError(backup)

    def run_processor(file_path: str, arguments: str) -> None:
        exe = file_path if file_path.endswith(".exe") \
            else f"py {file_path}" if file_path.endswith(".py") \
            else None

        if exe is None:
            raise ValueError(f"only python and exe files are supported, "
                f"{file_path} is not supported")

        working_dir, _, _ = file_path.rpartition('\\')

        # We expect %COMSPEC% to be cmd.exe or something like that.
        try:
            cmd_with_args = f"{exe} {arguments}"
            logger.info(f"launching '{cmd_with_args}'")
            # NOTE: should I worry about 'universal_newlines'?
            with subprocess.Popen(
                args=cmd_with_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=working_dir,
                text=True
                ) as p:
                assert p.stdout is not None # Just for mypy.
                for line in p.stdout:
                    # Since in io.TextIOBase lines are split on '\n' it there are
                    # any \r in the sequence we just ignore it.
                    logger.info(line.rstrip())
                    # TODO: Sometimes the output seems to stop in the console
                    # until you press enter it is the so called "mark mode" and
                    # it can be programmatically detected and disabled.
                    # https://stackoverflow.com/questions/13599822/command-prompt-gets-stuck-and-continues-on-enter-key-press
                    # https://stackoverflow.com/questions/41409727/turn-off-windows-10-console-mark-mode-from-my-application

                if p.wait() != 0:
                    raise ChildProcessError(f"{file_path} exited with error code {p.returncode}")
        except Exception as ex:
            raise Exception(f"something went wrong during the execution of "
                f"{file_path}") from ex

    def check_existence_of_netcdf_file(start_dir: str):
        walker = os.walk(
            start_dir,
            onerror=lambda ex: logger.exception("an error occured while traversing"
                f"'{ex.filename}' we ignore it and keep going"))
        for dirpath, dirnames, filenames in walker:
            if any(filename.endswith(".nc") for filename in filenames):
                return

        raise ChildProcessError(f"no NetCDF file generated in '{start_dir}'")

    def do_backup_and_pam() -> None:
        timestamp = f"{int(time.time())}"
        assert len(timestamp) == 10
        assert experiment_name
        assert which_hydrognss
        backup_name = f"{experiment_name}_{timestamp}"
        backup_path_noext = os.path.join(conf[Conf.BACKUP_DIR], backup_name)
        logger.info("doing the backup")
        try:
            shutil.make_archive(backup_path_noext, "zip", data_dir, which_hydrognss)
        except Exception as ex:
            raise Exception("unable to make backup archive") from ex
        if pam:
            logger.info("running the PAM")
            run_processor(
                conf[Conf.PAM_EXE],
                f"{PROC_NAMES_PAM[end]} {auxiliary_data_dir} "
                f"{conf[Conf.BACKUP_DIR]} {backup_name}"
            )

            pam_output = os.path.join(conf[Conf.BACKUP_DIR], "PAM_Output")
            try:
                with zipfile.ZipFile(f"{backup_path_noext}.zip", 'a') as zipf:
                    for file in os.listdir(pam_output):
                        file_path = os.path.join(pam_output, file)
                        zipf.write(file_path, f"{which_hydrognss}\\DataRelease\\PAM_Output\\{file}")
            except Exception as ex:
                raise Exception("unable to add the PAM output figures to the "
                    "backup") from ex
            _recycle(pam_output)

            if start <= Proc.L1B <= end: # If L1B was executed.
                logger.info("running the compare tool")
                # Wee peel of two files from the L1B executable path.
                should_be_bin, _, _ = conf[Conf.L1B_EXE].rpartition("\\")
                should_be_L1B, _, _ = should_be_bin.rpartition("\\")
                compare_L1B_exe: typing.Union[list[str], str] = glob.glob('**/compareL1B.exe',
                    root_dir=should_be_L1B, recursive=True)
                if len(compare_L1B_exe) != 1:
                    logger.info("skipping compare L1B because too many were found {compare_L1B_exe}")
                    return
                compare_L1B_exe = compare_L1B_exe[0]
                compare_L1B_exe = os.path.join(should_be_L1B, compare_L1B_exe)
                if not os.path.isfile(compare_L1B_exe):
                    logger.info("skipping compare L1B because it was not found")
                    return
                run_processor(
                    compare_L1B_exe,
                    f"{backup_path_noext}.zip"
                )
                compare_tool_out_path = os.path.join(f"{conf[Conf.BACKUP_DIR]}",
                        "compareL1B_output")
                with zipfile.ZipFile(f"{backup_path_noext}.zip", 'a') as zipf:
                    RR_plots_dir = os.path.join(compare_tool_out_path,
                        f"{backup_name}_SSTLplots_1_RR")
                    LR_plots_dir = os.path.join(compare_tool_out_path,
                        f"{backup_name}_SSTLplots_1_LR")
                    try:
                        for file in os.listdir(RR_plots_dir):
                            file_path = os.path.join(RR_plots_dir, file)
                            zipf.write(file_path, f"{which_hydrognss}\\DataRelease\\SSTLplots_1_RR\\{file}")
                    except FileNotFoundError:
                        logger.exception("an error occurred while putting RR in the backup")
                    try:
                        for file in os.listdir(LR_plots_dir):
                            file_path = os.path.join(LR_plots_dir, file)
                            zipf.write(file_path, f"{which_hydrognss}\\DataRelease\\SSTLplots_1_LR\\{file}")
                    except FileNotFoundError:
                        logger.exception("an error occurred while putting LR in the backup")
                _recycle(compare_tool_out_path)

        logger.info("orchestration finished")
        # NOTE: it would be cool to send a notificaiton:
        # https://github.com/jithurjacob/Windows-10-Toast-Notifications/blob/master/win10toast/__init__.py
        # https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shell_notifyicona
        print("\a", end='')

    if should_clean:
        logger.info("cleaning up from previous execution")
        if os.path.exists(hydrognss_1_dir):
            _recycle(hydrognss_1_dir)
        if os.path.exists(hydrognss_2_dir):
            _recycle(hydrognss_2_dir)
        if backup:
            backup_name_format = re.compile("_[0-9]{10}\.zip$")
            experiment_name = backup_name_format.sub("", backup).split("\\")[-1]
            if experiment_name == backup:
                raise Exception("invalud backup file selected")
            logger.info("loading the backup")
            with zipfile.ZipFile(backup) as zipf:
                name_list = zipf.namelist()
                if name_list[0].startswith("HydroGNSS-1"):
                    which_hydrognss = "HydroGNSS-1"
                elif name_list[0].startswith("HydroGNSS-2"):
                    which_hydrognss = "HydroGNSS-2"
                else:
                    raise ValueError("the backup contains a bad file: {name_list[0]!r}")
                if not all(name.startswith(which_hydrognss) for name in name_list):
                    raise ValueError("not all the files in the backup are in "
                        "the {which_hydrognss} directory")
                if os.path.exists(hydrognss_1_dir) and os.path.exists(hydrognss_2_dir):
                    raise Exception("Both HydroGNSS-1 and HydroGNSS-2 are present. Please "
                        "delete one of the two.")
            try:
                shutil.unpack_archive(backup, data_dir)
            except Exception as ex:
                raise Exception("unable to extract the backup") from ex
    else:
        if os.path.exists(hydrognss_1_dir) and os.path.exists(hydrognss_2_dir):
            raise Exception("Both HydroGNSS-1 and HydroGNSS-2 are present. Please "
                "delete one of the two.")
        which_hydrognss = "HydroGNSS-1" if os.path.exists(hydrognss_1_dir) \
            else "HydroGNSS-2"
        try:
            with open(os.path.join(data_release_dir(), "experiment_name.txt")) as f:
                experiment_name = f.read().strip()
        except Exception as ex:
            raise Exception("unable to read the experiment name from the file") from ex
        if not _experiment_name_format.search(experiment_name):
            raise ValueError("the experiment name does not have the correct "
                "format in the experiment_name.txt file")
        logger.info("keeping the data release directory of the previous execution")

    # The actual "orchestration" starts here.

    if start == Proc.L1A:
        logger.info("runnning L1A")
        run_processor(
            conf[Conf.L1A_EXE],
            ""
        )

        l1a_work_dir, _, _ = conf[Conf.L1A_EXE].rpartition('\\')
        l1a_output_file = os.path.join(
            l1a_work_dir,
            "..\conf\AbsoluteFilePath.txt"
        )
        try:
            with open(l1a_output_file) as f:
                l1a_out = f.read().strip()
        except Exception as ex:
            raise Exception("unable to get L1A output path") from ex

        if not os.path.exists(l1a_out):
            raise Exception(
                f"L1A produced output in a non existing directory: {l1a_out}"
            )

        which_hydrognss = list(filter(None, l1a_out.split("\\")))[-1]
        if which_hydrognss != "HydroGNSS-1" and which_hydrognss != "HydroGNSS-2":
            raise ValueError("HSAVERS did not put the satellite in the path '{l1a_out}'")
        experiment_name = list(filter(None, l1a_out.split("\\")))[-2]
        if not _experiment_name_format.search(experiment_name):
            raise ValueError("the L1A output directory has not the correct format")

        try:
            os.mkdir(hydrognss_dir())
            for direc in DATA_RELEASE_SUBDIRS:
                direc = os.path.join(data_release_dir(), direc)
                os.makedirs(direc)
            del direc
        except Exception as ex:
            raise Exception("unable to create the directory structure") from ex

        # This is needed for when not should_clean, so that the PAM can read the
        # appropriate file from the PAM directory in the backup folder.
        try:
            with open(os.path.join(data_release_dir(), "experiment_name.txt"), 'w') as f:
                f.write(experiment_name)
        except Exception as ex:
            raise Exception("unable to write the experiment name in the file") from ex

        l1a_out_dir = os.path.join(l1a_out, f"DataRelease\\{PROC_OUTPUT_DIRS[Proc.L1A]}")
        try:
            shutil.copytree(l1a_out_dir, l1a_l1b_dir(), dirs_exist_ok=True)
        except Exception as ex:
            raise Exception("unable to copy {l1a_out_dir} to "
                "{data_release_dir()}") from ex

        # The last 21 characters are the ones of the timestamp.
        l1a_file_for_pam = os.path.join(l1a_out,
            f"{experiment_name[:-21]}_inOutReferenceFile.mat")

        try:
            shutil.copy2(l1a_file_for_pam, data_release_dir())
        except Exception as ex:
            raise Exception("unable to copy files for the PAM") from ex

        check_existence_of_netcdf_file(l1a_l1b_dir())
        if end == Proc.L1A:
            do_backup_and_pam()
            return

    assert experiment_name, "This variable should have been assigned by now"
    assert which_hydrognss, "This variable should have been assigned by now"

    logger.info("detecting the dates of the simulation")
    try:
        year_month_format = re.compile("^[0-9]{4}-[0-9]{2}$")
        day_format = re.compile("^[0-9]{2}$")

        year_month_list = sorted(os.listdir(l1a_l1b_dir()))
        if not all(year_month_format.search(year_month) for year_month in year_month_list):
            raise Exception("there are files which are not directories of year and month of the data")
        start_year_month = year_month_list[0]
        end_year_month = year_month_list[-1]

        start_year_month_dir = os.path.join(l1a_l1b_dir(), start_year_month)
        start_days = sorted(os.listdir(start_year_month_dir))
        if not all(day_format.search(day) for day in start_days):
            raise Exception(f"there are files which are not named as days in {start_year_month}")
        start_day = start_days[0]

        end_year_month_dir = os.path.join(l1a_l1b_dir(), end_year_month)
        end_days = sorted(os.listdir(end_year_month_dir))
        if not all(day_format.search(day) for day in end_days):
            raise Exception(f"there are files which are not named as days in {end_year_month}")
        end_day = end_days[-1]

        valid_hours = ['H00', 'H06', 'H12', 'H18']
        start_hours = sorted(os.listdir(os.path.join(start_year_month_dir, start_day)))
        if not all(hour in valid_hours for hour in start_hours):
            raise Exception(f"there are directories that have incorrect hour names in {start_hours}")
        end_hours = sorted(os.listdir(os.path.join(end_year_month_dir, end_day)))
        if not all(hour in valid_hours for hour in end_hours):
            raise Exception(f"there are directories that have incorrect hour names in {end_hours}")
        start_hour = start_hours[0]
        end_hour = end_hours[-1]

        start_date = f"{start_year_month}-{start_day}"
        end_date = f"{end_year_month}-{end_day}"
    except Exception as ex:
        raise Exception("unable to detect the dates of the simulation") from ex

    # Here we expect to have QGIS correctly put in the path
    if start == Proc.L1A or start == Proc.L1B:
        logger.info("runnning L1B")
        run_processor(
            conf[Conf.L1B_EXE],
            f"{start_date} {end_date}"
        )
        logger.info("runnning L1B_MM")
        run_processor(
            conf[Conf.L1B_MM_EXE],
            f"{start_date} {end_date}"
        )
        logger.info("runnning L1B_CX")
        run_processor(
            conf[Conf.L1B_CX_EXE],
            # f"-P {data_release_dir()} --Log {LOG_LEVELS_IEEC[log_level]}"
            f"--StartDateTime {start_date}T00:00 --StopDateTime {end_date}T23:59"
        )
        logger.info("runnning L1B_CC")
        run_processor(
            conf[Conf.L1B_CC_EXE],
            # f"-P {data_release_dir()}" # Is this done by IEEC too?
            f"--StartDateTime {start_date}T00:00 --StopDateTime {end_date}T23:59"
        )
        logger.info("running L1B_MM again")
        run_processor(
            conf[Conf.L1B_MM_EXE],
            f"{start_date} {end_date}"
        )
        if end == Proc.L1B:
            do_backup_and_pam()
            return

    match end:
        case Proc.L2FT:
            logger.info("running L2FT")
            # This does not support logging options apparently.
            # To decide if repr or oper shall be run the appropriate processor
            # can be selected from the options.
            run_processor(
                conf[Conf.L2FT_EXE],
                f"{start_date} {end_date} ..\\conf\\H1conf_track.txt"
            )
        case Proc.L2FB:
            logger.info("running L2FB")
            run_processor(
                conf[Conf.L2FB_EXE],
                f"{start_date} {end_date} ..\\conf {LOG_LEVELS_IFAC[log_level]}"
            )
        case Proc.L2SM:
            logger.info("running L2SM")
            l2sm_working_dir = os.path.dirname(os.path.dirname(conf[Conf.L2SM_EXE]))
            run_processor(
                conf[Conf.L2SM_EXE],
                # f"-input {l2sm_working_dir} {start_date}T00:00 {end_date}T12:59"
                f"{start_date}T00:00 {end_date}T23:59 ..\\conf\\configuration.cfg"
            )
        case Proc.L2SI:
            logger.info("running L2SI")
            l2si_dir = os.path.join(auxiliary_data_dir, "L2OP-SI")
            run_processor(
                conf[Conf.L2SI_EXE],
                f"--StartDateTime {start_date}T00:00 --StopDateTime {end_date}T23:59"
                # ""
                # f"-P {data_release_dir} -M {l2si_dir} --Log {LOG_LEVELS_IEEC[log_level]}"
            )
        case other:
            assert False

    check_existence_of_netcdf_file(os.path.join(data_release_dir(), PROC_OUTPUT_DIRS[end]))
    do_backup_and_pam()

# TODO: add the name for the file object for better error messages.
def gui(logger: logging.Logger, state_file: typing.TextIO, config_file: typing.TextIO, log_dir: str) -> None:
    """This function creates a user friendly GUI to operate the orchestrator."""

    start: Proc
    end: Proc
    pam: bool
    backup: str

    try:
        state_json = json.load(state_file)

        annotations = inspect.get_annotations(Args)
        keys  = list(annotations.keys())
        types = list(annotations.values())
        del annotations

        for i in range(len(keys)):
            key = keys[i]
            actual_type = type(state_json[key])
            correct_type = types[i]
            if not issubclass(correct_type, actual_type):
                raise TypeError(f"the key {key} has type {actual_type} instead "
                    f"of {correct_type}")

        if len(state_json.keys()) != len(keys):
            logger.warning("the state file has extraneous keys")

        # TODO: clamp start and end.
        start = Proc(state_json["start"])
        end = Proc(state_json["end"])
        pam = state_json["pam"]
        backup = state_json["backup"]
        log_level = state_json["log_level"]

        # We delay all path valitions to the run function, since the default
        # that we give in case of error could also don't exist.

        args: Args = {"start": start, "end": end, "pam": pam, "backup": backup,
            "log_level": log_level}
        if not validate_arguments(args):
            raise ValueError("the state file has an illegal configuration")
        del args
    except (json.JSONDecodeError, KeyError, TypeError, ValueError):
        logger.exception("an error while reading the previous state file, using"
            " the default instead")
        start = Proc(ARGS_DEFAULT["start"])
        end = Proc(ARGS_DEFAULT["end"])
        pam = ARGS_DEFAULT["pam"]
        backup = ARGS_DEFAULT["backup"]
        log_level = ARGS_DEFAULT["log_level"]

    try:
        conf_json = json.load(config_file)

        for option in Conf:
            key = option.name
            actual_type = type(conf_json[key])
            if actual_type != str:
                raise TypeError(f"the key {key} has type {actual_type} instead "
                    f"of {str}")

        if len(conf_json.keys()) != len(Conf):
            logger.warning("the configuration file has extraneous keys")

        # Again we delay the path validation.

        conf = [conf_json[key.name] for key in Conf] # We read only the keys that we need.
    except (json.JSONDecodeError, KeyError, TypeError):
        logger.exception("an error occured while reading the configuration file"
            "using the default one instead")
        conf = CONF_VALUES_DEFAULT

    # Be carefull in the way you create istances of tkinter.Variable. You have
    # to keep a reference to each one of them somewere, either in a function or
    # a class, otherwise they are going to be garbage collected away and you are
    # not going to see for example the default value of comboboxes, and
    # obviously since you have no reference to them you are not going to be able
    # to use them.
    # https://stackoverflow.com/a/66202218

    root = tkinter.Tk()
    root.resizable(False, False)
    root.title("Orchestrator")
    def save_state_and_close() -> None:
        try:
            state_file.truncate(0)
            state_file.seek(0)
            res: Args = {
                "start": Proc[start_var.get()],
                "end": Proc[end_var.get()],
                "pam": pam_var.get(),
                "backup": backup_var.get(),
                "log_level": LogLevel(log_level_combobox.current())
            }
            assert validate_arguments(res)
            logger.info("saving state file")
            state_file.write(json.dumps(res))
        except Exception:
            logger.exception("unable to save the state")
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", save_state_and_close)

    # Settings Toplevel

    settings_toplevel = tkinter.Toplevel(root)
    settings_toplevel.resizable(False, False)
    settings_toplevel.title("Orchestrator - Settings")
    settings_toplevel.protocol("WM_DELETE_WINDOW",
        lambda: settings_toplevel.withdraw() \
            or settings_toplevel.grab_release() # type: ignore
    )
    # Deiconified later to not create this window multiple times.
    settings_toplevel.withdraw()

    settings_frame = tkinter.ttk.Frame(settings_toplevel)
    settings_frame.grid(column=0, row=0, padx=".5c", pady=".5c")

    # NOTE: It would be nice to set initialdir for all the exe_dialog so that it
    #       makes the user select files starting from the proper direcotry. But
    #       it would require a bit of messy code and there is no way to contrain
    #       explorer.exe to a single directory. A possible way to force the user
    #       to select just files in the directories of bin and scripts would be
    #       to create a Listbox dialog that shows only the listing of the
    #       directories bin and scripts. But again this would be messy.

    settings_label_frames = []
    for group in ConfGroup:
        settings_label_frame = tkinter.ttk.LabelFrame(settings_frame,
            text=CONF_GROUP_NAME[group], labelanchor="n")
        settings_label_frames.append(settings_label_frame)
    del settings_label_frame

    settings_label_frames[ConfGroup.IO_DIR].grid(row=0, column=0)
    settings_label_frames[ConfGroup.L1A]   .grid(row=1, column=0)
    settings_label_frames[ConfGroup.L1B]   .grid(row=2, column=0, rowspan=3)
    settings_label_frames[ConfGroup.L2FB]  .grid(row=0, column=1)
    settings_label_frames[ConfGroup.L2FT]  .grid(row=1, column=1)
    settings_label_frames[ConfGroup.L2SI]  .grid(row=2, column=1)
    settings_label_frames[ConfGroup.L2SM]  .grid(row=3, column=1)
    settings_label_frames[ConfGroup.PAM]   .grid(row=4, column=1)

    exe_dialog = lambda option: tkinter.filedialog.askopenfilename(
        parent=settings_toplevel,
        filetypes=[("Executable", "*.exe *.py"),],
        title=CONF_DIALOG_TITLES[option],
        initialdir=os.getenv("HOMEDRIVE", "C:"),
        multiple=False # type: ignore
    ).replace("/", "\\")
    dir_dialog = lambda option: tkinter.filedialog.askdirectory(
        parent=settings_toplevel,
        title=CONF_DIALOG_TITLES[option],
        initialdir=os.getenv("HOMEDRIVE", "C:")
    ).replace("/", "\\")
    conf_vars = []
    # Here the grid layut used are always relative to a LabelFrame. Apparently
    # even though the row number is relative to the loop and not the a
    # LabelFrame everything seems to work fine. To give a concrete example of
    # what I am talking about consider when we put the first widget inside a
    # LabelFrame at, say, iteration n, the widget will be put in row n but it
    # will still show up as the first element in the LabelFrame without any
    # additional space above it.
    for option in Conf:
        i = option
        tkinter.ttk.Label(settings_label_frames[CONF_GROUP[option]], text=CONF_NAMES[i]) \
            .grid(column=0, row=i.value, sticky="w", padx=".1c")
        var = tkinter.StringVar(root, conf[i])
        conf_vars.append(var)
        entry = tkinter.ttk.Entry(settings_label_frames[CONF_GROUP[option]], textvariable=var,
            state="readonly", width=40)
        entry.grid(column=1, row=i.value, padx=".1c")
        entry.xview("end")
        kind = CONF_KINDS[i]
        dialog = exe_dialog if kind == ConfKind.EXE \
            else dir_dialog if kind == ConfKind.DIR \
            else None
        assert dialog is not None, f"The ConfKind enumeration shall contain only EXE and" \
            f" DIR, it has instead {ConfKind.__members__}"
        def closure(var=var, dialog=dialog, entry=entry, option=option):
            res = dialog(option)
            if res:
                nonlocal last_value, last_index
                last_value = var.get()
                last_index = option
                var.set(res)
            entry.xview("end")
        tkinter.ttk.Button(settings_label_frames[CONF_GROUP[option]], text="Browse", command=closure) \
            .grid(column=2, row=i.value)
    del var, entry, kind, dialog
    assert len(conf_vars) == len(Conf)

    # TODO: use collections.deque to have a limited number of undo actions.
    last_value = None
    last_index = None
    def undo_config_change() -> None:
        nonlocal last_value, last_index
        if last_value is not None and last_index is not None:
            logger.info("undoing last change to the configuration")
            conf_vars[last_index].set(last_value)
            last_value = None
            last_index = None
    tkinter.ttk.Button(settings_frame, text="Undo", command=undo_config_change) \
        .grid(column=0, row=i+1, stick="e")

    def save_config():
        res = [
            f'\t"{option.name}": "{_escape_string(conf_vars[option].get())}"'
            for option in Conf
        ]
        res = "{\n" + ",\n".join(res) + "\n}"

        try:
            config_file.truncate(0)
            config_file.seek(0)
            config_file.write(res)
            config_file.flush()
            logger.info("configuration saved")
        except OSError:
            logger.exception("unable to save the configuration file")

    # TODO: instead of using a button I should use a tkinter.Menu with save,
    #       import and export funcitonality.
    tkinter.ttk.Button(settings_frame, text="Save", command=save_config) \
        .grid(column=1, row=i+1, pady=".3c", stick="w")

    # Orchestrator Toplevel

    orchestrator_frame = tkinter.ttk.Frame(root)
    orchestrator_frame.grid(column=0, row=0, padx="1c", pady="1c")

    start_label = tkinter.ttk.Label(orchestrator_frame, text="Start:")
    start_label.grid(column=0, row=0)

    start_var = tkinter.StringVar(root, start.name, "start_var")
    start_combobox = tkinter.ttk.Combobox(
        orchestrator_frame,
        textvariable=start_var,
        values=_enum_members_as_strings(Proc),
        state="readonly"
    )
    # start_combobox.current(0)
    start_combobox.grid(column=1, row=0)

    end_label = tkinter.ttk.Label(orchestrator_frame, text="End:")
    end_label.grid(column=3, row=0)

    end_var = tkinter.StringVar(root, end.name, "end_var")
    end_combobox = tkinter.ttk.Combobox(
        orchestrator_frame,
        textvariable=end_var,
        values=_enum_members_as_strings(Proc),
        state="readonly"
    )
    # end_combobox.current(0)
    end_combobox.grid(column=4, row=0)

    pam_var = tkinter.BooleanVar(root, pam, "pam_var")
    pam_checkbutton = tkinter.ttk.Checkbutton(
        orchestrator_frame,
        text="PAM",
        variable=pam_var,
        onvalue=True,
        offvalue=False
    )
    pam_checkbutton.grid(column=5, row=0)

    backup_dialog = lambda: tkinter.filedialog.askopenfilename(
        parent=root,
        filetypes=[("ZIP Archive", ".zip")],
        initialdir=conf_vars[Conf.BACKUP_DIR].get(),
        title="Select a backup file",
        multiple=False # type: ignore
    ).replace("/", "\\")
    backup_button = tkinter.ttk.Button(
        orchestrator_frame,
        text="Choose backup",
        command=lambda: (
            backup_var.set(backup_dialog()) # type: ignore
            or backup_entry.xview("end"))
    )
    backup_button.grid(column=0, row=1, columnspan=2, pady=".5c", sticky="e")

    backup_var = tkinter.StringVar(root, backup, "backup_var")
    backup_entry = tkinter.ttk.Entry(
        orchestrator_frame,
        textvariable=backup_var,
        state="readonly"
    )
    backup_entry.grid(column=2, row=1, columnspan=3, pady=".5c", sticky="w")

    log_level_label = tkinter.ttk.Label(orchestrator_frame, text="Log Level:")
    log_level_label.grid(column=5, row=1, sticky="s")

    log_level_var = tkinter.StringVar(root, LOG_LEVELS_FOR_DISPLAY[log_level], "log_level_var")
    log_level_combobox = tkinter.ttk.Combobox(
        orchestrator_frame,
        textvariable=log_level_var,
        values=LOG_LEVELS_FOR_DISPLAY,
        state="readonly",
        width=6
    )
    log_level_combobox.grid(column=5, row=2, sticky="n")

    def keep_ui_invariant(name1, name2, op):
        """https://tcl.tk/man/tcl8.5/TclCmd/trace.htm#M14"""
        start = Proc[start_var.get()]
        end = Proc[end_var.get()]

        match name1:
            case "start_var":
                if start <= Proc.L1B:
                    if start > end:
                        end_combobox.current(start.value)
                else:
                    end_combobox.current(start.value)
                if start == Proc.L1A:
                    backup_var.set("")
            case "end_var":
                if end <= Proc.L1B:
                    if start > end:
                        start_combobox.current(end.value)
                else:
                    if start > Proc.L1B:
                        start_combobox.current(end.value)
                if end < Proc.L1B:
                    pam_var.set(False)
            # Both the PAM checkbox and the backup entry should be both cleared
            # and disabled if are not valid to input and enabled otherwise. This
            # is a more crude approach that is slightly simpler to implement.
            case "pam_var":
                if end < Proc.L1B:
                    pam_var.set(False)
            case "backup_var":
                if start == Proc.L1A:
                    backup_var.set("")
            case other:
                assert False

        # TODO: add assertion with validate_arguments
    start_var.trace_add("write", keep_ui_invariant)
    end_var.trace_add("write", keep_ui_invariant)
    pam_var.trace_add("write", keep_ui_invariant)
    backup_var.trace_add("write", keep_ui_invariant)

    def orchestrate_simulation() -> None:
        if Proc[start_var.get()] > Proc.L1A and not backup_var.get():
            should_continue = tkinter.messagebox.askokcancel(
                "Are you sure that you want to to proceed?",
                "If a backup file is not selected, the metadata from the previous "
                "run will be processed."
            )
            if not should_continue:
                return

        conf = [conf_vars[option].get() for option in Conf]

        start_time = time.gmtime()
        start_time_str = time.strftime("%Y%m%d_%H%M%S", start_time)
        pseudo_module_id = f"{start_var.get()}{end_var.get()}"
        logfile_name = f"{pseudo_module_id}_{start_time_str}.log"
        logfile_path = os.path.join(log_dir, logfile_name)
        try:
            file_handler = logging.FileHandler(logfile_path) if os.name == "nt" \
                else logging.NullHandler()
        except Exception as ex:
            logger.exception("unable to create log file for this run")
        run_logger = logging.getLogger(f"{__name__}.run")
        # The log level is setted internally in the run routune.
        # run_logger.setLevel(logging.INFO)
        # If we run multiple simulations from the same window we keep appending
        # file handlers to the same {__name__}.run logger object, therefore we
        # append the log of the new simulation to the old files, which is bad.
        # This happens because we call logging.getLogger() with the same name
        # multiple times and it gives us back always the same logger object.
        while run_logger.handlers:
            run_logger.removeHandler(run_logger.handlers[0])
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s: %(funcName)s: %(message)s")
        )
        run_logger.addHandler(file_handler)

        args: Args = {
            "start": Proc[start_var.get()],
            "end": Proc[end_var.get()],
            "pam": pam_var.get(),
            "backup": backup_var.get(),
            "log_level": LogLevel(log_level_combobox.current()),
        }
        try:
            run(
                logger=run_logger,
                args=args,
                conf=conf
            )
        except Exception as ex:
            run_logger.exception("the orchestration encoutered a problem")
            logger.error("the orchestration terminated baddly")

        # Closing the window to see if this solves the misterious bug that is
        # related to deleting the DataRelease direcotry.
        save_state_and_close()

    run_button = tkinter.ttk.Button(
        orchestrator_frame,
        text="Run!",
        command=orchestrate_simulation
    )
    run_button.grid(column=0, row=2, columnspan=2)

    settings_button = tkinter.ttk.Button(
        orchestrator_frame,
        text="Settings",
        command=lambda: settings_toplevel.deiconify() \
            or settings_toplevel.grab_set() # type: ignore
    )
    settings_button.grid(column=3, row=2, columnspan=2)

    root.mainloop()

def _main() -> int:
    if os.name != "nt":
        print("os not supported, some things are not going to work but the GUI "
            "will show up", file=sys.stderr)

    home_drive = os.getenv("HOMEDRIVE", "C:")
    local_appdata = os.getenv("LOCALAPPDATA", "C:")
    orchestrator_appdata = os.path.join(local_appdata,
        "Tor Vergata\\HydroGNSS Orchestrator")
    config_path = os.path.join(orchestrator_appdata, "conf.json")
    state_path = os.path.join(orchestrator_appdata, "state.json")

    config_file: typing.TextIO
    state_file: typing.TextIO
    if os.name != "nt":
        conf_default = dict(zip(_enum_members_as_strings(Conf), CONF_VALUES_DEFAULT))
        config_file = io.StringIO(json.dumps(conf_default))
        state_file = io.StringIO(json.dumps(ARGS_DEFAULT))
    else:
        try:
            os.makedirs(orchestrator_appdata, exist_ok=True)

            config_file = os.fdopen(os.open(config_path, os.O_RDWR | os.O_CREAT), 'rt+')
            state_file = os.fdopen(os.open(state_path, os.O_RDWR | os.O_CREAT), 'rt+')
        except Exception as ex:
            # Here we could also just operate from memory as a fallback, but if
            # we can't create/open files we may have a bigger problem, therefore
            # we just stop the execution here.
            raise Exception("unable to create a necessary file or directory for"
                "the orchestrator") from ex

    log_dir = "..\\log"
    if not os.path.exists(log_dir) and os.name == "nt":
        print("the orchestrator was not launched from the correct working "
            "directory, it did not found the ..\\log directory",
            file=sys.stderr)
        return 1

    formatter = logging.Formatter("%(levelname)s:%(funcName)s %(message)s")
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)
    logger = logging.getLogger(__name__)

    # NOTE: should I add support for CLI? also a --version flag?
    # TODO: find a way to install the files the first time we run the
    #       orchestrator that does not involve a bunch of errors like now.

    try:
        gui(logger, state_file, config_file, log_dir)
    except Exception as ex:
        raise Exception("unable to create the GUI") from ex

    return 0

if __name__ == '__main__':
    raise SystemExit(_main())
