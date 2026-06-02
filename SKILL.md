---
name: skillify
description: >
  Cross-agent workflow-to-skill-pack builder. This skill should be used when the
  user asks to "skillify it", "把它技能化", "创建技能包", "把这次流程沉淀成 skill",
  "生成 skill pack", "turn this into a skill", or otherwise wants a working agent
  workflow converted into a reusable SKILL.md-based capability with minimum code,
  unit tests, integration tests, offline LLM eval fixtures, resolver metadata,
  resolver evals, and an interactive HTML registry report. Compatible with Codex,
  Claude Code, OpenCode, and OpenClaw style agent skills.
---

# skillify

Turn a workflow that has already worked once into a tested, reusable skill pack.

Use this skill after an agent has built or debugged something to a working state and
the user wants to preserve the procedure as a reusable capability. Keep the output
small: write only the documentation, code, tests, evals, and resolver metadata that
directly protect that capability.

## Workflow

1. Extract the reusable behavior.
   - Identify the concrete user trigger, successful workflow, required tools, and
     artifacts that made the original task work.
   - Separate deterministic steps from judgment-heavy steps. Deterministic steps
     belong in `scripts/`; judgment-heavy guidance belongs in `SKILL.md` or
     `references/`.

2. Create a pack manifest.
   - Use `scripts/init_pack.py` with a JSON manifest to create the skeleton.
   - Prefer short lowercase hyphenated names.
   - Include `scripts`, `references`, or `assets` only when the pack genuinely
     needs them.

3. Write the skill.
   - Put trigger phrases and "when to use" information in `SKILL.md` frontmatter.
   - Keep `SKILL.md` focused on the core workflow.
   - Move detailed patterns, schemas, and examples into `references/`.

4. Add quality gates.
   - Add unit tests for deterministic scripts.
   - Add integration tests for the representative end-to-end skill workflow.
   - Add `evals/skill_cases.jsonl`, `evals/resolver_cases.jsonl`, and
     `evals/rubric.md`.
   - Add `resolver.yaml` with positive triggers, negative examples, and an expected
     confidence threshold.

5. Verify and report.
   - Run `scripts/validate_pack.py <pack-dir>`.
   - Run `scripts/run_pack_tests.py <pack-dir>`.
   - Run `scripts/run_llm_eval.py <pack-dir>` in offline mode.
   - Run `scripts/resolve_skill.py --root <skills-root> --query "<user request>"`
     for representative resolver checks.
   - Update `registry.json`, then run `scripts/build_report.py registry.json`.

## Pack Shape

Every generated pack uses this base structure:

```text
<skill-name>/
  SKILL.md
  pack.json
  tests/
    unit/
    integration/
  evals/
    skill_cases.jsonl
    resolver_cases.jsonl
    rubric.md
  resolver.yaml
```

Optional folders:

- `scripts/` for deterministic code.
- `references/` for detailed material loaded only when needed.
- `assets/` for templates or files used in generated output.

## Scripts

- `scripts/init_pack.py`: create a skill pack from a manifest JSON.
- `scripts/validate_pack.py`: validate structure, frontmatter, eval files, and
  resolver metadata.
- `scripts/run_pack_tests.py`: run unit and integration tests with `unittest`.
- `scripts/run_llm_eval.py`: offline eval validation with a provider extension
  point for future model-backed scoring.
- `scripts/resolve_skill.py`: local resolver for all packs under a skills root.
- `scripts/build_report.py`: render `registry.json` into an interactive HTML
  report.

Read `references/pack-schema.md` for manifest, resolver, eval, and registry
formats before creating or modifying a pack.
