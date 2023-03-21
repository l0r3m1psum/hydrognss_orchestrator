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
"""

# TODO: add a VERSION global so that it can be displayed in the window.

import enum
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
    L2SM = enum.auto() # Soil Mosture

# The PAM (Performance Assesment Module) expects the names with this format.
PROC_NAMES_PAM = ["L1_A", "L1_B", "L2_FB", "L2_FT", "L2_SI", "L2_SM",]
assert len(Proc) == len(PROC_NAMES_PAM)

# Configuration of the variuous processors #####################################
# Here we define a big table (the lists here defined are its rows) with all the
# usefull information about the paths that are neede by the various processors.

class Conf(enum.IntEnum):
    """All the paths that can be configured. The name in the enumaration is also
    the key in the JSON object used for serialization."""
    BACKUP_DIR      = 0
    DATA_DIR        = enum.auto()
    L1A_EXE         = enum.auto()
    L1A_WORK_DIR    = enum.auto()
    L1B_EXE         = enum.auto()
    L1B_WORK_DIR    = enum.auto()
    L1B_MM_EXE      = enum.auto()
    L1B_MM_WORK_DIR = enum.auto()
    L1B_CX_EXE      = enum.auto()
    L1B_CX_WORK_DIR = enum.auto()
    L1B_CC_EXE      = enum.auto()
    L1B_CC_WORK_DIR = enum.auto()
    L2FB_EXE        = enum.auto()
    L2FB_WORK_DIR   = enum.auto()
    L2FT_EXE        = enum.auto()
    L2FT_WORK_DIR   = enum.auto()
    L2SI_EXE        = enum.auto()
    L2SI_WORK_DIR   = enum.auto()
    L2SM_EXE        = enum.auto()
    L2SM_WORK_DIR   = enum.auto()
    PAM_EXE         = enum.auto()
    PAM_WORK_DIR    = enum.auto()

class ConfKind(enum.Enum):
    """Which kind of path to expect in the configuration option."""
    EXE = enum.auto()
    DIR = enum.auto()

# Names of the configuration options to be displayed in the GUI.
CONF_NAMES = [
    "Backup Directory",
    "Data Directory",
    "L1A Executable",
    "L1A Working Dir.",
    "L1B Executable",
    "L1B Working Dir.",
    "L1BMM Executable",
    "L1BMM Working Dir.",
    "L1BCX Executable",
    "L1BCX Working Dir.",
    "L1BCC Executable",
    "L1BCC Working Dir.",
    "L2FB Executable",
    "L2FB Working Dir.",
    "L2FT Executable",
    "L2FT Working Dir.",
    "L2SI Executable",
    "L2SI Working Dir.",
    "L2SM Executable",
    "L2SM Working Dir.",
    "PAM Executable",
    "PAM Working Dir.",
]
assert len(CONF_NAMES) == len(Conf)

# What kind of path the configuration options want.
CONF_KINDS = [
    ConfKind.DIR,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
    ConfKind.EXE,
    ConfKind.DIR,
]
assert len(CONF_KINDS) == len(Conf)

CONF_VALUES_DEFAULT = [
    "C:\\E2ES_backups",
    "C:\\PDGS_NAS_folder",
    "C:\\L1A\\bin\\HSAVERS.exe",
    "C:\\L1A\\bin",
    "C:\\L1BOP\\scripts\\Run_L1b_Processor_with_dates.py",
    "C:\\L1BOP",
    "C:\\L1OP-MM\\scripts\\Run_L1Merge_with_dates.py",
    "C:\\L1OP-MM",
    "C:\\L2OP-SI\\bin\\L1B_CX_DR.exe",
    "C:\\L2OP-SI\\bin",
    "C:\\L2OP-SI\\bin\\L1B_CC_DR.exe",
    "C:\\L2OP-SI\\bin",
    "C:\\L2OP-FB\\bin\\L2OP_FB.exe",
    "C:\\L2OP-FB\\bin",
    "C:\\L2OP-FT\\bin\\L2PPFT_mainscript.exe",
    "C:\\L2OP-FT\\bin",
    "C:\\L2OP-SI\\bin\\L2OP_SI_DR.exe",
    "C:\\L2OP-SI\\bin",
    "C:\\L2OP-SSM\\bin\\SML2OP_start.exe",
    "C:\\L2OP-SSM",
    "C:\\PAM\\bin\\PAM_start.exe",
    "C:\\PAM",
]
assert len(CONF_VALUES_DEFAULT) == len(Conf)

CONF_DIALOG_TITLES = [
    "Choose the backup directory",
    "Choose the main input output directory",
    "Choose the L1A executable",
    "Choose the L1A working directory",
    "Choose the L1B executable",
    "Choose the L1B working directory",
    "Choose the L1B merge module executable",
    "Choose the L1B merge module working directory",
    "Choose the L1B CX executable",
    "Choose the L1B CX working directory",
    "Choose the L1B CC executable",
    "Choose the L1B CC working directory",
    "Choose the L2FB executable",
    "Choose the L2FB working directory",
    "Choose the L2FT executable",
    "Choose the L2FT working directory",
    "Choose the L2SI executable",
    "Choose the L2SI working directory",
    "Choose the L2SM executable",
    "Choose the L2SM working directory",
    "Choose the PAM executable",
    "Choose the PAM working directory",
]
assert len(CONF_DIALOG_TITLES) == len(Conf)

PROCESSORS_SUBDIRS = [
    "bin", "conf", "doc", "log", "scripts", "src", "temp", "tests",
]

# This are the subdirectories that must be in each directory of the
# configuration options.
CONF_SUBDIRS: list[typing.Optional[list[str]]] = [
    [],
    ["Auxiliary_Data", "ConfigurationFiles", "DataRelease"],
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
    None,
    [], # PROCESSORS_SUBDIRS,
]
assert len(CONF_SUBDIRS) == len(Conf)
assert all(
    iff(subdirs is None, kind == ConfKind.EXE)
    for subdirs, kind in zip(CONF_SUBDIRS, CONF_KINDS)
), "subdir is not different from None iff kind is not EXE"
assert all(
    iff(type(subdirs) == list, kind == ConfKind.DIR)
    for subdirs, kind in zip(CONF_SUBDIRS, CONF_KINDS)
), "subdir is not a list iff kind is DIR"

# Arguments ####################################################################

class Args(typing.TypedDict):
    """The arguments needed to run the orchestration. Not all combination of
    arguments are valid."""
    start: Proc
    end: Proc
    pam: bool
    backup: str

ARGS_DEFAULT: Args = {
    "start": Proc.L1A,
    "end": Proc.L1A,
    "pam": False,
    "backup": "",
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

def run(logger: logging.Logger, args: Args, conf: list[str]) -> None:
    """If anything goes wrong this function throws an exception with an
    explenation of what went wrong."""

    assert validate_arguments(args)
    assert len(conf) == len(Conf)

    if os.name != "nt":
        logger.info("skipping the run because we are not on windows")
        return

    # TODO: check that all path in conf exist and are of the right kind
    # TODO: check that if it is truthy backup should be a path to an existing .zip

    for option in Conf:
        subdirs = CONF_SUBDIRS[option]
        if not subdirs:
            continue
        for subdir in subdirs:
            assert CONF_KINDS[option] == ConfKind.DIR
            subdir_path = os.path.join(conf[option], subdir)
            if not os.path.exists(subdir_path):
                logger.warning(f"{conf[option]} does not contain {subdir} as a "
                    f"directory")

    data_dir = conf[Conf.DATA_DIR]
    data_release_dir = os.path.join(data_dir, "DataRelease")
    auxiliary_data_dir = os.path.join(data_dir, "Auxiliary_Data")

    start = args["start"]
    end = args["end"]
    pam = args["pam"]
    backup = args["backup"]
    should_clean = start == Proc.L1A or backup

    # This is used later to create the backup name and to give input to the PAM
    # and it is set either when loading a backup or when running HSAVERS.
    experiment_name = None

    def run_processor(working_dir: str, file_path: str, arguments: str) -> None:
        exe = file_path if file_path.endswith(".exe") \
            else f"py {file_path}" if file_path.endswith(".py") \
            else None

        if exe is None:
            raise Exception(f"only python and exe files are supported, "
                f"{file_path} is not supported")

        # We expect %COMSPEC% to be cmd.exe or something like that.
        try:
            # NOTE: should I worry about 'universal_newlines'?

            with subprocess.Popen(
                args=f"{exe} {arguments}",
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                cwd=working_dir,
                text=True
                ) as p:
                assert p.stdout is not None # Just for mypy.
                for line in p.stdout:
                    # TODO: do something sensible for lines that end with just \r
                    logger.info(line.rstrip())

                if p.wait() != 0:
                    raise Exception(f"{file_path} exited with error code {p.returncode}")
        except Exception as ex:
            raise Exception(f"something went wrong during the execution of "
                f"{file_path}") from ex

    def do_backup_and_pam() -> None:
        timestamp = f"{int(time.time())}"
        assert len(timestamp) == 10
        assert experiment_name
        backup_name = f"{experiment_name}_{timestamp}"
        backup_path_noext = os.path.join(conf[Conf.BACKUP_DIR], backup_name)
        logger.info("doing the backup")
        try:
            shutil.make_archive(backup_path_noext, "zip", data_release_dir)
        except Exception as ex:
            raise Exception("unable to make backup archive") from ex
        if pam:
            logger.info("running the PAM")
            run_processor(
                conf[Conf.PAM_WORK_DIR],
                conf[Conf.PAM_EXE],
                f"{PROC_NAMES_PAM[end]} {auxiliary_data_dir} "
                f"{conf[Conf.BACKUP_DIR]} {backup_name}"
            )

            pam_output = os.path.join(conf[Conf.BACKUP_DIR], "PAM_Output")
            try:
                with zipfile.ZipFile(f"{backup_path_noext}.zip", 'a') as zipf:
                    for file in os.listdir(pam_output):
                        file_path = os.path.join(pam_output, file)
                        zipf.write(file_path, f"PAM_Output\\{file}")
            except Exception as ex:
                raise Exception("unable to add the PAM output figures to the "
                    "backup") from ex
            try:
                shutil.rmtree(pam_output)
            except Exception as ex:
                raise Exception("unable to delete {pam_output}") from ex
        logger.info("orchestration finished")
        print("\a", end='')

    if should_clean:
        logger.info("cleaning up from previous execution")
        if os.path.exists(data_release_dir):
            shutil.rmtree(data_release_dir)
        try:
            os.mkdir(data_release_dir)
            os.mkdir(os.path.join(data_release_dir, "L1A_L1B"))
            os.mkdir(os.path.join(data_release_dir, "L2OP-FB"))
            os.mkdir(os.path.join(data_release_dir, "L2OP-FT"))
            os.mkdir(os.path.join(data_release_dir, "L2OP-SI"))
            os.mkdir(os.path.join(data_release_dir, "L2OP-SSM"))
            os.mkdir(os.path.join(data_release_dir, "L1A-SW-RX"))
            os.mkdir(os.path.join(data_release_dir, "L2-FDI"))
        except Exception as ex:
            raise Exception("unable to create the directory structure") from ex
    else:
        try:
            with open(os.path.join(data_release_dir, "experiment_name.txt")) as f:
                experiment_name = f.read().strip() # TODO: validate
        except Exception as ex:
            raise Exception("unable to read the experiment name from the file") from ex
        logger.info("keeping the data release directory of the previous execution")

    if backup:
        assert should_clean
        backup_name_format = re.compile("_[0-9]{10}\.zip$")
        experiment_name = backup_name_format.sub("", backup).split("\\")[-1]
        if experiment_name == backup:
            raise Exception("invalud backup file selected")
        logger.info("loading the backup")
        # TODO: do a partial validation of the contents of the archive like the
        #       firts level of directories in data_release_dir (ZipFile.getinfo()).
        try:
            shutil.unpack_archive(backup, data_release_dir)
        except Exception as ex:
            raise Exception("unable to extract the backup") from ex

    # The actual "orchestration" starts here.

    if start == Proc.L1A:
        logger.info("runnning L1A")
        run_processor(
            conf[Conf.L1A_WORK_DIR],
            conf[Conf.L1A_EXE],
            ""
        )

        l1a_output_file = os.path.join(
            conf[Conf.L1A_WORK_DIR],
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

        experiment_name_format = re.compile("_[0-9]{2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-[0-9]{4}_[0-9]{2}_[0-9]{2}_[0-9]{2}$")
        experiment_name = list(filter(None, l1a_out.split("\\")))[-1]
        if not experiment_name_format.search(experiment_name):
            raise Exception("the L1A output directory has not the correct format")

        # This is needed for when not should_clean, so that the PAM can read the
        # appropriate file from the PAM directory in the backup folder.
        try:
            with open(os.path.join(data_release_dir, "experiment_name.txt"), 'w') as f:
                f.write(experiment_name)
        except Exception as ex:
            raise Exception("unable to write the experiment name in the file") from ex

        l1a_out_dir = os.path.join(l1a_out, "DataRelease\L1A_L1B")
        try:
            shutil.copytree(l1a_out_dir, os.path.join(data_release_dir, "L1A_L1B"), dirs_exist_ok=True)
        except Exception as ex:
            raise Exception("unable to copy {l1a_out_dir} to "
                "{data_release_dir}") from ex

        # The last 21 characters are the ones of the timestamp.
        l1a_file_for_pam = os.path.join(l1a_out,
            f"{experiment_name[:-21]}_inOutReferenceFile.mat")

        try:
            # This code is commented-out because it was needed before but now
            # is not. We keep it arround just in case something has to change
            # back...
            # shutil.copy2(l1a_file_for_pam, os.path.join(conf[Conf.BACKUP_DIR],
            #     f"PAM\\{experiment_name}.mat"))
            shutil.copy2(l1a_file_for_pam, data_release_dir)
        except Exception as ex:
            raise Exception("unable to copy files for the PAM") from ex

        if end == Proc.L1A:
            do_backup_and_pam()
            return

    assert experiment_name, "This variable should have been assigned by now"

    logger.info("detecting the dates of the simulation")
    try:
        year_month_format = re.compile("^[0-9]{4}-[0-9]{2}$")
        day_format = re.compile("^[0-9]{2}$")
        l1a_l1b_dir = os.path.join(data_release_dir, "L1A_L1B")

        year_month_list = sorted(os.listdir(l1a_l1b_dir))
        if not all(year_month_format.search(year_month) for year_month in year_month_list):
            raise Exception("there are files which are not directories of year and month of the data")
        start_year_month = year_month_list[0]
        end_year_month = year_month_list[-1]

        start_days = sorted(os.listdir(os.path.join(l1a_l1b_dir, start_year_month)))
        if not all(day_format.search(day) for day in start_days):
            raise Exception("there are files which are not named as days in {start_year_month}")
        start_day = start_days[0]

        end_days = sorted(os.listdir(os.path.join(l1a_l1b_dir, end_year_month)))
        if not all(day_format.search(day) for day in end_days):
            raise Exception(f"there are files which are not named as days in {end_year_month}")
        end_day = end_days[-1]

        start_date = f"{start_year_month}-{start_day}"
        end_date = f"{end_year_month}-{end_day}"
    except Exception as ex:
        raise Exception("unable to detect the dates of the simulation") from ex

    # Here we expect to have QGIS correctly put in the path
    if start == Proc.L1A or start == Proc.L1B:
        logger.info("runnning L1B")
        run_processor(
            conf[Conf.L1B_WORK_DIR],
            conf[Conf.L1B_EXE],
            f"{start_date} {end_date}"
        )
        logger.info("runnning L1B_MM")
        run_processor(
            conf[Conf.L1B_MM_WORK_DIR],
            conf[Conf.L1B_MM_EXE],
            f"{start_date} {end_date}"
        )
        logger.info("runnning L1B_CX")
        run_processor(
            conf[Conf.L1B_CX_WORK_DIR],
            conf[Conf.L1B_CX_EXE],
            f"-P {data_release_dir}"
        )
        logger.info("runnning L1B_CC")
        try:
            run_processor(
                conf[Conf.L1B_CC_WORK_DIR],
                conf[Conf.L1B_CC_EXE],
                f"-P {data_release_dir}"
            )
        except Exception:
            logger.info("this processor failed but we allow the orchestrator to "
                "contine the execution as Gabrielle asked.")
        logger.info("runnning L1B_MM again")
        run_processor(
            conf[Conf.L1B_MM_WORK_DIR],
            conf[Conf.L1B_MM_EXE],
            f"{start_date} {end_date}"
        )
        if end == Proc.L1B:
            do_backup_and_pam()
            return

    match end:
        case Proc.L2FT:
            logger.info("runnning L2FT")
            run_processor(
                conf[Conf.L2FT_WORK_DIR],
                conf[Conf.L2FT_EXE],
                f"{start_date} {end_date}"
            )
            do_backup_and_pam()
            return
        case Proc.L2FB:
            logger.info("runnning L2FB")
            run_processor(
                conf[Conf.L2FB_WORK_DIR],
                conf[Conf.L2FB_EXE],
                f"{start_date} {end_date} {data_dir} yes"
            )
            do_backup_and_pam()
            return
        case Proc.L2SM:
            logger.info("runnning L2SM")
            run_processor(
                conf[Conf.L2SM_WORK_DIR],
                conf[Conf.L2SM_EXE],
                f"-input {data_dir} {start_date} {end_date} 1 25 L1 L"
            )
            do_backup_and_pam()
            return
        case Proc.L2SI:
            logger.info("runnning L2SI")
            l2si_dir = os.path.join(auxiliary_data_dir, "L2OP-SI")
            run_processor(
                conf[Conf.L2SI_WORK_DIR],
                conf[Conf.L2SI_EXE],
                f"-P {data_release_dir} -M {l2si_dir}"
            )
            do_backup_and_pam()
            return
        case other:
            assert False

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

        # We delay all path valitions to the run function, since the default
        # that we give in case of error could also don't exist.

        args: Args = {"start": start, "end": end, "pam": pam, "backup": backup}
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

    try:
        conf_json = json.load(config_file)

        for option in Conf:
            key = option.name
            actual_type = type(conf_json[key])
            if actual_type != str:
                raise TypeError(f"the key {key} has type {actual_type} instead "
                    f"of {str}")

        if len(conf_json.keys()) != len(Conf):
            breakpoint()
            logger.warning("the configuration file has extraneous keys")

        # Again we delay the path validation.

        conf = list(conf_json.values())
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
    def save_state() -> None:
        try:
            state_file.truncate(0)
            state_file.seek(0)
            res: Args = {
                "start": Proc[start_var.get()],
                "end": Proc[end_var.get()],
                "pam": pam_var.get(),
                "backup": backup_var.get(),
            }
            assert validate_arguments(res)
            logger.info("saving state file")
            state_file.write(json.dumps(res))
        except Exception:
            logger.exception("unable to save the state")
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", save_state)

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

    # TODO: use tkinter.ttk.LabelFrame as Leila said
    # NOTE: It would be nice to set initialdir for all the exe_dialog so that it
    #       makes the user select files starting from the proper direcotry. But
    #       it would require a bit of messy code and there is no way to contrain
    #       explorer.exe to a single directory. A possible way to force the user
    #       to select just files in the directories of bin and scripts would be
    #       to create a Listbox dialog that shows only the listing of the
    #       directories bin and scripts. But again this would be messy.

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
    for option in Conf:
        i = option
        tkinter.ttk.Label(settings_frame, text=CONF_NAMES[i]) \
            .grid(column=0, row=i.value, sticky="w", padx=".1c")
        var = tkinter.StringVar(root, conf[i])
        conf_vars.append(var)
        entry = tkinter.ttk.Entry(settings_frame, textvariable=var,
            state="readonly", width=40)
        entry.grid(column=1, row=i.value, padx=".1c")
        entry.xview("end")
        kind = CONF_KINDS[i]
        dialog = exe_dialog if kind == ConfKind.EXE \
            else dir_dialog if kind == ConfKind.DIR \
            else None
        assert dialog, f"The ConfKind enumeration shall contain only EXE and" \
            f" DIR, it has instead {ConfKind.__members__}"
        def closure(var=var, dialog=dialog, entry=entry, option=option):
            res = dialog(option)
            if res:
                var.set(res)
            entry.xview("end")
        tkinter.ttk.Button(settings_frame, text="Browse", command=closure) \
            .grid(column=2, row=i.value)
    del var, entry, kind, dialog
    assert len(conf_vars) == len(Conf)

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
            logger.info("configuration saved")
        except OSError:
            logger.exception("unable to save the configuration file")

    # TODO: instead of using a button I should use a tkinter.Menu with save,
    #       import and export funcitonality.
    save_button = tkinter.ttk.Button(settings_frame, text="Save",
        command=save_config).grid(column=2, row=i+1, pady=".3c")

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
                "run will be processed"
            )
            if not should_continue:
                return

        conf = [conf_vars[option].get() for option in Conf]

        start_time = time.gmtime()
        start_time_str = time.strftime("%H_%M_%S %d-%m-%Y", start_time)
        logfile_name = f"run from {start_var.get()} to {end_var.get()} at {start_time_str}.txt"
        logfile_path = os.path.join(log_dir, logfile_name)
        # TODO: add try except here.
        file_handler = logging.FileHandler(logfile_path) if os.name == "nt" \
            else logging.NullHandler()
        run_logger = logging.getLogger(f"{__name__}.run")
        run_logger.setLevel(logging.INFO)
        run_logger.addHandler(file_handler)
        # TODO: add formatter.

        args: Args = {
            "start": Proc[start_var.get()],
            "end": Proc[end_var.get()],
            "pam": pam_var.get(),
            "backup": backup_var.get(),
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
