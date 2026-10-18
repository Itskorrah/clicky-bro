"""Offline tests for private developer runtime staging and migration."""
import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("dev", ROOT / "scripts/dev.py")
dev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dev)

TEST_KEY = "test-placeholder-" + "x" * 40
ROTATED_TEST_KEY = "rotated-placeholder-" + "y" * 40
LEGACY_TEST_KEY = "legacy-placeholder-" + "z" * 40


def write_json(path: Path, value, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    os.chmod(path, mode)


def write_key(path: Path, key: str, mode=0o600):
    write_json(path, {"api_key": key}, mode=mode)


class DeveloperRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name)
        self.root = self.base / "checkout"
        self.runtime = self.base / "Application Support/clicky-bro/development"
        self.cache = self.base / "Caches/clicky-bro/development"
        self.canonical_key = self.root / ".local/credentials/gemini.json"
        self._create_project_assets()
        self._create_legacy_state()
        write_key(self.canonical_key, TEST_KEY)
        self.paths = dev.developer_paths(
            self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
        )

    def tearDown(self):
        self.temp.cleanup()

    def _create_project_assets(self):
        assets = {
            "app/agent/dist/cli.js": "#!/usr/bin/env node\n// synthetic CLI fixture\n",
            "app/agent/dist/config.js": "// synthetic module\n",
            "app/agent/package.json": '{"name":"fixture-agent","type":"module"}\n',
            "app/node_modules/commander/index.js": "// synthetic commander\n",
            "app/node_modules/commander/package.json": '{"name":"commander"}\n',
            "app/node_modules/unrelated/index.js": "// must not be staged\n",
            "app/app-skills/teach/SKILL.md": "---\nname: teach\ndescription: fixture\n---\n",
            "app/config/codex-config.toml": "# staged Codex template\n",
            "app/skills/ModelInstructions.md": "# Model instructions fixture\n",
        }
        for relative, contents in assets.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
            path.write_text(contents, encoding="utf-8")
            os.chmod(path, 0o600)

    def _create_legacy_state(self):
        self.source_runtime = self.root / ".local/runtime/native"
        self.source_workspace = self.root / ".local/workspaces/default"
        old_cli = str(self.root / "app/agent/dist/cli.js")
        old_workspace = str(self.source_workspace)
        old_app_skills = str(self.root / "app/app-skills")
        write_json(self.source_runtime / "shell.json", {
            "cliCommand": ["node", old_cli],
            "workspace": old_workspace,
            "writableRoots": [],
            "answerSource": "gemini",
            "answerModels": {"gemini": "gemini-3.5-flash-lite"},
            "appSkillsPath": old_app_skills,
            "speechVoice": "mac",
            "customSetting": {"keep": True},
        })
        write_json(self.source_runtime / "logs/app.log", {"fixture": "safe log state"})
        # An old runtime copy must never revive a Gemini key after its canonical
        # source has been removed; that key is managed only by the validated mirror.
        write_key(self.source_runtime / "credentials/gemini.json", LEGACY_TEST_KEY)
        write_json(self.source_workspace / "helpers.json", {
            "helpers": [{"id": "saved-helper", "instruction": "fixture"}]
        })
        write_json(self.source_workspace / "runs.json", {
            "runs": [{"id": "fixture-run", "status": "completed", "message": "CLICKY_BRO_HELPER_OK"}]
        })

    def initialize(self):
        return dev.initialize_developer_runtime(
            self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
        )

    def test_stages_only_managed_agent_assets_and_rewrites_exact_defaults(self):
        paths = self.initialize()
        self.assertNotEqual(paths["runtime"].resolve(), self.root.resolve())
        self.assertEqual(paths["workspace"], self.runtime / "workspaces/default")

        settings = json.loads((paths["runtime"] / "shell.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["cliCommand"], ["node", str(paths["agent_dist"] / "cli.js")])
        self.assertEqual(settings["workspace"], str(paths["workspace"]))
        self.assertEqual(settings["appSkillsPath"], str(paths["app_skills"]))
        self.assertEqual(settings["customSetting"], {"keep": True})
        self.assertEqual(settings["answerModels"], {"gemini": "gemini-3.5-flash-lite"})

        self.assertEqual((paths["agent_dist"] / "cli.js").read_text(encoding="utf-8"),
                         (self.root / "app/agent/dist/cli.js").read_text(encoding="utf-8"))
        self.assertTrue(paths["agent_package"].is_file())
        self.assertTrue((paths["agent_commander"] / "index.js").is_file())
        self.assertTrue((paths["app_skills"] / "teach/SKILL.md").is_file())
        self.assertEqual(paths["agent_config_template"].read_text(encoding="utf-8"),
                         "# staged Codex template\n")
        self.assertEqual((paths["agent_skills"] / "ModelInstructions.md").read_text(encoding="utf-8"),
                         "# Model instructions fixture\n")
        self.assertFalse((paths["agent"] / "node_modules/unrelated").exists())

        # The migration copies, never moves, the source-of-truth state.
        original = json.loads((self.source_runtime / "shell.json").read_text(encoding="utf-8"))
        self.assertEqual(original["cliCommand"], ["node", str(self.root / "app/agent/dist/cli.js")])
        self.assertTrue(self.source_workspace.exists())

    def test_user_custom_node_is_preserved_while_managed_cli_path_is_rewritten(self):
        old_cli = str(self.root / "app/agent/dist/cli.js")
        custom_command = ["/opt/custom-node/bin/node", old_cli]
        custom_workspace = str(self.base / "personal-workspace")
        custom_skills = str(self.base / "personal-skills")
        write_json(self.source_runtime / "shell.json", {
            "cliCommand": custom_command,
            "workspace": custom_workspace,
            "appSkillsPath": custom_skills,
            "customSetting": "preserved",
        })

        paths = self.initialize()
        settings = json.loads((paths["runtime"] / "shell.json").read_text(encoding="utf-8"))
        self.assertEqual(settings["cliCommand"], [custom_command[0], str(paths["agent_dist"] / "cli.js")])
        self.assertNotEqual(settings["cliCommand"][0], "node")
        self.assertEqual(settings["workspace"], custom_workspace)
        self.assertEqual(settings["appSkillsPath"], custom_skills)
        self.assertEqual(settings["customSetting"], "preserved")

    def test_migration_is_one_time_and_does_not_resurrect_deleted_state(self):
        paths = self.initialize()
        migrated_runs = paths["workspace"] / "runs.json"
        migrated_helpers = paths["workspace"] / "helpers.json"
        self.assertTrue(migrated_runs.is_file())
        self.assertTrue(migrated_helpers.is_file())

        settings_path = paths["runtime"] / "shell.json"
        settings = json.loads(settings_path.read_text(encoding="utf-8"))
        settings["customSetting"] = {"userEdited": True}
        write_json(settings_path, settings)
        migrated_runs.unlink()
        migrated_helpers.unlink()

        again = dev.initialize_developer_runtime(
            self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
        )
        final_settings = json.loads((again["runtime"] / "shell.json").read_text(encoding="utf-8"))
        self.assertEqual(final_settings["customSetting"], {"userEdited": True})
        self.assertFalse((again["workspace"] / "runs.json").exists())
        self.assertFalse((again["workspace"] / "helpers.json").exists())
        self.assertTrue(again["migration_marker"].is_file())

    def test_key_mirror_is_private_refreshes_and_only_exports_its_path(self):
        paths = self.initialize()
        self.assertTrue(paths["key_available"])
        if os.name == "posix":
            self.assertEqual(stat.S_IMODE(paths["credentials"].stat().st_mode), 0o700)
            self.assertEqual(stat.S_IMODE(paths["key_file"].stat().st_mode), 0o600)
        self.assertEqual(json.loads(paths["key_file"].read_text(encoding="utf-8"))["api_key"], TEST_KEY)

        rotated = "rotated-placeholder-" + "y" * 40
        write_key(self.canonical_key, rotated)
        env = dev.prepare(
            self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
        )
        self.assertEqual(json.loads(paths["key_file"].read_text(encoding="utf-8"))["api_key"], rotated)
        self.assertEqual(env["CLICKY_BRO_GEMINI_KEY_FILE"], str(paths["key_file"]))
        self.assertNotIn(rotated, json.dumps(env))

    def test_invalid_or_missing_canonical_key_clears_stale_mirror_and_env_path(self):
        paths = self.initialize()
        self.assertTrue(paths["key_file"].is_file())

        invalid = "not a valid provider key"
        write_key(self.canonical_key, invalid)
        env = dev.prepare(
            self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
        )
        self.assertFalse(paths["key_file"].exists())
        self.assertNotIn("CLICKY_BRO_GEMINI_KEY_FILE", env)
        self.assertNotIn(invalid, json.dumps(env))

        write_key(self.canonical_key, TEST_KEY)
        dev.prepare(self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key)
        self.canonical_key.unlink()
        env = dev.prepare(
            self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
        )
        self.assertFalse(paths["key_file"].exists())
        self.assertNotIn("CLICKY_BRO_GEMINI_KEY_FILE", env)
        # A legacy runtime credential cannot be copied back after canonical deletion.
        self.assertFalse((paths["credentials"] / "gemini.json").exists())

    def test_key_file_and_parent_symlinks_are_rejected_without_reading_through(self):
        outside = self.base / "outside/gemini.json"
        write_key(outside, TEST_KEY)
        link_parent = self.root / ".local/credential-alias"
        link_parent.parent.mkdir(parents=True, exist_ok=True)
        link_parent.symlink_to(outside.parent, target_is_directory=True)
        linked_source = link_parent / "gemini.json"

        paths = dev.initialize_developer_runtime(
            self.root, home=self.runtime, cache=self.cache, canonical_key=linked_source
        )
        self.assertFalse(paths["key_available"])
        self.assertFalse(paths["key_file"].exists())
        self.assertEqual(json.loads(outside.read_text(encoding="utf-8"))["api_key"], TEST_KEY)

        self.canonical_key.unlink()
        self.canonical_key.parent.mkdir(parents=True, exist_ok=True)
        self.canonical_key.symlink_to(outside)
        paths = dev.initialize_developer_runtime(
            self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
        )
        self.assertFalse(paths["key_available"])
        self.assertFalse(paths["key_file"].exists())
        self.assertEqual(json.loads(outside.read_text(encoding="utf-8"))["api_key"], TEST_KEY)

    def test_symlinked_or_insecure_destination_key_fails_closed(self):
        paths = self.initialize()
        external = self.base / "external-key.json"
        write_key(external, TEST_KEY)
        paths["key_file"].unlink()
        paths["key_file"].symlink_to(external)
        with self.assertRaises(RuntimeError) as raised:
            dev.initialize_developer_runtime(
                self.root, home=self.runtime, cache=self.cache, canonical_key=self.canonical_key
            )
        self.assertNotIn(TEST_KEY, str(raised.exception))
        self.assertEqual(json.loads(external.read_text(encoding="utf-8"))["api_key"], TEST_KEY)
        self.assertTrue(paths["key_file"].is_symlink())

    def test_environment_strips_supported_credentials_preserves_unrelated_values_and_never_logs_key(self):
        paths = self.initialize()
        inherited_secrets = (
            "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN",
            "CLAUDE_CODE_MESSAGING_TOKEN", "ASSEMBLYAI_API_KEY", "COMPOSIO_API_KEY",
            "CLICKY_BRO_SARVAM_KEY", "CLICKY_BRO_GEMINI_KEY", "GEMINI_API_KEY",
            "GOOGLE_API_KEY", "CODEX_HOME", "OPENCLICKY_PRIVATE_TEST",
        )
        base_env = {name: "synthetic-secret-value" for name in inherited_secrets}
        base_env.update({"PATH": f"/usr/bin{os.pathsep}{self.root / 'node_modules/.bin'}",
                         "LANG": "en_AU.UTF-8", "UNRELATED_TEST_SETTING": "kept"})
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            env = dev.environment(
                self.root, paths=paths, base_env=base_env, key_available=True
            )
        for name in inherited_secrets:
            self.assertNotIn(name, env)
        self.assertEqual(env["LANG"], "en_AU.UTF-8")
        self.assertEqual(env["UNRELATED_TEST_SETTING"], "kept")
        self.assertEqual(env["CLICKY_BRO_GEMINI_KEY_FILE"], str(paths["key_file"]))
        self.assertNotIn(TEST_KEY, json.dumps(env))
        self.assertNotIn("synthetic-secret-value", json.dumps(env))
        self.assertNotIn(TEST_KEY, stdout.getvalue() + stderr.getvalue())
        self.assertNotIn("synthetic-secret-value", stdout.getvalue() + stderr.getvalue())
        self.assertNotIn(str(self.root), env["PATH"])


if __name__ == "__main__":
    unittest.main()
