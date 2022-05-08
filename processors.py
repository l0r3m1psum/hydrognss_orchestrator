from utils import write_to_yaml
import subprocess
from abc import ABC, abstractmethod


class Processor(ABC):
    def __init__(self, context, output) -> None:
        self.ctx = context
        self.out = output

    def run(self):
        self.before_run()
        cp: subprocess.CompletedProcess = subprocess.run(
            [
                self.ctx['processors'][self.__class__.__name__]['executable'], 
                *self.ctx['processors'][self.__class__.__name__]['args']
            ], 
            check=True, capture_output=True)
        self.after_run(cp)
        self.write()

    
    def write(self):
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