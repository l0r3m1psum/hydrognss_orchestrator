import unittest
import orchestrator
import itertools


class TestOrchestratorArgumentsValidation(unittest.TestCase):

    def setUp(self):
        if not __debug__:
            self.fail("this test case must be run in debug mode")

    def test_all(self):

        args_gen = itertools.product(
            orchestrator.Proc.__members__.values(), # start
            orchestrator.Proc.__members__.values(), # end
            [True, False],                          # pam
            [True, False],                          # clean
            ["", "C:\\some\\path"]                  # backup
        )
        for args in args_gen:
            try:
                _ = orchestrator.validate_orchestrator_arguments(*args)
            except AssertionError:
                self.fail(args)

        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()

# tkinter.Tk.dooneevent https://stackoverflow.com/a/49028688
