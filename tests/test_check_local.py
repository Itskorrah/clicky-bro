import pathlib
import subprocess
import tempfile
import unittest
from scripts import check_local as checks


class LocalRunnerTests(unittest.TestCase):
    def test_plan_is_offline_and_adds_platform_flags_explicitly(self):
        names = [c.name for c in checks.checklist()]
        self.assertEqual(len(names), 7)
        self.assertNotIn('macos-native-tests', names)
        extras = [c.name for c in checks.checklist(native=True, windows=True, linux=True)]
        self.assertEqual(len(extras), 10)
        self.assertIn('windows-core-tests', extras)
        self.assertIn('linux-python-tests', extras)

    def test_missing_dependencies_skip_without_spawning(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            calls = []
            def never_run(*a, **kw):
                calls.append(a)
                raise AssertionError('must not execute')
            test = checks.Check('agent-typecheck', ('npm', 'run', 'test'), 'npm-deps')
            result = checks.execute(test, root, system='Linux', which=lambda _: '/fake/npm', runner=never_run)
            self.assertEqual(result.status, 'skipped')
            self.assertEqual(calls, [])

    def test_native_check_refuses_false_mac_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            test = checks.Check('native', ('python3', '-V'), 'macos')
            result = checks.execute(test, pathlib.Path(directory), system='Linux', runner=lambda *a, **kw: None)
            self.assertEqual(result.status, 'skipped')
            self.assertIn('macOS', result.reason)

    def test_pass_fail_timeout_and_result_codes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            test = checks.Check('sample', ('python3', '--version'))
            fake = lambda *a, **kw: subprocess.CompletedProcess(a, 0)
            ok = checks.execute(test, root, which=lambda _: '/fake/python3', runner=fake)
            self.assertEqual(ok.status, 'passed')
            bad = checks.execute(test, root, which=lambda _: '/fake/python3', runner=lambda *a, **kw: subprocess.CompletedProcess(a, 1))
            self.assertEqual(bad.status, 'failed')
            self.assertEqual(checks.exit_code([ok]), 0)
            self.assertEqual(checks.exit_code([ok, checks.Result('skip','skipped',0)]), 2)
            self.assertEqual(checks.exit_code([ok, bad]), 1)
            timeout = checks.execute(test, root, which=lambda _: '/fake/python3', runner=lambda *a, **kw: (_ for _ in ()).throw(subprocess.TimeoutExpired('sample',1)))
            self.assertEqual(timeout.status, 'failed')

    def test_dependency_prerequisite_with_node_modules_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            (root / 'app/node_modules').mkdir(parents=True)
            test = checks.Check('agent', ('npm', 'run', 'test'), 'npm-deps')
            result = checks.execute(test, root, which=lambda _: '/fake/npm', runner=lambda *a, **kw: subprocess.CompletedProcess(a, 0))
            self.assertEqual(result.status, 'passed')


if __name__ == '__main__':
    unittest.main()
