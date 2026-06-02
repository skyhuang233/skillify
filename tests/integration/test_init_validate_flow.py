import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class InitValidateFlowTest(unittest.TestCase):
    def test_generated_pack_passes_quality_gate_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            manifest = tmp / "manifest.json"
            manifest.write_text(
                json.dumps(
                    {
                        "name": "demo-skill",
                        "description": "Demo skill for the skillify integration test.",
                        "triggers": ["demo trigger"],
                        "negative_examples": ["not demo"],
                        "resources": ["scripts"],
                        "workflow": ["Run the demo workflow.", "Verify the result."],
                    }
                ),
                encoding="utf-8",
            )
            commands = [
                [sys.executable, str(ROOT / "scripts" / "init_pack.py"), str(manifest), "--root", str(tmp)],
                [sys.executable, str(ROOT / "scripts" / "validate_pack.py"), str(tmp / "demo-skill")],
                [sys.executable, str(ROOT / "scripts" / "run_llm_eval.py"), str(tmp / "demo-skill")],
                [sys.executable, str(ROOT / "scripts" / "run_pack_tests.py"), str(tmp / "demo-skill")],
            ]
            for command in commands:
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
