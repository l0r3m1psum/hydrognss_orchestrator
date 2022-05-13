from msilib.schema import Error
from utils import write_to_yaml, get_timestamp
import subprocess
from abc import ABC
import logging

run_timestamp = get_timestamp()

class Processor(ABC):

    def __init__(self, context, output, log_file = f'log_{run_timestamp}.log') -> None:
        self.ctx = context
        self.out = output
        self.command = []
        self.completed_process = None
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(context['logLevel'])
        if log_file:
            self.fh = logging.FileHandler(log_file)
            self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.log.addHandler(self.fh)
    
    def _before_build_command():
        pass
    
    def _build_command(self):
        if 'executable' in self.ctx['processors'][self.__class__.__name__]:
            command = [self.ctx['processors'][self.__class__.__name__]['executable']]
        elif 'script' in self.ctx['processors'][self.__class__.__name__]:
            command = ['python', self.ctx['processors'][self.__class__.__name__]]
        else:
            self.log.error('Malformed config yaml: missing script or executable relative path')
            raise Exception('Malformed configuration yaml')
        
        if 'args' in self.ctx['processors'][self.__class__.__name__]:
            command = [*command, *self.ctx['processors'][self.__class__.__name__]['args']]
            command = list(filter(None, command))
        
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
        self.log.debug(f'Command being executed\n{str(self.command)}')
        self.log.debug(f'Process settings\n{str(settings)}')
        self.log.info(f'Starting processor execution')
        try:
            cp: subprocess.CompletedProcess = subprocess.run(self.command, **settings)
        except subprocess.CalledProcessError as e:
            self.log.error("Processor error", exc_info=True)
            self.log.error(f"Output\n---stdout---\n{e.stdout}\n---stderr---\n{e.stderr}")
            raise e
        else:
            self.log.info('Processor execution ended.')
            self.log.debug(f"Output\n---stdout---\n{cp.stdout}\n---stderr---\n{cp.stderr}")
            self.completed_process = cp

    def _after_run(self):
        pass
    
    def _end(self):
        self.log.debug(f'Executed Command\n{" ".join(self.completed_process.args)}')
        self.log.debug(f'Execution Output\n---stdout---\n{self.completed_process.stdout}\n---stderr---\n{self.completed_process.stderr}')
        self.log.debug(f'Execution Context\n{str(self.ctx)}')
        write_to_yaml(self.out, self.ctx)

    def start(self):
        self._before_build_command()
        self._build_command()
        self._before_run()
        self._run()
        self._after_run()
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

    def _before_build_command(self):
        # se gia esistnono nel contesto, non fare nulla
        if 'args' in self.ctx['processors'][self.__class__.__name__]:
            pass
        #altrimenti vai a recuperarli
        else:
            self.ctx['processors'][self.__class__.__name__]['args'] = ['2021-12-10', '2021-12-12']
    

class L2_SM(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)



class L2_FB(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)



class L2_FT(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)
    

class L2_SI(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

