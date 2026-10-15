"""Integration tests for each CLI, using only Python's standard library.

NOTE_CLI_VARIANT selects powershell (default), pwsh, or cmd.
POWERSHELL_EXE optionally supplies a portable PowerShell executable.
"""

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
VARIANT = os.environ.get("NOTE_CLI_VARIANT", "powershell")


class NoteCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="note cli test ")
        self.addCleanup(self.temp.cleanup)
        self.cwd = Path(self.temp.name)
        self.db = self.cwd / ".notes" / "db"
        # Also exercise installation paths containing spaces and brackets.
        self.install = self.cwd / "tool [installed]"
        self.install.mkdir()
        for name in ("note.ps1", "note.cmd"):
            shutil.copy2(ROOT / name, self.install / name)

    def run_cli(self, *args, variant=None):
        variant = variant or VARIANT
        if variant in ("powershell", "pwsh"):
            command = [os.environ.get("POWERSHELL_EXE", variant), "-NoLogo",
                       "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                       "-File", str(self.install / "note.ps1"), *args]
        elif variant == "cmd":
            # Quote every test argument so cmd treats shell operators literally.
            # Embedded quotes/newlines have separate shell-specific syntax.
            if any('"' in arg or '\n' in arg for arg in args):
                self.skipTest("Use the PowerShell entrypoint for this quoting case")
            arguments = " ".join('"' + arg + '"' for arg in args)
            command = 'cmd.exe /d /s /c ""' + str(self.install / "note.cmd") + '" ' + arguments + '"'
        else:
            self.fail("Unknown NOTE_CLI_VARIANT: " + variant)
        return subprocess.run(command, cwd=self.cwd, capture_output=True,
                              encoding="utf-8", timeout=30)

    def add(self, text):
        result = self.run_cli("add", text)
        expected_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        self.assertEqual(result.stdout, expected_hash + "\n")
        self.assertEqual((self.db / expected_hash).read_bytes(), text.encode("utf-8"))
        return expected_hash

    def test_add_list_deduplicate_delete(self):
        text = "Einkaufsliste: Milch, Eier, Brot"
        note_hash = self.add(text)
        self.add(text)
        self.assertEqual(len(list(self.db.iterdir())), 1)
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, note_hash + "\t" + text + "\n")
        result = self.run_cli("delete", note_hash)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse((self.db / note_hash).exists())
        self.assertEqual(self.run_cli("list").stdout, "")

    def test_unicode(self):
        text = "Gr\u00fc\u00dfe aus K\u00f6ln \u2014 \u65e5\u672c\u8a9e \U0001f4dd"
        note_hash = self.add(text)
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, note_hash + "\t" + text + "\n")

    def test_multiple_words_are_joined_with_spaces(self):
        result = self.run_cli("add", "one", "two words", "three")
        text = "one two words three"
        note_hash = hashlib.sha256(text.encode()).hexdigest()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.db / note_hash).read_bytes(), text.encode())

    def test_leading_unicode_bom_is_note_content(self):
        text = "\ufeffnot an encoding marker"
        note_hash = self.add(text)
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, note_hash + "\t" + text + "\n")

    def test_storage_errors_return_failure(self):
        (self.cwd / ".notes").write_text("this is a file", encoding="utf-8")
        result = self.run_cli("add", "cannot save")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr.strip())

    def test_shell_characters_are_literal(self):
        self.add("it's $HOME; $(exit 99) & echo injected | < > ^ ! [text] -flag")
        self.assertEqual(len(list(self.db.iterdir())), 1)

    def test_multiline_text(self):
        text = "first line\nsecond line\n\n"
        note_hash = self.add(text)
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, note_hash + "\t" + text.rstrip("\n") + "\n")

    def test_list_sorts_by_hash(self):
        hashes = {self.add(text): text for text in ("z", "a", "m")}
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "".join(h + "\t" + hashes[h] + "\n" for h in sorted(hashes)))

    def test_empty_list_does_not_create_storage(self):
        result = self.run_cli("list")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertFalse(self.db.exists())

    def test_invalid_commands_and_missing_arguments(self):
        for args in ((), ("unknown",), ("ADD", "text"), ("add",), ("delete",)):
            with self.subTest(args=args):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, "")
                self.assertTrue(result.stderr.strip())
        self.assertFalse(self.db.exists())

    def test_missing_note(self):
        result = self.run_cli("delete", "0" * 64)
        self.assertEqual(result.returncode, 1)
        self.assertIn("no note with hash", result.stderr)
        self.assertFalse(self.db.exists())

    def test_delete_rejects_paths_wildcards_and_short_hashes(self):
        note_hash = self.add("keep this note")
        sentinel = self.cwd / ".notes" / "sentinel"
        sentinel.write_text("keep this file", encoding="utf-8")
        for invalid_hash in ("../sentinel", "..\\sentinel", "*", note_hash[:8], note_hash.upper()):
            with self.subTest(hash=invalid_hash):
                result = self.run_cli("delete", invalid_hash)
                self.assertEqual(result.returncode, 1)
                self.assertIn("invalid hash", result.stderr)
        self.assertTrue((self.db / note_hash).exists())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "keep this file")



if __name__ == "__main__":
    unittest.main()
