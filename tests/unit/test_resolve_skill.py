import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from resolve_skill import resolve


class ResolveSkillTest(unittest.TestCase):
    def test_positive_and_negative_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            skill = root / "demo-skill"
            skill.mkdir()
            (skill / "resolver.yaml").write_text(
                "name: demo-skill\n"
                "description: Demo workflow skill.\n"
                "triggers:\n"
                "  - demo trigger\n"
                "negative_examples:\n"
                "  - unrelated request\n"
                "expected_confidence: 0.75\n",
                encoding="utf-8",
            )
            self.assertEqual(resolve(root, "please run demo trigger")[0]["name"], "demo-skill")
            self.assertEqual(resolve(root, "unrelated request"), [])


if __name__ == "__main__":
    unittest.main()
