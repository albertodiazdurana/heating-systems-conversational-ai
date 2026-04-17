# BL-003: Streamlit boot crashes on Python 3.11.0rc1 with asyncio.InvalidStateError

**Status:** Open
**Priority:** Medium
**Date Created:** 2026-04-18
**Origin:** Sprint 1 step 11 manual smoke test (Session 5, 2026-04-18 00:09 local time)
**Author:** Alberto Diaz Durana

---

## Problem Statement

`streamlit run app.py` aborts at startup with an internal Streamlit
runtime error before any UI is rendered:

```
asyncio.exceptions.InvalidStateError: invalid state
  File "/home/berto/_projects/heating-systems-conversational-ai/.venv/lib/python3.11/site-packages/streamlit/runtime/runtime.py", line 631, in _loop_coroutine
    async_objs.started.set_result(None)

Please report this bug at https://github.com/streamlit/streamlit/issues.
Aborted!
```

This blocks Sprint 1 §6 exit-criterion box "`streamlit run app.py` starts
without error", even though the agent itself works end-to-end (smoke test
5/5 PASS via direct `build_agent()` invocation, see
`dsm-docs/handoffs/2026-04-17_s5_step11_smoke_test_results.md`).

## Diagnosis

### Probed facts (Session 5)

- **Python version:** 3.11.0**rc1** (release candidate, not 3.11.0 final).
  This is the WSL Ubuntu system Python from before Python 3.11.0 GA.
- **Streamlit version:** 1.56.0
- **Behavior outside Streamlit runtime:** all imports, agent
  construction, and 5/5 smoke queries work cleanly via direct
  `build_agent()` invocation. The crash is purely in Streamlit's own
  `_loop_coroutine` startup sequence.

### Root cause hypothesis

Python 3.11.0rc1 had several asyncio race-condition issues that were
fixed in Python 3.11.0 final and subsequent 3.11.x patches. The error
`InvalidStateError: invalid state` on `Future.set_result()` is a
documented asyncio race the 3.11 release notes mention fixing.

Streamlit emits "Please report this bug" because Streamlit's own
developers do not expect this state in their `_loop_coroutine`. The most
likely cause is the unsupported Python version, not a Streamlit bug.

## Proposed Solution

Two-step fix, in order:

### Step 1 (this BL): Upgrade Python in the venv

Replace the current `.venv` (built on Python 3.11.0rc1) with one built on
Python 3.11.x final or Python 3.12. Recommended: Python 3.12.x (most
recent stable, all 3.11 asyncio fixes included).

Commands (in WSL):
```bash
# Install Python 3.12 via apt or pyenv
sudo apt install python3.12 python3.12-venv  # or use pyenv

# Recreate venv
rm -rf .venv
python3.12 -m venv .venv
.venv/bin/pip install -e .

# Re-test
.venv/bin/streamlit run app.py
```

### Step 2 (conditional): Report upstream IF the bug reproduces

If `streamlit run app.py` still crashes with the same `InvalidStateError`
on Python 3.11.x or 3.12 (i.e., the rc1 hypothesis is wrong):

1. Build a minimal repro (likely just `import langchain`/`langgraph`
   then `streamlit run minimal.py`)
2. File at https://github.com/streamlit/streamlit/issues with: Streamlit
   version, Python version, OS, full traceback, minimal repro

If the bug does NOT reproduce after the venv upgrade, no upstream report
is needed. The decision deferred to Step 1's outcome.

## Success Criteria

- [ ] `.venv` recreated on Python 3.11.x or 3.12 (not rc1)
- [ ] `.venv/bin/streamlit run app.py` starts without error and renders
      the chat input in a browser
- [ ] All 55 unit tests + smoke test 5/5 still pass on the new venv
- [ ] Sprint 1 §6 box "`streamlit run app.py` starts without error" can
      finally be checked
- [ ] (Conditional) If bug reproduces on supported Python: minimal repro
      filed at streamlit/streamlit GitHub Issues with link in this BL

## Scope

Sprint 3 polish item per the original Sprint 1 plan §7 deferred list
(Streamlit polish). Could be Sprint 2 prep if a working UI is needed
to demo Sprint 2 RAG progress.

## Untracked files

None. The fix touches `.venv/` (gitignored) only. No backwards-
compatibility shims needed in committed code.

## Notes

The agent layer (LangGraph + tools + Ollama) is fully working. This BL
only blocks the Streamlit UI layer. For development and demos, the smoke
runner (`scripts/smoke_test.py`) provides a working end-to-end test path.
