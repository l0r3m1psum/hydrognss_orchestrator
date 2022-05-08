from utils import write_to_yaml, get_timestamp
import subprocess
from abc import ABC, abstractmethod
import logging

run_timestamp = get_timestamp()
class Processor(ABC):

    def __init__(self, context, output, log_file = f'log_{run_timestamp}.log') -> None:
        self.ctx = context
        self.out = output
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.setLevel(context['logLevel'])
        if log_file:
            self.fh = logging.FileHandler(log_file)
            self.fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            self.log.addHandler(self.fh)

    def run(self):
        self.before_run()

        executable = self.ctx['processors'][self.__class__.__name__]['executable']
        if self.ctx['processors'][self.__class__.__name__]['args']:
            args = [executable, *self.ctx['processors'][self.__class__.__name__]['args']]
        else:
            args = [executable]
        self.log.debug(f'Args\n{str(args)}')
        
        self.log.info(f'Starting processor execution...')
        cp: subprocess.CompletedProcess = subprocess.run(
            args, 
            check=True, capture_output=True, text=True)
        self.log.info('Processor execution ended.')

        self.after_run(cp)
        self.end(cp)

    
    def end(self, cp: subprocess.CompletedProcess):
        self.log.debug(f'Executed Command\n{" ".join(cp.args)}')
        self.log.debug(f'Execution Output\n---stdout---\n{cp.stdout}\n---stderr---\n{cp.stderr}')
        self.log.debug(f'Execution Context\n{str(self.ctx)}')
        write_to_yaml(self.out, self.ctx)


    @abstractmethod
    def before_run(self):
        pass
    
    @abstractmethod
    def after_run(self, cp: subprocess.CompletedProcess):
        pass



class L1_A(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def before_run(self):
        pass
    
    def after_run(self, cp: subprocess.CompletedProcess):
        pass

class L1_B(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def before_run(self):
        pass
    
    def after_run(self, cp: subprocess.CompletedProcess):
        pass

class L2_SM(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def before_run(self):
        pass
    
    def after_run(self, cp: subprocess.CompletedProcess):
        pass

class L2_FB(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)
    
    def before_run(self):
        pass
    
    def after_run(self, cp: subprocess.CompletedProcess):
        pass

class L2_FT(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)
    
    def before_run(self):
        pass
    
    def after_run(self, cp: subprocess.CompletedProcess):
        pass

class L2_SI(Processor):
    def __init__(self, context, output) -> None:
        super().__init__(context, output)

    def before_run(self):
        pass
    
    def after_run(self, cp: subprocess.CompletedProcess):
        pass