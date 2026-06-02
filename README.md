# skillify

Turn a working agent workflow into a reusable, tested, cross-agent skill pack.

`skillify` is a SKILL.md-based agent skill for preserving workflows that have
already worked once. When you say "skillify it" or "把它技能化", the agent can
convert the workflow into a small skill pack with documentation, minimum code,
tests, offline eval fixtures, resolver metadata, resolver eval cases, and an
interactive HTML registry report.

## What It Creates

Each generated skill pack uses this shape:

```text
<skill-name>/
  SKILL.md
  pack.json
  resolver.yaml
  tests/
    unit/
    integration/
  evals/
    skill_cases.jsonl
    resolver_cases.jsonl
    rubric.md
```

Optional folders are created only when useful:

- `scripts/` for deterministic code
- `references/` for detailed guidance loaded on demand
- `assets/` for templates or output resources

## Install

Clone this repository into your agent's skills directory.

Codex:

```powershell
git clone https://github.com/skyhuang233/skillify.git C:\Users\21340\.codex\skills\skillify
```

Claude Code:

```powershell
git clone https://github.com/skyhuang233/skillify.git C:\Users\21340\.claude\skills\skillify
```

For portable locations, replace the destination with your own skills directory,
for example `~/.codex/skills/skillify` or `~/.claude/skills/skillify`.

## Use

After an agent completes a workflow that you want to preserve, ask:

```text
skillify it
```

or:

```text
把它技能化
```

The skill guides the agent through:

1. Extracting the reusable behavior.
2. Creating a pack manifest.
3. Writing `SKILL.md` and any minimum scripts/references/assets.
4. Adding unit tests, integration tests, eval fixtures, and resolver metadata.
5. Running validation and updating the HTML registry report.

## Scripts

All scripts use Python standard library only.

```powershell
python scripts\init_pack.py manifest.json --root C:\Users\21340\.codex\skills
python scripts\validate_pack.py C:\Users\21340\.codex\skills\<skill-name>
python scripts\run_pack_tests.py C:\Users\21340\.codex\skills\<skill-name>
python scripts\run_llm_eval.py C:\Users\21340\.codex\skills\<skill-name>
python scripts\resolve_skill.py --root C:\Users\21340\.codex\skills --query "skillify it"
python scripts\build_report.py registry.json skillify-report.html
```

When using Claude Code, replace `C:\Users\21340\.codex\skills` with
`C:\Users\21340\.claude\skills` in commands that target generated packs.

Use `PYTHONDONTWRITEBYTECODE=1` during verification if you want to avoid
`__pycache__` files.

## Report

`registry.json` is the data source for the static HTML report.

Generate it with:

```powershell
python scripts\build_report.py registry.json skillify-report.html
```

Open `skillify-report.html` in a browser to search and filter registered skill
packs by status.

## Included Test Pack

This repository includes `skillify` itself as a validated pack in `registry.json`.
The registry may also list local packs created while testing; those entries are
report metadata, not required dependencies.

## Validation

Run these checks before publishing changes:

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONDONTWRITEBYTECODE='1'
python C:\Users\21340\.codex\skills\.system\skill-creator\scripts\quick_validate.py .
python scripts\validate_pack.py .
python scripts\run_pack_tests.py .
python scripts\run_llm_eval.py .
```

`PYTHONUTF8=1` is useful on Windows when validating files that contain Chinese
trigger phrases.
