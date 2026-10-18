#!/usr/bin/env python3
"""Local clicky-bro development commands; no global configuration changes."""
import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
LOCAL_RUNTIME = ROOT / '.local/runtime/native'
LOCAL_WORKSPACE = ROOT / '.local/workspaces/default'
DERIVED = Path.home() / 'Library/Caches/clicky-bro/DerivedData-local'
BINARY = DERIVED / 'Build/Products/Debug/OpenClicky.app/Contents/MacOS/OpenClicky'


def developer_paths(root=ROOT, *, home=None, cache=None, canonical_key=None):
    """Resolve private developer runtime and staged-code paths without touching them."""
    root = Path(root)
    home = Path(home) if home is not None else Path.home() / 'Library/Application Support/clicky-bro/development'
    cache = Path(cache) if cache is not None else Path.home() / 'Library/Caches/clicky-bro/development'
    agent = cache / 'agent'
    return {
        'runtime': home,
        'workspace': home / 'workspaces/default',
        'user_skills': home / 'skills',
        'credentials': home / 'credentials',
        'key_file': home / 'credentials/gemini.json',
        'migration_marker': home / '.developer-migration-v1',
        'cache': cache,
        'agent': agent,
        'agent_dist': agent / 'dist',
        'agent_package': agent / 'package.json',
        'agent_commander': agent / 'node_modules/commander',
        'agent_config': agent / 'config',
        'agent_config_template': agent / 'config/codex-config.toml',
        'agent_skills': agent / 'skills',
        'agent_version': agent / 'macos/clicky-bro/VERSION',
        'app_skills': cache / 'app-skills',
        'source_runtime': root / '.local/runtime/native',
        'source_workspace': root / '.local/workspaces/default',
        'source_key': Path(canonical_key) if canonical_key is not None else root / '.local/credentials/gemini.json',
        'source_agent_dist': root / 'app/agent/dist',
        'source_agent_package': root / 'app/agent/package.json',
        'source_commander': root / 'app/node_modules/commander',
        'source_agent_config_template': root / 'app/config/codex-config.toml',
        'source_agent_skills': root / 'app/skills',
        'source_agent_version': root / 'app/macos/clicky-bro/VERSION',
        'source_app_skills': root / 'app/app-skills',
        'source_default_cli': root / 'app/agent/dist/cli.js',
        'source_default_workspace': root / '.local/workspaces/default',
        'source_default_app_skills': root / 'app/app-skills',
    }


def _check_directory(path, *, private_root=None):
    path = Path(path)
    if private_root is not None:
        private_root = Path(private_root)
        try:
            relative = path.relative_to(private_root)
        except ValueError as error:
            raise RuntimeError('Developer path escaped its private root.') from error
        _check_directory(private_root)
        current = private_root
        for component in relative.parts:
            current = current / component
            _create_private_directory(current)
        return path
    return _create_private_directory(path)


def _create_private_directory(path):
    path = Path(path)
    try:
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
        info = path.lstat()
    except OSError as error:
        raise RuntimeError('Could not prepare a private developer directory.') from error
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise RuntimeError('Developer directory is not an owned regular directory.')
    try:
        os.chmod(path, 0o700)
    except OSError as error:
        raise RuntimeError('Could not secure a private developer directory.') from error
    return path


def _regular_owned_file(path, *, mode=None, max_size=None):
    try:
        info = Path(path).lstat()
    except OSError:
        return False
    return (stat.S_ISREG(info.st_mode) and info.st_uid == os.getuid()
            and (mode is None or stat.S_IMODE(info.st_mode) == mode)
            and (max_size is None or 0 < info.st_size <= max_size))


def _copy_file_atomically(source, destination, *, mode=0o600, replace=False, require_source_owner=True):
    source = Path(source)
    destination = Path(destination)
    source_fd = None
    temporary_path = None
    try:
        source_fd = os.open(source, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0))
        source_info = os.fstat(source_fd)
        if not stat.S_ISREG(source_info.st_mode) or (require_source_owner and source_info.st_uid != os.getuid()):
            raise RuntimeError('Developer source file is not a regular file owned by this user.')
        if destination.exists() or destination.is_symlink():
            destination_info = destination.lstat()
            if (stat.S_ISLNK(destination_info.st_mode) or not stat.S_ISREG(destination_info.st_mode)
                    or destination_info.st_uid != os.getuid()):
                raise RuntimeError('Developer destination file is not a regular file owned by this user.')
            if not replace:
                return False

        fd, temp_name = tempfile.mkstemp(prefix='.' + destination.name + '.', dir=destination.parent)
        temporary_path = Path(temp_name)
        os.fchmod(fd, mode)
        with os.fdopen(source_fd, 'rb') as source_handle, os.fdopen(fd, 'wb') as destination_handle:
            source_fd = None
            shutil.copyfileobj(source_handle, destination_handle, length=1024 * 1024)
            destination_handle.flush()
            os.fsync(destination_handle.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
        os.chmod(destination, mode)
        return True
    except FileNotFoundError:
        raise RuntimeError('A required developer source file is missing.')
    except OSError as error:
        raise RuntimeError('Could not copy a developer file safely.') from error
    finally:
        if source_fd is not None:
            os.close(source_fd)
        if temporary_path is not None:
            try:
                temporary_path.unlink()
            except OSError:
                pass


def _seed_missing_tree(source, destination, *, private_root, source_root=None):
    source = Path(source)
    destination = Path(destination)
    source_root = Path(source_root) if source_root is not None else source
    if not source.exists() and not source.is_symlink():
        return
    info = source.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode) or info.st_uid != os.getuid():
        raise RuntimeError('Developer state source is not an owned regular directory.')
    _check_directory(destination, private_root=private_root)
    for entry in os.scandir(source):
        source_path = Path(entry.path)
        destination_path = destination / entry.name
        entry_info = entry.stat(follow_symlinks=False)
        if stat.S_ISLNK(entry_info.st_mode):
            raise RuntimeError('Developer state contains a symbolic link; migration stopped without following it.')
        if stat.S_ISDIR(entry_info.st_mode):
            if destination_path.exists() or destination_path.is_symlink():
                destination_info = destination_path.lstat()
                if stat.S_ISLNK(destination_info.st_mode) or not stat.S_ISDIR(destination_info.st_mode) or destination_info.st_uid != os.getuid():
                    raise RuntimeError('Existing developer state path is not an owned regular directory.')
            _check_directory(destination_path, private_root=private_root)
            _seed_missing_tree(source_path, destination_path, private_root=private_root, source_root=source_root)
        elif stat.S_ISREG(entry_info.st_mode):
            # The project-managed key is mirrored only from the validated
            # canonical source below. Never revive a stale legacy copy.
            if source_path.relative_to(source_root).as_posix() == 'credentials/gemini.json':
                continue
            _copy_file_atomically(source_path, destination_path, mode=0o600, replace=False)
        else:
            raise RuntimeError('Developer state contains an unsupported file type; migration stopped.')


def _read_validated_key(path):
    path = Path(path)
    try:
        parent_info = path.parent.lstat()
    except OSError:
        return None
    if (stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode)
            or parent_info.st_uid != os.getuid()):
        return None
    try:
        fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NOFOLLOW', 0) | getattr(os, 'O_CLOEXEC', 0))
    except OSError:
        return None
    try:
        info = os.fstat(fd)
        if (not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
                or stat.S_IMODE(info.st_mode) != 0o600 or not 0 < info.st_size <= 8192):
            return None
        content = bytearray()
        while len(content) <= 8192:
            chunk = os.read(fd, min(4096, 8193 - len(content)))
            if not chunk:
                break
            content.extend(chunk)
        if not 0 < len(content) <= 8192:
            return None
        try:
            parsed = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return None
        if not isinstance(parsed, dict) or not isinstance(parsed.get('api_key'), str):
            return None
        api_key = parsed['api_key']
        if not (30 <= len(api_key) <= 200 and all(character.isascii() and (character.isalnum() or character in '_.-') for character in api_key)):
            return None
        return bytes(content)
    finally:
        os.close(fd)


def _remove_key_mirror(path):
    path = Path(path)
    if not (path.exists() or path.is_symlink()):
        return
    try:
        info = path.lstat()
    except OSError as error:
        raise RuntimeError('Could not inspect the developer key mirror safely.') from error
    if (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid()
            or stat.S_IMODE(info.st_mode) != 0o600):
        raise RuntimeError('Developer key mirror is not an owned owner-only regular file.')
    try:
        path.unlink()
    except OSError as error:
        raise RuntimeError('Could not remove a stale developer key mirror.') from error


def _refresh_key_mirror(source, destination, *, private_root):
    content = _read_validated_key(source)
    if content is None:
        _remove_key_mirror(destination)
        return False
    destination = Path(destination)
    _check_directory(destination.parent, private_root=private_root)
    if destination.exists() or destination.is_symlink():
        if not _regular_owned_file(destination, mode=0o600, max_size=8192):
            raise RuntimeError('Developer key mirror is not an owned owner-only regular file.')
    temp_path = None
    try:
        fd, name = tempfile.mkstemp(prefix='.gemini.', dir=destination.parent)
        temp_path = Path(name)
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'wb') as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, destination)
        temp_path = None
        os.chmod(destination, 0o600)
    except OSError as error:
        raise RuntimeError('Could not refresh the private developer key mirror.') from error
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except OSError:
                pass
    if not _regular_owned_file(destination, mode=0o600, max_size=8192):
        raise RuntimeError('Developer key mirror failed owner-only validation.')
    return True


def _stage_tree(source, destination, *, cache_root):
    source = Path(source)
    destination = Path(destination)
    source_info = source.lstat()
    if stat.S_ISLNK(source_info.st_mode) or not stat.S_ISDIR(source_info.st_mode):
        raise RuntimeError('A required staged developer asset directory is missing or invalid.')
    _check_directory(destination, private_root=cache_root)
    for current, directories, files in os.walk(source, followlinks=False):
        relative = Path(current).relative_to(source)
        target_directory = destination / relative
        _check_directory(target_directory, private_root=cache_root)
        for name in directories:
            path = Path(current) / name
            if path.is_symlink():
                raise RuntimeError('A staged developer asset contains a symbolic link.')
            _check_directory(target_directory / name, private_root=cache_root)
        for name in files:
            source_file = Path(current) / name
            if source_file.is_symlink() or not source_file.is_file():
                raise RuntimeError('A staged developer asset is not a regular file.')
            _copy_file_atomically(source_file, target_directory / name, mode=0o600, replace=True)


def _safe_path(root, original_path):
    root = Path(root).resolve()
    entries = []
    for value in [str(Path.home() / '.local/bin'), '/usr/bin', '/bin', '/usr/sbin', '/sbin', *original_path.split(os.pathsep)]:
        if not value:
            continue
        candidate = Path(value).expanduser()
        try:
            resolved = candidate.resolve()
            resolved.relative_to(root)
        except (OSError, ValueError):
            entries.append(str(candidate))
    return os.pathsep.join(dict.fromkeys(entries))


def _managed_node(root, path):
    node = shutil.which('node', path=path)
    if node is None:
        return None
    try:
        Path(node).resolve().relative_to(Path(root).resolve())
    except (OSError, ValueError):
        return node
    return None


def _write_config(path, data):
    path = Path(path)
    _check_directory(path.parent, private_root=path.parent.parent)
    fd, name = tempfile.mkstemp(prefix='.shell.', dir=path.parent)
    temporary = Path(name)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            json.dump(data, handle, indent=2)
            handle.write('\n')
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
        temporary = None
        os.chmod(path, 0o600)
    except OSError as error:
        raise RuntimeError('Could not save the private developer settings safely.') from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except OSError:
                pass


def _default_settings(paths, node):
    return {
        'cliCommand': [node or 'node', str(paths['agent_dist'] / 'cli.js')],
        'backendUrl': 'http://127.0.0.1:18787',
        'workspace': str(paths['workspace']),
        'writableRoots': [],
        'answerSource': 'gemini',
        'answerModels': {'gemini': 'gemini-3.5-flash-lite'},
        'speechVoice': 'mac',
        'transcriptionProvider': 'apple',
        'registerAsLoginItem': False,
        'useClaudeCodePlan': False,
        'useCodexPlan': False,
        'appSkillsPath': str(paths['app_skills']),
    }


def _migrate_default_paths(config_path, paths, root, node):
    config_path = Path(config_path)
    if config_path.is_symlink():
        raise RuntimeError('Developer settings cannot be a symbolic link.')
    if not config_path.exists():
        _write_config(config_path, _default_settings(paths, node))
        return
    if not _regular_owned_file(config_path):
        raise RuntimeError('Developer settings are not an owned regular file.')
    try:
        data = json.loads(config_path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return
    if not isinstance(data, dict):
        return
    changed = False
    command = data.get('cliCommand')
    old_cli = str(Path(root) / 'app/agent/dist/cli.js')
    if (isinstance(command, list) and len(command) == 2 and command[1] == old_cli
            and isinstance(command[0], str)
            and (command[0] in ('node', node) or Path(command[0]).name in ('node', 'nodejs'))):
        data['cliCommand'] = [command[0], str(paths['agent_dist'] / 'cli.js')]
        changed = True
    if data.get('workspace') == str(Path(root) / '.local/workspaces/default'):
        data['workspace'] = str(paths['workspace'])
        changed = True
    if data.get('appSkillsPath') == str(Path(root) / 'app/app-skills'):
        data['appSkillsPath'] = str(paths['app_skills'])
        changed = True
    if changed:
        _write_config(config_path, data)


def _migration_complete(path):
    path = Path(path)
    if not (path.exists() or path.is_symlink()):
        return False
    if not _regular_owned_file(path, mode=0o600, max_size=128):
        raise RuntimeError('Developer migration marker is invalid.')
    try:
        if path.read_text(encoding='ascii').strip() != 'v1':
            raise RuntimeError('Developer migration marker is invalid.')
        return True
    except (OSError, UnicodeDecodeError):
        raise RuntimeError('Developer migration marker is invalid.')


def _write_migration_marker(path):
    path = Path(path)
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, 'O_NOFOLLOW', 0), 0o600)
        with os.fdopen(fd, 'w', encoding='ascii') as handle:
            handle.write('v1\n')
            handle.flush()
            os.fsync(handle.fileno())
    except FileExistsError:
        if not _migration_complete(path):
            raise RuntimeError('Developer migration marker is invalid.')
    except OSError as error:
        raise RuntimeError('Could not record developer-state migration safely.') from error


def initialize_developer_runtime(root=ROOT, *, home=None, cache=None, canonical_key=None):
    paths = developer_paths(root, home=home, cache=cache, canonical_key=canonical_key)
    _create_private_directory(paths['runtime'].parent)
    _create_private_directory(paths['runtime'])
    _create_private_directory(paths['cache'])
    for key in ('workspace', 'user_skills', 'credentials'):
        _check_directory(paths[key], private_root=paths['runtime'])
    for key in ('agent', 'agent_dist', paths['agent'] / 'node_modules',
                paths['agent'] / 'config', paths['agent'] / 'skills', 'app_skills'):
        path = paths[key] if isinstance(key, str) else key
        _check_directory(path, private_root=paths['cache'])

    _stage_tree(paths['source_agent_dist'], paths['agent_dist'], cache_root=paths['cache'])
    _copy_file_atomically(paths['source_agent_package'], paths['agent_package'], mode=0o600, replace=True)
    _stage_tree(paths['source_commander'], paths['agent_commander'], cache_root=paths['cache'])
    _copy_file_atomically(paths['source_agent_config_template'], paths['agent_config_template'], mode=0o600, replace=True)
    _stage_tree(paths['source_agent_skills'], paths['agent_skills'], cache_root=paths['cache'])
    if paths['source_agent_version'].is_file() and not paths['source_agent_version'].is_symlink():
        _check_directory(paths['agent_version'].parent, private_root=paths['cache'])
        _copy_file_atomically(paths['source_agent_version'], paths['agent_version'], mode=0o600, replace=True)
    _stage_tree(paths['source_app_skills'], paths['app_skills'], cache_root=paths['cache'])
    paths['key_available'] = _refresh_key_mirror(paths['source_key'], paths['key_file'], private_root=paths['runtime'])

    marker = paths['migration_marker']
    # Validate before seeding so an invalid marker never causes repeated import
    # of legacy files into a runtime that the user has already changed.
    migrated = _migration_complete(marker)
    if not migrated:
        _seed_missing_tree(paths['source_runtime'], paths['runtime'], private_root=paths['runtime'])
        _seed_missing_tree(paths['source_workspace'], paths['workspace'], private_root=paths['runtime'])
        safe_path = _safe_path(root, os.environ.get('PATH', ''))
        node = _managed_node(root, safe_path)
        _migrate_default_paths(paths['runtime'] / 'shell.json', paths, root, node)
        _write_migration_marker(marker)
    return paths


def environment(root=ROOT, *, paths=None, base_env=None, key_available=None):
    paths = paths or developer_paths(root)
    env = dict(os.environ if base_env is None else base_env)
    secret_names = {
        'OPENAI_API_KEY', 'ANTHROPIC_API_KEY', 'GEMINI_API_KEY', 'GOOGLE_API_KEY',
        'GROQ_API_KEY', 'MISTRAL_API_KEY', 'XAI_API_KEY', 'OPENROUTER_API_KEY',
        'CLICKY_BRO_TOKEN', 'CLICKY_BRO_OPENAI_KEY', 'CLICKY_BRO_ANTHROPIC_KEY',
        'CLICKY_BRO_GEMINI_KEY', 'CLICKY_BRO_OPENROUTER_KEY', 'CLICKY_BRO_GROQ_KEY',
        'CLICKY_BRO_MISTRAL_KEY', 'CLICKY_BRO_XAI_KEY', 'CODEX_HOME',
        'CLICKY_BRO_SARVAM_KEY', 'ASSEMBLYAI_API_KEY', 'COMPOSIO_API_KEY',
        'ANTHROPIC_AUTH_TOKEN', 'CLAUDE_CODE_MESSAGING_TOKEN',
    }
    for key in list(env):
        if key.startswith('OPENCLICKY_') or key in secret_names:
            env.pop(key, None)
    env['CLICKY_BRO_HOME'] = str(paths['runtime'])
    env['CLICKY_BRO_USER_SKILLS_DIR'] = str(paths['user_skills'])
    safe_path = _safe_path(root, env.get('PATH', ''))
    env['PATH'] = safe_path
    if key_available is None:
        key_available = _read_validated_key(paths['key_file']) is not None
    if key_available:
        env['CLICKY_BRO_GEMINI_KEY_FILE'] = str(paths['key_file'])
    else:
        env.pop('CLICKY_BRO_GEMINI_KEY_FILE', None)
    return env


def prepare(root=ROOT, *, home=None, cache=None, canonical_key=None):
    paths = initialize_developer_runtime(root, home=home, cache=cache, canonical_key=canonical_key)
    return environment(root, paths=paths, key_available=paths['key_available'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=('build', 'test-native', 'launch', 'smoke-answer', 'smoke-voice', 'prepare'))
    args = parser.parse_args()
    env = prepare()
    if args.command in ('build', 'test-native'):
        command = ['xcodebuild', '-project', str(ROOT / 'app/macos/OpenClicky/OpenClicky.xcodeproj'),
                   '-scheme', 'OpenClicky', '-configuration', 'Debug', '-destination', 'platform=macOS,arch=arm64',
                   '-derivedDataPath', str(DERIVED),
                   '-clonedSourcePackagesDirPath', str(Path.home() / 'Library/Caches/clicky-bro/DerivedData/SourcePackages'), '-jobs', '2',
                   'CODE_SIGNING_ALLOWED=YES', 'CODE_SIGN_IDENTITY=-', 'DEVELOPMENT_TEAM=']
        if args.command == 'test-native':
            env['TEST_RUNNER_CLICKY_BRO_HOME'] = str(ROOT / '.local/runtime/native-tests')
            env.pop('CLICKY_BRO_GEMINI_KEY_FILE', None)
            env['TEST_RUNNER_CLICKY_BRO_GEMINI_KEY_FILE'] = ''
            command += ['test', '-only-testing:OpenClickyTests']
        else:
            command += ['build']
        return subprocess.call(command, cwd=ROOT, env=env)
    if args.command == 'prepare':
        print('Private developer runtime and staged agent assets are ready; credential contents remain private.')
        return 0
    if not BINARY.is_file():
        raise RuntimeError('Build the native app first: python3 scripts/dev.py build')
    if args.command == 'launch':
        # LaunchServices cannot reliably open redirected output in a Documents
        # FileProvider tree. Keep this developer log beside the generated cache.
        log = DERIVED.parent / 'development.log'
        fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        os.close(fd)
        # LaunchServices owns the GUI lifetime and recognizes this precise bundle.
        # Only nonsecret paths are passed as arguments; the key stays in its file.
        command = ['/usr/bin/open', '-n', '-a', str(BINARY.parents[2]),
                   '--stdout', str(log), '--stderr', str(log)]
        # LaunchServices inherits the caller's working directory; keeping that
        # directory under the checkout would leave the GUI app anchored in the
        # protected Documents tree even though its runtime is private.
        launch_working_directory = str(Path(env['CLICKY_BRO_HOME']) / 'workspaces/default')
        launch_env = dict(env)
        launch_env['PWD'] = launch_working_directory
        for name in ('CLICKY_BRO_HOME', 'CLICKY_BRO_GEMINI_KEY_FILE',
                     'CLICKY_BRO_USER_SKILLS_DIR', 'PATH'):
            command += ['--env', name + '=' + launch_env[name]]
        command += ['--env', 'PWD=' + launch_working_directory]
        subprocess.run(command, cwd=launch_working_directory, env=launch_env, check=True)
        print('Launched clicky-bro. Workspace window and menu-bar controls are available.')
        return 0
    flag = '--openclicky-answer-smoke' if args.command == 'smoke-answer' else '--openclicky-mac-voice-smoke'
    return subprocess.call([str(BINARY), flag], cwd=ROOT, env=env)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (OSError, RuntimeError, subprocess.CalledProcessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
