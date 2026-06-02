import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_pack import validate_pack


class ValidatePackTest(unittest.TestCase):
    def test_missing_skill_md_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors = validate_pack(Path(tmp) / "missing-pack")
        self.assertTrue(any("missing pack directory" in err for err in errors))

    def test_invalid_frontmatter_name_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            pack = Path(tmp) / "bad-name"
            (pack / "tests" / "unit").mkdir(parents=True)
            (pack / "tests" / "integration").mkdir(parents=True)
            (pack / "evals").mkdir()
            (pack / "SKILL.md").write_text("---\nname: Bad Name\ndescription: bad\n---\n\n# Bad\n", encoding="utf-8")
            (pack / "pack.json").write_text("{}", encoding="utf-8")
            (pack / "resolver.yaml").write_text("name: bad-name\ntriggers:\n  - bad\nexpected_confidence: 0.75\n", encoding="utf-8")
            (pack / "evals" / "skill_cases.jsonl").write_text("{}", encoding="utf-8")
            (pack / "evals" / "resolver_cases.jsonl").write_text("{}", encoding="utf-8")
            (pack / "evals" / "rubric.md").write_text("rubric", encoding="utf-8")
            errors = validate_pack(pack)
        self.assertTrue(any("invalid frontmatter name" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
