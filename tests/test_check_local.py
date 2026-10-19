import pathlib
import subprocess
import sys
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

    def test_windows_npm_shim_uses_node_cli_without_shell(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            npm = root / 'Program Files' / 'nodejs' / 'npm.cmd'
            node = npm.parent / 'node.exe'
            cli = npm.parent / 'node_modules' / 'npm' / 'bin' / 'npm-cli.js'
            cli.parent.mkdir(parents=True)
            npm.parent.mkdir(parents=True, exist_ok=True)
            node.touch()
            cli.touch()
            npm.touch()
            found = {'npm': str(npm), 'node': str(node)}
            actual = checks.command_argv(('npm', 'run', 'build', '--prefix', 'app'),
                                         system='Windows', which=found.get)
            self.assertEqual(actual, (str(node), str(cli), 'run', 'build', '--prefix', 'app'))

    def test_dotnet_runtime_without_sdk_is_skipped_before_test_command(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            test = checks.Check('windows-core-tests', ('dotnet', 'test', 'Core.Tests.csproj'), 'dotnet')
            calls = []

            def no_sdk(*args, **kwargs):
                calls.append(args[0])
                return subprocess.CompletedProcess(args[0], 0, stdout='', stderr='')

            def never_run(*args, **kwargs):
                raise AssertionError('test command must not execute without an SDK')

            result = checks.execute(test, root, system='Windows', which=lambda _: '/fake/dotnet',
                                    probe=no_sdk, runner=never_run)
            self.assertEqual(result.status, 'skipped')
            self.assertIn('SDK', result.reason)
            self.assertEqual(calls, [['/fake/dotnet', '--list-sdks']])

    def test_dotnet_sdk_presence_runs_core_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            test = checks.Check('windows-core-tests', ('dotnet', 'test', 'Core.Tests.csproj'), 'dotnet')

            def has_sdk(*args, **kwargs):
                return subprocess.CompletedProcess(args[0], 0, stdout='8.0.426 [C:/dotnet/sdk]', stderr='')

            calls = []

            def pass_test(argv, **kwargs):
                calls.append(argv)
                return subprocess.CompletedProcess(argv, 0, stdout='', stderr='')

            result = checks.execute(test, root, system='Windows', which=lambda _: '/fake/dotnet',
                                    probe=has_sdk, runner=pass_test)
            self.assertEqual(result.status, 'passed')
            self.assertEqual(calls, [test.argv])

    def test_runner_discards_output_with_bytes_outside_windows_code_page(self):
        with tempfile.TemporaryDirectory() as directory:
            root = pathlib.Path(directory)
            code = "import sys; sys.stdout.buffer.write(bytes([0x9d])); sys.stderr.buffer.write(bytes([0x9d]))"
            test = checks.Check('unicode-output', (sys.executable, '-c', code))
            result = checks.execute(test, root, system='Windows')
            self.assertEqual(result.status, 'passed')


if __name__ == '__main__':
    unittest.main()
