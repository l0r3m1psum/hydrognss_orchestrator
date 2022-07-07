from utils import write_to_yaml, get_timestamp, get_data_time_boudaries_from
import subprocess
from abc import ABC
import logging
import os
import shutil
import re
from itertools import chain

DATA_RELEASE = 'DataRelease'
L1A_L1B = DATA_RELEASE + '\L1A_L1B'

class Processor(ABC):

    def __init__(self, context, output) -> None:
        self.ctx = context
        if 'timestamp' not in self.ctx:
            self.ctx['timestamp'] = get_timestamp()
        self.out = output
        self.cwd = self.ctx['processors'][self.__class__.__name__]['workingDirectory']
        self.command = []
        # self.completed_process = None
        # init logging
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(context['logLevel'])
        fh = logging.FileHandler(f'{self.ctx["timestamp"]}.log')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.log.addHandler(fh)

    def _build_args(self):
        self.log.debug('Not implemented...')
        pass

    def _build_command(self):
        if 'executable' in self.ctx['processors'][self.__class__.__name__]:
            self.log.debug('Found executable in config')
            command = [os.path.join(
                os.path.normpath(self.ctx['processors'][self.__class__.__name__]['workingDirectory']),
                os.path.normpath(self.ctx['processors'][self.__class__.__name__]['executable'])
            )]
        elif 'script' in self.ctx['processors'][self.__class__.__name__]:
            self.log.debug('Found script in config')
            command = ['python', os.path.join(
                os.path.normpath(self.ctx['processors'][self.__class__.__name__]['workingDirectory']),
                os.path.normpath(self.ctx['processors'][self.__class__.__name__]['script'])
            )]
        else:
            self.log.error(
                'Malformed config yaml: missing script or executable relative path')
            raise Exception('Malformed configuration yaml')
        if 'args' in self.ctx['processors'][self.__class__.__name__]:
            command = [*command, *self.ctx['processors']
                       [self.__class__.__name__]['args']]
            command = list(filter(None, command))
        self.log.debug(f'Built command string: {" ".join(command)}')
        self.command = command

    def _before_run(self):
        self.log.debug('Not implemented...')
        pass

    def _run(self):
        settings = {
            'cwd': self.cwd,
            'text': True,
            'stdout': subprocess.PIPE,
            'stderr': subprocess.PIPE,
            'universal_newlines': True
        }
        self.log.debug(f'Process settings\n{str(settings)}')
        self.log.info(f'Starting processor execution')
        try:
            popen = subprocess.Popen(self.command, **settings)
            self.log.debug(f'Execution Output\n')
            for line in chain(iter(popen.stdout.readline, ""), iter(popen.stderr.readline, "")):
                self.log.debug(line)
                print(line) 
            popen.stdout.close()
            popen.stderr.close()
            return_code = popen.wait()
            if return_code:
                raise subprocess.CalledProcessError(return_code, self.command)
        except subprocess.CalledProcessError as e:
            self.log.error("Processor error", exc_info=True)
            raise e
        else:
            self.log.info('Processor execution ended.')
            self.log.debug(f'Execution Context\n{str(self.ctx)}')
            # self.completed_process = cp

    def _after_run(self):
        self.log.debug('Not implemented...')
        pass

    def _end(self):
        write_to_yaml(self.out, self.ctx)

    def start(self, dry=False):
        self.log.info('_build_args')
        self._build_args()
        self.log.info('_build_command')
        self._build_command()
        self.log.info('_before_run')
        self._before_run()
        if not dry:
            self.log.info('_run')
            self._run()
        else:
            self.log.info('dry mode, skip processing...')
        self.log.info('_after_run')
        self._after_run()
        self.log.info('_end')
        self._end()


class L1_A(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def _before_run(self):
        self.cwd = os.path.join(self.cwd, 'bin')
        self.log.debug(f'Updated working directory {self.cwd}')

    
    def _after_run(self):
        # out_lines = self.completed_process.stdout.splitlines()
        # out_lines = list(filter(None, out_lines))
        # l1a_tmp_dir_path = out_lines[len(out_lines) - 1]
        with open(os.path.join(self.ctx['processors'][__class__.__name__]['workingDirectory'], 'conf', 'AbsoluteFilePath.txt')) as f:
            l1a_output_path = f.readlines().pop()
        
        self.ctx['backupFile'] = list(filter(None, l1a_output_path.split("\\"))).pop()

        self.log.debug(f'L1A generated output: {l1a_output_path}')
        l1a_data_path_src = os.path.join(l1a_output_path, L1A_L1B)
        self.log.debug(f'L1A generated data: {l1a_data_path_src}')
        l1a_data_path_dst =  os.path.join(self.ctx['dataRoot'], L1A_L1B)
        self.log.debug(f'Copying L1A data from {l1a_data_path_src} to {l1a_data_path_dst}')
        shutil.copytree(l1a_data_path_src, l1a_data_path_dst, dirs_exist_ok=True)
        
        pam_data_path_src = None
        for f in os.listdir(l1a_output_path):
            if re.match('.*mat', f):
                pam_data_path_src = os.path.join(l1a_output_path, f)
                break
        if not pam_data_path_src:
            self.log.debug(f'Files in {l1a_data_path_src}: {os.listdir(l1a_data_path_src)}')
            raise Exception(f'No PAM mat file found in {pam_data_path_src}')
        pam_data_path_dst = os.path.join(self.ctx['backupRoot'], 'PAM', f'{self.ctx["backupFile"]}.mat')
        self.log.debug(f'Copying PAM data from {pam_data_path_src} to {pam_data_path_dst}')
        shutil.copy(pam_data_path_src, pam_data_path_dst)
        self.log.debug('Done.')


class L1_B(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def _build_args(self):
        time_frame = get_data_time_boudaries_from(
            os.path.join(self.ctx['dataRoot'], L1A_L1B))
        self.log.debug(f'Built args string: {" ".join(time_frame)}')
        self.ctx['processors'][self.__class__.__name__]['args'] = time_frame


class L2_SM(Processor):
    argsTemplate = '-input {dataRoot}\DataRelease\L1A_L1B {dataRoot}\DataRelease\L2OP-SSM {dataRoot}\Auxiliary_Data {startYear} {startMonth} {startDay} {numberOfDays} {resolution} {signal} {polarization}'

    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def _build_args(self):
        time_frame = get_data_time_boudaries_from(
            os.path.join(self.ctx['dataRoot'], L1A_L1B))
        # substitutions
        args = self.argsTemplate
        args = args.replace('{dataRoot}', self.ctx['dataRoot'])
        args = args.replace('{startYear}', time_frame[0].split('-')[0])
        args = args.replace('{startMonth}', time_frame[0].split('-')[1])
        args = args.replace('{startDay}', time_frame[0].split('-')[2])
        args = args.replace('{numberOfDays}', '')
        args = args.replace(
            '{resolution}', self.ctx['processors'][self.__class__.__name__]['resolution'])
        args = args.replace(
            '{signal}', self.ctx['processors'][self.__class__.__name__]['signal'])
        args = args.replace(
            '{polarization}', self.ctx['processors'][self.__class__.__name__]['polarization'])
        self.log.debug(f'Built args string: {args}')
        self.ctx['processors'][self.__class__.__name__]['args'] = args.split(
            ' ')


class L2_FB(Processor):
    argsTemplate = '{startDate} {endDate} {dataRoot}'

    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def _build_args(self):
        time_frame = get_data_time_boudaries_from(
            os.path.join(self.ctx['dataRoot'], L1A_L1B))
        # substitutions
        args = self.argsTemplate
        args = args.replace('{startDate}', time_frame[0])
        args = args.replace('{endDate}', time_frame[1])
        args = args.replace('{dataRoot}', self.ctx['dataRoot'])
        self.log.debug(f'Built args string: {args}')
        self.ctx['processors'][self.__class__.__name__]['args'] = args.split(
            ' ')


class L2_FT(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)
    
    def _build_args(self):
        time_frame = get_data_time_boudaries_from(
            os.path.join(self.ctx['dataRoot'], L1A_L1B))
        self.log.debug(f'Built args string: {" ".join(time_frame)}')
        self.ctx['processors'][self.__class__.__name__]['args'] = time_frame

class L2_SI(Processor):
    argsTemplate = '-P {DataRelease_folder}'
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def _build_args(self):
        args = self.argsTemplate
        args = args.replace('{DataRelease_folder}',os.path.join(self.ctx['dataRoot'],DATA_RELEASE))
        self.log.debug(f'Built args string: {args}')
        self.ctx['processors'][self.__class__.__name__]['args'] = args.split(
            ' ')

