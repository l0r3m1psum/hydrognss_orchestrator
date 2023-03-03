import unittest
import orchestrator

class TestOrchestratorRun(unittest.TestCase):

    def setUp(self):
        if not __debug__:
            raise Exception("this test case must be run in debug mode")

    def test_processors_order(self):
        with self.assertRaises(AssertionError):
            orchestrator.run(
                start=orchestrator.Proc.L1B,
                end=orchestrator.Proc.L1A,
                pam=False,
                clean=True,
                backup="/any/path",
                conf=orchestrator.CONF_VALUES_DEFAULT
            )

    def test_pam_when_processor_is_not_L2(self):
        with self.assertRaises(AssertionError):
            orchestrator.run(
                start=orchestrator.Proc.L1A,
                end=orchestrator.Proc.L1A,
                pam=True,
                clean=True,
                backup="",
                conf=orchestrator.CONF_VALUES_DEFAULT
            )

    def test_backup_when_clean_is_selected(self):
        with self.assertRaises(AssertionError):
            orchestrator.run(
                start=orchestrator.Proc.L1B,
                end=orchestrator.Proc.L1B,
                pam=False,
                clean=True,
                backup="/any/path",
                conf=orchestrator.CONF_VALUES_DEFAULT
            )

    def test_L2_processors_should_be_the_same(self):
        with self.assertRaises(AssertionError):
            orchestrator.run(
                start=orchestrator.Proc.L2FT,
                end=orchestrator.Proc.L2SI,
                pam=False,
                clean=False,
                backup="/any/path",
                conf=orchestrator.CONF_VALUES_DEFAULT
            )

    def test_backup_without_clean(self):
        with self.assertRaises(AssertionError):
            orchestrator.run(
                start=orchestrator.Proc.L1B,
                end=orchestrator.Proc.L1B,
                pam=False,
                clean=False,
                backup="/any/path",
                conf=orchestrator.CONF_VALUES_DEFAULT
            )

if __name__ == '__main__':
    unittest.main()
