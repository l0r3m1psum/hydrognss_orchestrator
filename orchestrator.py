"""This module contains the code for the GUI and the logic to operate and run
the orchestrator. This two functionalities are provided in the only three
exported functions i.e. gui(), run() and read_or_create_config_file().

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

import enum
import idlelib.tooltip # type: ignore
import json
import os
import re
import shutil
import sys
import time
import tkinter
import tkinter.filedialog
import tkinter.ttk
import traceback
import typing

# We do not know if this is really needed for high DPI screens.
# import ctypes
# ctypes.windll.shcore.SetProcessDpiAwareness(1)

# The processors that the orchestrator manages.
class Proc(enum.IntEnum):
    L1A  = 0           # HSAVERS
    L1B  = enum.auto() # ???
    L2FB = enum.auto() # Forest Biomass
    L2FT = enum.auto() # Freeze/Thaw state
    L2SI = enum.auto() # Surface Inundation
    L2SM = enum.auto() # Soil Mosture

# All the options that can be configured.
class Conf(enum.IntEnum):
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

# Which kind of path to expect in the configuration option.
class ConfKind(enum.Enum):
    EXE = enum.auto()
    DIR = enum.auto()

# Just for convenience.
PROC_NAMES = list(Proc.__members__)
# Since the PAM (Performance Assesment Module) expects the names in this way.
PROC_NAMES_PAM = ["L1_A", "L1_B", "L2_FB", "L2_FT", "L2_SI", "L2_SM",]
assert len(Proc) == len(PROC_NAMES_PAM)

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
    "C:\\PDGS_NAS_Folder",
    "C:\\L1A\\bin\\HSAVERS.exe",
    "C:\\L1A\\bin",
    "C:\\L1BOP\\scripts\\Run_L1b_Processor_with_dates.py",
    "C:\\L1BOP\\scripts",
    "C:\\L1OP-MM\\scripts\\Run_L1Merge_with_dates.py",
    "C:\\L1OP-MM\\scripts",
    "C:\\L1OP-CX\\bin\\L1B_CX_DR.exe",
    "C:\\L1OP-CX\\bin",
    "C:\\L1OP-CC\\bin\\L1B_CC_DR.exe",
    "C:\\L1OP-CC\\bin",
    "C:\\L2FB\\bin\\L2OP_FB.exe",
    "C:\\L2FB\\bin",
    "C:\\L2FT\\bin\\L2PPFT_mainscript.exe",
    "C:\\L2FT\\bin",
    "C:\\L2OP-SI\\bin\\L2OP_SI_DR.exe",
    "C:\\L2OP-SI\\bin",
    "C:\\L2OP-SSM\\bin\\SML2OP_start.exe",
    "C:\\L2OP-SSM",
    "C:\\PAM\\bin\\PAM_start.exe",
    "C:\\PAM\\",
]
assert len(CONF_VALUES_DEFAULT) == len(Conf)

# TODO: add a list for the processors' dialog titles.

PROCESSORS_SUBDIRS = [
    "bin", "conf", "doc", "log", "scripts", "src", "temp", "tests",
]

# This are the subdirectories that must be in each directory of the
# configuration options.
CONF_SUBDIRS: list[typing.Optional[list[str]]] = [
    ["PAM", "PAM_Output"],
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
# A iff B = A and B or not A and not B
# TODO: iff can be represented with bool(A) == bool(B)
assert all(
    subdirs is None and kind == ConfKind.EXE
    or subdirs is not None and kind != ConfKind.EXE
    for subdirs, kind in zip(CONF_SUBDIRS, CONF_KINDS)
), "subdir is not different from None iff kind is not EXE"
assert all(
    type(subdirs) == list and kind == ConfKind.DIR
    or type(subdirs) != list and kind != ConfKind.DIR
    for subdirs, kind in zip(CONF_SUBDIRS, CONF_KINDS)
), "subdir is not a list iff kind is DIR"

# %LOCALAPPDATA% can be modified for just this program by running python in the
# following way: cmd /V /C "set LOCALAPPDATA=... && py ..."
config_options_file_path = os.path.expandvars(os.path.join(
    "%LOCALAPPDATA%", "HydroGNSS Orchestrator\\config.json"
))

def _escape_str(s: str) -> str:
    # f"{s!r}"[2:-2]
    return s.encode("unicode_escape").decode("utf-8")

# TODO: In case a path is not correct we should use the empty string
def read_or_create_config_file() -> typing.Optional[list[str]]:
    """As the name suggests this function reads the configuration file (or
    creates it if it does not exists) and then return it to you. If None is
    returned because an error occurred, you can just copy the
    CONF_VALUES_DEFAULT and use that as the configuration."""

    if os.name != "nt":
        print("skipping the configuration file read/creation because we are not"
            " on windows", file=sys.stderr)
        return None

    os.makedirs(os.path.dirname(config_options_file_path), exist_ok=True)

    if os.path.isfile(config_options_file_path):
        try:
            with open(config_options_file_path) as f:
                res = json.load(f)

                config_keys = list(Conf.__members__)
                res_keys = res.keys()
                if not set(res_keys) == set(config_keys):
                    print(f"bad config file, the keys shall be "
                        f"{sorted(config_keys)} and are {sorted(res_keys)} "
                        f"instead, loading default config instead",
                        file=sys.stderr)
                    return None

                # TODO: here I should change just the ones that don't exist.
                if not all(os.path.exists(value) for value in res.values()):
                    print("all the values is the config file shall be existing "
                        "paths, loading the default config instead",
                        file=sys.stderr)
                    return None

                return [res[option.name] for option in Conf]

        except json.JSONDecodeError:
            print("invalid json in configuration file, loading the default one "
                "instead", file=sys.stderr)
            return None
        except OSError:
            print("error while opening the config file, loading the default one"
                " instead", file=sys.stderr)
            return None
    else:
        print("configuration file not found creating the default one",
            file=sys.stderr)

        res = [
            f'\t"{option.name}": "{_escape_str(CONF_VALUES_DEFAULT[option])}"'
            for option in Conf
        ]
        res = "{\n" + ",\n".join(res) + "\n}"

        try:
            with open(config_options_file_path, "w") as f:
                f.write(res)
        except OSError:
            print("unable to create the configuration file", file=sys.stderr)
            return None

        return CONF_VALUES_DEFAULT[:]

    return True

def run(start: Proc, end: Proc, pam: bool, clean: bool, backup: str, conf: list[str]) -> None:
    """If anything goes wrong this function throws an exception with an
    explenation of what went wrong."""

    assert start <= end
    # Logical implication i.e. (A -> B) is equivalent to (not A or B).
    assert not pam or end > Proc.L1B, "if pam is enabled then the processor should one of the L2"
    # TODO: check that start != L1A iff not clean or backup.
    assert not backup or start != Proc.L1A, "if a backup file is to be restored then the starting processor should not be L1A"
    assert not clean or not backup, "if clean is enabled then no backup file should be selected"
    assert not backup or clean, "if a backup file has been specified then clean should be enable"
    assert not (start > Proc.L1B and end > Proc.L1B) or start == end
    assert len(conf) == len(Conf)

    if os.name != "nt":
        print("skipping the run because we are not on windows", file=sys.stderr)
        return

    # TODO: put all check here so that the UI does not have to be so strict
    #       about many things.

    for option in Conf:
        subdirs = CONF_SUBDIRS[option]
        if not subdirs:
            continue
        for subdir in subdirs:
            assert CONF_KINDS[option] == ConfKind.DIR
            subdir_path = os.path.join(conf[option], subdir)
            if not os.path.exists(subdir_path):
                # NOTE: Should I use an actual logger at this point.
                print(f"warning: {conf[option]} does not contain {subdir} as a "
                    f"directory", file=sys.stderr)

    data_dir = conf[Conf.DATA_DIR]
    data_release_dir = os.path.join(data_dir, "DataRelease")
    auxiliary_data_dir = os.path.join(data_dir, "Auxiliary_Data")

    # This is used later to create the backup name and to give input to the PAM
    # and it is set either when loading a backup or when running HSAVERS.
    experiment_name = None

    def run_processor(working_dir: str, file_path: str, arguments: str) -> None:
        original_working_dir = os.getcwd()
        try:
            os.chdir(working_dir)
        except OSError as ex:
            raise Exception(f"unable to move to {working_dir} for {file_path}") \
                from ex

        exe = file_path if file_path.endswith(".exe") \
            else f"py {file_path}" if file_path.endswith(".py") \
            else None

        if exe is None:
            raise Exception(f"only python and exe files are supported, "
                f"{file_path} is not supported")

        # We expect %COMSPEC% to be cmd.exe or something like that.
        # TODO: use subprocess module and log output to file
        res = os.system(f"{exe} {arguments}")
        if res != 0:
             raise Exception(f"{file_path} exited with error code {res}")

        try:
            os.chdir(original_working_dir)
        except OSError as ex:
            raise Exception(f"unable to go back to {original_working_dir} for "
                f"{file_path}") from ex

    def do_backup_and_pam():
        timestamp = f"{int(time.time())}"
        assert len(timestamp) == 10
        assert experiment_name
        backup_name = f"{experiment_name}_{timestamp}"
        print("doing the backup")
        try:
            shutil.make_archive(
                os.path.join(conf[Conf.BACKUP_DIR], backup_name),
                "zip", data_release_dir)
        except Exception as ex:
            raise Exception("unable to make backup archive") from ex
        if pam:
            print("running the PAM")
            run_processor(
                conf[Conf.PAM_WORK_DIR],
                conf[Conf.PAM_EXE],
                f"{PROC_NAMES_PAM[end]} {auxiliary_data_dir} "
                f"{conf[Conf.BACKUP_DIR]} {backup_name}"
            )
        print("orchestration finished\a")

    if clean:
        print("cleaning up from previous execution")
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
        print("keeping the data release direcotory of the previous execution")

    if backup:
        backup_name_format = re.compile("_[0-9]{10}\.zip$")
        experiment_name = backup_name_format.sub("", backup).split("\\")[-1]
        if experiment_name == backup:
            raise Exception("invalud backup file selected")
        print("loading the backup")
        # TODO: do a partial validation of the contents of the archive like the
        #       firts level of directories in data_release_dir (ZipFile.getinfo()).
        try:
            shutil.unpack_archive(backup, data_release_dir)
        except Exception as ex:
            raise Exception("unable to extract the backup") from ex

    # The actual "orchestration" starts here.

    if start == Proc.L1A:
        print("runnning L1A")
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
            raise Exception("the L1A output direcotory has not the correct format")

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
            shutil.copy2(l1a_file_for_pam, os.path.join(conf[Conf.BACKUP_DIR],
                f"PAM\\{experiment_name}.mat"))
            shutil.copy2(l1a_file_for_pam, data_release_dir)
        except Exception as ex:
            raise Exception("unable to copy files for the PAM") from ex

        if end == Proc.L1A:
            do_backup_and_pam()
            return

    assert experiment_name, "This variable should have been assigned by now"

    print("detecting the dates of the simulation")
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
        print("runnning L1B")
        run_processor(
            conf[Conf.L1B_WORK_DIR],
            conf[Conf.L1B_EXE],
            f"{start_date} {end_date}"
        )
        print("runnning L1B_MM")
        run_processor(
            conf[Conf.L1B_MM_WORK_DIR],
            conf[Conf.L1B_MM_EXE],
            f"{start_date} {end_date}"
        )
        print("runnning L1B_CX")
        run_processor(
            conf[Conf.L1B_CX_WORK_DIR],
            conf[Conf.L1B_CX_EXE],
            f"-P {data_release_dir}"
        )
        print("runnning L1B_CC")
        try:
            run_processor(
                conf[Conf.L1B_CC_WORK_DIR],
                conf[Conf.L1B_CC_EXE],
                f"-P {data_release_dir}"
            )
        except Exception:
            print("this processor failed but we allow the orchestrator to "
                "contine the execution as Gabrielle asked.")
        print("runnning L1B_MM again")
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
            print("runnning L2FT")
            run_processor(
                conf[Conf.L2FT_WORK_DIR],
                conf[Conf.L2FT_EXE],
                f"{start_date} {end_date}"
            )
            do_backup_and_pam()
            return
        case Proc.L2FB:
            print("runnning L2FB")
            run_processor(
                conf[Conf.L2FB_WORK_DIR],
                conf[Conf.L2FB_EXE],
                f"{start_date} {end_date} {data_dir} yes"
            )
            do_backup_and_pam()
            return
        case Proc.L2SM:
            print("runnning L2SM")
            run_processor(
                conf[Conf.L2SM_WORK_DIR],
                conf[Conf.L2SM_EXE],
                f"-input {data_dir} {start_date} {end_date} 1 25 L1 L"
            )
            do_backup_and_pam()
            return
        case Proc.L2SI:
            print("runnning L2SI")
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

# TODO: add Checkbox for not deleting the DataRelease folder in the begining,
#       this is needed for quick retry after error.
def gui(root: tkinter.Tk, conf: list[str]) -> None:
    """This function creates a user friendly GUI to operate the orchestrator.

    The GUI can be created on top of any instance of tkinter.Wm the most common
    subclasses are tkinter.Tk and tkinter.Toplevel.

    You need to start the mainloop."""

    # Be carefull in the way you create istances of tkinter.Variable. You have
    # to keep a reference to each one of them somewere, either in a function or
    # a class, otherwise they are going to be garbage collected away and you are
    # not going to see for example the default value of comboboxes, and
    # obviously since you have no reference to them you are not going to be able
    # to use them.
    # https://stackoverflow.com/a/66202218

    assert len(conf) == len(Conf)

    # If somebody calls us multiple times.
    for child in root.winfo_children(): child.destroy()
    if 'child' in locals(): del child

    root.resizable(False, False)
    root.title("Orchestrator")

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

    # NOTE: shall I use tkinter.ttk.LabelFrame as Leila said?
    # NOTE: It would be nice to set initialdir for all the exe_dialog so that it
    #       makes the user select files starting from the proper direcotry. But
    #       it would require a bit of messy code and there is no way to contrain
    #       explorer.exe to a single directory. A possible way to force the user
    #       to select just files in the directories of bin and scripts would be
    #       to create a Listbox dialog that shows only the listing of the
    #       directories bin and scripts. But again this would be messy.
    # NOTE: Should I validate the directory structure of the selected
    #       direcotries?

    # TODO: add a title to this dialogs.
    # TODO: this should always start from C:
    exe_dialog = lambda: tkinter.filedialog.askopenfilename(
        parent=settings_toplevel,
        filetypes=[("Executable", "*.exe *.py"),],
        multiple=False # type: ignore
    ).replace("/", "\\")
    dir_dialog = lambda: tkinter.filedialog.askdirectory(
        parent=settings_toplevel
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
        def closure(var=var, dialog=dialog, entry=entry):
            res = dialog()
            if res:
                var.set(res)
            entry.xview("end")
        tkinter.ttk.Button(settings_frame, text="Browse", command=closure) \
            .grid(column=2, row=i.value)
    del var, entry, kind, dialog
    assert len(conf_vars) == len(Conf)

    def save_config():
        if os.name != "nt":
            print("skipping the saving of the configuration file because we are"
                " not on windows", file=sys.stderr)
            return
        res = [
            f'\t"{option.name}": "{_escape_str(conf_vars[option].get())}"'
            for option in Conf
        ]
        res = "{\n" + ",\n".join(res) + "\n}"

        try:
            with open(config_options_file_path, "w") as f:
                f.write(res)
            print("configuration saved")
        except OSError:
            print("unable to save the configuration file", file=sys.stderr)

    save_button = tkinter.ttk.Button(settings_frame, text="Save",
        command=save_config).grid(column=2, row=i+1, pady=".3c")

    # Orchestrator Toplevel

    orchestrator_frame = tkinter.ttk.Frame(root)
    orchestrator_frame.grid(column=0, row=0, padx="1c", pady="1c")

    start_label = tkinter.ttk.Label(orchestrator_frame, text="Start:")
    start_label.grid(column=0, row=0)

    start_var = tkinter.StringVar(root, Proc.L1A.name, "start_var")
    start_combobox = tkinter.ttk.Combobox(
        orchestrator_frame,
        textvariable=start_var,
        values=PROC_NAMES,
        state="readonly"
    )
    start_combobox.current(0)
    start_combobox.grid(column=1, row=0)

    end_label = tkinter.ttk.Label(orchestrator_frame, text="End:")
    end_label.grid(column=3, row=0)

    end_var = tkinter.StringVar(root, Proc.L1A.name, "end_var")
    end_combobox = tkinter.ttk.Combobox(
        orchestrator_frame,
        textvariable=end_var,
        values=PROC_NAMES,
        state="readonly"
    )
    end_combobox.current(0)
    end_combobox.grid(column=4, row=0)

    pam_var = tkinter.BooleanVar(root, False, "pam_var")
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

    backup_var = tkinter.StringVar(root, "", "backup_var")
    backup_entry = tkinter.ttk.Entry(
        orchestrator_frame,
        textvariable=backup_var,
        state="readonly"
    )
    backup_entry.grid(column=2, row=1, columnspan=3, pady=".5c", sticky="w")

    clean_var = tkinter.BooleanVar(root, True, "clean_var")
    clean_checkbutton = tkinter.ttk.Checkbutton(
        orchestrator_frame,
        text="Clean",
        variable=clean_var,
        onvalue=True,
        offvalue=False
    )
    clean_checkbutton.grid(column=5, row=1)
    clean_tooltip = idlelib.tooltip.Hovertip(clean_checkbutton,
        "If you do not want to do some\n"
        "debugging keep this checked,\n"
        "unless you choose a backup file.")

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
                if end <= Proc.L1B:
                    pam_var.set(False)
            # Both the PAM checkbox and the backup entry shoulb be both cleared
            # and disabled if are not valid to input and enabled otherwise. This
            # is a more crude approach that is slightly simpler to implement.
            case "pam_var":
                if end <= Proc.L1B:
                    pam_var.set(False)
            case "backup_var":
                if start == Proc.L1A:
                    backup_var.set("")
                if backup_var.get():
                    clean_var.set(False)
            case "clean_var":
                if backup_var.get():
                    clean_var.set(False)
            case other:
                assert False
    start_var.trace_add("write", keep_ui_invariant)
    end_var.trace_add("write", keep_ui_invariant)
    pam_var.trace_add("write", keep_ui_invariant)
    backup_var.trace_add("write", keep_ui_invariant)
    clean_var.trace_add("write", keep_ui_invariant)

    # NOTE: right now the simulation is allowed to start even if start
    #       != Proc.L1A and a backup file is not selected. This is done to allow
    #       the users to do manual changes.
    def orchestrate_simulation():
        conf = [conf_vars[option].get() for option in Conf]
        try:
            run(
                start=Proc[start_var.get()],
                end=Proc[end_var.get()],
                pam=pam_var.get(),
                clean=clean_var.get(),
                backup=backup_var.get(),
                conf=conf
            )
        except Exception as ex:
            print("the orchestration encoutered a problem: ", file=sys.stderr)
            traceback.print_exception(type(ex), ex, ex.__traceback__)
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

def _main() -> int:
    if os.name != "nt":
        print("os not supported, some things are not going to work but the GUI "
            "will show up", file=sys.stderr)

    # NOTE: should I add support for CLI?

    conf = read_or_create_config_file()
    if not conf:
        conf = CONF_VALUES_DEFAULT[:]

    root = tkinter.Tk()
    gui(root, conf)
    root.mainloop()

    return 0

if __name__ == '__main__':
    raise SystemExit(_main())
