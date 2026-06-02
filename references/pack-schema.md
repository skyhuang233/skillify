# skillify Pack Schema

Use this reference when creating or updating a skill pack.

## Manifest Input

`scripts/init_pack.py` accepts a JSON manifest:

```json
{
  "name": "my-skill",
  "description": "What the skill does and when it should be used.",
  "triggers": ["skillify it", "turn this workflow into a skill"],
  "negative_examples": ["unrelated request"],
  "resources": ["scripts", "references", "assets"],
  "workflow": ["Step one.", "Step two."]
}
```

Rules:

- `name` must be lowercase letters, digits, and hyphens only.
- `description` must explain both the capability and when to use it.
- `triggers` should include exact user phrases.
- `negative_examples` should include likely false positives.
- `resources` is optional; create only folders the pack really needs.
- `workflow` is optional; if absent, a minimal workflow is generated.

## pack.json

`pack.json` records package metadata and quality-gate status:

```json
{
  "schema_version": 1,
  "name": "my-skill",
  "description": "Reusable capability summary.",
  "resources": ["scripts"],
  "status": {
    "unit": "pending",
    "integration": "pending",
    "llm_eval": "pending",
    "resolver_eval": "pending"
  }
}
```

## resolver.yaml

The local resolver supports a small YAML subset:

```yaml
name: my-skill
description: Reusable capability summary.
triggers:
  - exact trigger phrase
  - another trigger
negative_examples:
  - false positive phrase
expected_confidence: 0.75
```

Use exact phrases for high-confidence triggers. Add negative examples for adjacent
skills or common ambiguous wording.

## Eval Files

`evals/skill_cases.jsonl` requires:

```json
{"id":"skill-smoke","input":"user request","expected_behavior":"what a correct agent should do","must_include":["important term"]}
```

`evals/resolver_cases.jsonl` requires:

```json
{"id":"resolver-positive","query":"user request","expected":"my-skill"}
{"id":"resolver-negative","query":"unrelated request","expected":null}
```

`evals/rubric.md` describes scoring criteria for future provider-backed LLM evals.

## Registry

`registry.json` is the single data source for the HTML report:

```json
{
  "schema_version": 1,
  "generated_at": "",
  "skills": [
    {
      "name": "my-skill",
      "description": "Summary.",
      "path": "C:\\Users\\name\\.codex\\skills\\my-skill",
      "triggers": ["trigger"],
      "status": {
        "unit": "pass",
        "integration": "pass",
        "llm_eval": "pass",
        "resolver_eval": "pass"
      },
      "summary": "Short report text."
    }
  ]
}
```
