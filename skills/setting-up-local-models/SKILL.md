---
name: setting-up-local-models
description: Set up and maintain a portable ~/Models repo for local model servers, with per-model start/stop scripts, repo-level status checks, and safe public-repo ignores.
version: 1.0.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [models, local models, servers, git, macos, llama.cpp, mlx, conventional commits]
---

# Setting up local models

Use this skill when you are managing a portable `~/Models` repository that stores local model server scripts, lightweight docs, and per-model folders, while keeping model payloads out of git.

## When to use

- The user wants a repeatable folder layout for local models.
- The user wants one folder per model with stable script names.
- The user wants a repo-level status script that shows which model servers are running.
- The user wants a simple stop-all script that references existing per-model stop scripts.
- The user wants the repo to be safe to publish publicly.
- The user wants conventional commits used consistently.

## Core patterns

- One model per folder inside a family folder.
- Keep `start.sh` and `stop.sh` inside each model folder.
- Keep model weights, caches, logs, pid files, and generated metadata out of git.
- Use a top-level status script to check all known models.
- Use a top-level stop-all script to stop all known models by calling the existing per-model stop scripts.
- Keep README and `agents.md` updated whenever the layout changes.
- Use conventional commits for all repo changes: `type(scope): short summary`.

## Suggested layout

```text
~/Models/
├── README.md
├── agents.md
├── status_check_all_models.sh
├── stop_all_models.sh
├── .gitignore
├── mlx/
│   └── qwen3.5/
│       └── Qwen3.5-0.8B/
│           ├── start.sh
│           └── stop.sh
└── gguf/
    └── gemma4/
        ├── gemma-4-e4b-it-Q4_K_M/
        │   ├── start.sh
        │   └── stop.sh
        └── gemma-4-26B-A4B-it-Q4_K_M/
            ├── start.sh
            └── stop.sh
```

## Add a new model

1. Create a new folder under the correct family folder.
2. Put the model payload in that folder.
3. Add `start.sh` and `stop.sh` in that folder.
4. Update `status_check_all_models.sh`.
5. Update `stop_all_models.sh` if you want the new model included in bulk shutdown.
6. Update `README.md` and `AGENTS.md`.
7. Commit with a conventional commit message.

## Status and shutdown scripts

- `status_check_all_models.sh` should only report status.
- `stop_all_models.sh` should stay simple and call the existing per-model stop scripts.
- Avoid duplicating shutdown logic in multiple places if a model folder already has a stop script.

## Performance tuning passes

When the user wants to optimize a `llama-server` launch for a specific model:

1. Read the repo's optimization note first if it exists.
2. Inspect the model's `start.sh` and keep changes localized to that model folder.
3. Prefer explicit `llama-server` flags over hidden defaults so tuning stays easy to inspect.
4. Make flags overrideable with environment variables when practical.
5. Good first-pass knobs to test on Apple Silicon are:
   - `--parallel 1` to reduce per-slot cache footprint
   - an explicit `--ctx-size`
   - smaller `--batch-size` and `--ubatch-size` values
   - explicit `--gpu-layers` / Metal offload behavior
   - `--flash-attn auto` unless the hardware or logs suggest otherwise
6. Verify with `bash -n` and compare status before and after the change.

## External references

If a linked post or document is not directly readable in the browser, use a fallback search to recover the main hint rather than blocking the optimization pass. Keep the extracted guidance conservative and measurable.

## Iterative llama-server optimization

Use this when the user wants to tune a specific `llama-server` model for lower first-token latency or cleaner interactive behavior.

1. Keep changes localized to the target model folder.
2. Start with conservative, explicit flags rather than changing many things at once.
3. Benchmark with a short fixed prompt so results are comparable.
   - Prefer a tiny prompt like `Reply with exactly one word: banana`.
   - Measure first-token time and total request time.
   - Compare the first request after restart and a second request on the same server.
4. Test one candidate flag change at a time.
   - Common levers: `--parallel`, `--ctx-size`, `--batch-size`, `--ubatch-size`, `--gpu-layers`, `--flash-attn`, `--cont-batching`, `--reasoning`.
   - Keep defaults overrideable via env vars so the script stays easy to tune.
5. Watch for hidden reasoning output.
   - If a model returns `reasoning_content` instead of a visible answer for a simple prompt, try `--reasoning off` before touching more expensive settings.
6. Prefer the simplest config that produces the best measured result.
   - On Apple Silicon, full GPU offload plus a smaller context and `--parallel 1` can be a strong baseline.
   - Do not assume a flag helps just because it sounds faster; verify it.
7. Record the benchmark outcome in the optimization plan or model notes so future adjustments have a baseline.

## Conventional commits

Use this format:

```text
type(scope): short summary
```

Examples:
- `docs(models): add repo guide`
- `chore(models): remove legacy model tree`
- `feat(models): add model status script`
- `fix(models): update gemma server path`

## Public-repo safety

Before committing, verify that only safe files are tracked:

- `README.md`
- `agents.md`
- scripts
- other small documentation files

Do not commit model binaries, caches, logs, or pid files.
