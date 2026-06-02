import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class BuildReportTest(unittest.TestCase):
    def test_report_contains_registry_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            registry = tmp / "registry.json"
            output = tmp / "report.html"
            registry.write_text(
                json.dumps({"schema_version": 1, "skills": [{"name": "demo", "description": "Demo"}]}),
                encoding="utf-8",
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build_report.py"), str(registry), str(output)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("demo", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
