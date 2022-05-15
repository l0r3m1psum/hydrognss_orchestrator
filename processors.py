from msilib.schema import Error
from utils import write_to_yaml, get_timestamp, get_data_time_boudaries_from
import subprocess
from abc import ABC
import logging
import os

L1A_L1B_PATH = 'DataRelease/L1A_L1B'

run_timestamp = get_timestamp()


class Processor(ABC):

    def __init__(self, context, output, log_file=f'log_{run_timestamp}.log') -> None:
        self.ctx = context
        self.out = output
        self.command = []
        self.completed_process = None
        # init logging
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(context['logLevel'])
        fh = logging.FileHandler(log_file)
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        self.log.addHandler(fh)

    def _build_args(self):
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
        self.log.debug(f'Built command: {command}')
        self.command = command

    def _before_run(self):
        pass

    def _run(self):
        settings = {
            'check': True,
            'capture_output': True,
            'text': True,
            'cwd': self.ctx['processors'][self.__class__.__name__]['workingDirectory'],
        }
        self.log.debug(f'Process settings\n{str(settings)}')
        self.log.info(f'Starting processor execution')
        try:
            cp: subprocess.CompletedProcess = subprocess.run(
                self.command, **settings)
        except subprocess.CalledProcessError as e:
            self.log.error("Processor error", exc_info=True)
            self.log.error(
                f"Output\n---stdout---\n{e.stdout}\n---stderr---\n{e.stderr}")
            raise e
        else:
            self.log.info('Processor execution ended.')
            self.log.debug(
                f"Output\n---stdout---\n{cp.stdout}\n---stderr---\n{cp.stderr}")
            self.log.debug(
                f'Execution Output\n---stdout---\n{cp.stdout}\n---stderr---\n{cp.stderr}')
            self.log.debug(f'Execution Context\n{str(self.ctx)}')

    def _after_run(self):
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

    def _after_run(self):
        # copia i prodotti generati dal processore nella storage directory
        # aggiorna il context
        pass


class L1_B(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def _build_args(self):
        time_frame = get_data_time_boudaries_from(
            os.path.join(self.ctx['dataRoot'], L1A_L1B_PATH))
        self.log.debug(f'Built args string: {" ".join(time_frame)}')
        self.ctx['processors'][self.__class__.__name__]['args'] = time_frame


class L2_SM(Processor):
    argsTemplate = '-input {dataRoot}\DataRelease\L1A_L1B {dataRoot}\DataRelease\L2OP-SSM {dataRoot}\Auxiliary_Data {startYear} {startMonth} {startDay} {numberOfDays} {resolution} {signal} {polarization}'

    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def _build_args(self):
        time_frame = get_data_time_boudaries_from(
            os.path.join(self.ctx['dataRoot'], L1A_L1B_PATH))
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
            os.path.join(self.ctx['dataRoot'], L1A_L1B_PATH))
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


class L2_SI(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)
