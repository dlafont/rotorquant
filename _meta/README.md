# _meta

This folder holds support material for `PRJ-rotorquant` that is not part of the
main working source tree.

## Purpose

I keep this folder for handoff notes, copied session logs, local archive
artifacts, and other project support files that help me continue work without
mixing them into source code or build output.

## What Belongs Here

- copied Codex chat sessions
- handoff summaries and checkpoint notes
- local archive material that should stay with this project
- project-specific support files that are not part of the runtime codebase

## What Does Not Belong Here

- source code
- tests
- build output
- generated benchmark results
- local dependency checkouts

Those should stay in the normal project folders such as `scripts/`, `tests/`,
`tools/`, or the project root when they are active working files.

## How I Distinguish Files

The main rule is location first, filename second.

- Files under `_meta/Codex_chat_copies/` are copied chat logs or session
  transcripts.
- Files with names like `handoff`, `checkpoint`, `archive`, or `summary` are
  usually support material, but they still need to live in the right folder.
- Active project instructions stay at the project root when they are meant to
  guide the current work, such as the benchmark TODO for this repo.

So, in practice:

- `TODO-kv-cache-benchmark-automation.md` stays at the project root because it
  is active working context for this repo.
- `_meta/Codex_chat_copies/Clone_and_compile_rotoquant_project_chat.md` is a
  copied session transcript because it lives inside the chat-copy folder.

## Current Convention

- `Codex_chat_copies/` = copied chat logs and session history
- root `_meta/` files = project support notes when needed
- project root = live instructions and active work items

Current continuation handoff:

- `Codex_chat_copies/RotorQuant_next_steps_handoff_2026-06-24.md`

If I add more handoff material later, I should put it here instead of scattering
it around the root folder.
