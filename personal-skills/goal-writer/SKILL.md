---
name: goal-writer
description: "Turn weak, vague, or sprawling asks into one strong, portable, auditable goal prompt for AI agents. Use when the user wants help writing a goal, objective, completion condition, prompt, task brief, success criteria, or implementation review contract for Claude, Codex, or another agent conversation."
---

# Goal Writer

Create a goal prompt that another AI agent can execute and audit. Treat a good goal as a compact contract: what should be achieved, what evidence proves it, what constraints matter, and what to do if completion is blocked.

## Workflow

1. Identify the user's rough intent, target agent or platform, available context, and desired output.
2. Ask up to three clarifying questions only when missing details would materially change the goal. If the user likely wants speed, state reasonable assumptions and continue.
3. Convert the ask into a concrete end state with visible evidence an agent can surface in the conversation.
4. Add constraints, boundaries, and non-goals so the agent has freedom to choose tactics without drifting.
5. Define how the agent should handle blockers, partial success, and uncertainty.
6. Before emitting the answer, budget the entire response to stay under 4,000 characters total, including the prompt, labels, notes, and any usage guidance.
7. Output one ready-to-use goal prompt plus only the brief notes needed to explain material tradeoffs. Fold platform needs into the goal instead of making the user choose Claude, Codex, or review variants.

## Goal Anatomy

Prefer this portable structure:

```text
Goal:
<One concise sentence naming the desired end state.>

Context:
- <Facts, files, systems, links, or background the agent should use.>

Success criteria:
- <Observable criterion 1.>
- <Observable criterion 2.>
- <Observable criterion 3.>

Evidence to provide:
- <Commands run, tests passed, files changed, artifacts produced, research sources checked, or other proof the agent should report.>

Review standard:
- <How the agent should inspect the actual implementation, artifact, evidence, or source material before claiming completion.>

Constraints:
- <Things that must remain true, must not change, or must be handled carefully.>

Blocked or incomplete handling:
- <What to do if success is not currently reachable.>

Budget or stopping rule:
- <Optional turn, time, token, cost, or effort boundary.>
```

Omit sections that add no value. Keep the final goal short enough to paste into another conversation, but specific enough that a separate evaluator or user can tell whether it is done.

## Quality Bar

A strong goal usually has:

- One auditable end state, not a mood or broad direction.
- A verification surface, such as a test command, build result, artifact, checklist, source set, benchmark, empty queue, or final report.
- Constraints that prevent false success, such as preserving public API behavior, avoiding unrelated files, or labeling uncertainty.
- A bounded scope that gives the agent room to discover the path.
- A clear rule for blockers and partial completion.

Avoid goals that merely say "improve," "clean up," "research," "make better," or "finish this" without saying what finished means.

## Clarifying Questions

Ask questions when the weak input lacks one of these:

- Output: What artifact, decision, code change, report, plan, or answer should exist at the end?
- Evidence: How should the agent prove it is done?
- Constraints: What must not be changed, assumed, or overstated?
- Scope: Which files, systems, sources, users, or time period are in bounds?
- Risk: What should the agent do if it finds a blocker or conflicting evidence?

If asking questions, give the user a useful first draft too when possible. Mark unknowns with brackets so the user can fill them in.

## Universal Goal Design

Default to one platform-neutral goal. Do not ask the user to choose a platform. Do not emit separate Claude, Codex, and review prompts unless the user explicitly requests separate variants.

Make the goal work well in both transcript-evaluated and implementation-reviewed environments:

- Include transcript-verifiable proof: require the working agent to surface commands run, outputs observed, files changed, artifacts produced, sources checked, or blocker details in the conversation.
- Include implementation-review proof: require the agent to inspect the actual files, diffs, tests, logs, generated artifacts, or source evidence before declaring completion.
- Include a completion rule: the goal is not done until the evidence satisfies the success criteria and unresolved gaps are reported honestly.
- Include a stopping rule when the work could expand: time, turn, token, scope, or "stop and report blockers" boundaries.

Use this single-output shape:

```text
Goal:
<Outcome to achieve.>

Success criteria:
- <Observable criterion.>
- <Observable criterion.>

Evidence and review requirements:
- Surface the proof needed for a transcript evaluator to judge progress.
- Inspect the underlying implementation, artifact, files, tests, logs, or sources before claiming completion.
- Report changed paths, commands, outputs, sources, artifacts, and remaining gaps.

Constraints:
- <Important boundaries and non-goals.>

Blocked or incomplete handling:
- <What to report if the goal cannot be fully achieved.>
```

If the user explicitly asks for platform syntax, provide it only as a short usage note after the single goal, such as "For Claude, paste this after `/goal`." Do not rewrite the goal into a second version unless asked.

## Weak-to-Strong Patterns

Weak:

```text
Improve performance.
```

Strong:

```text
Goal:
Reduce p95 checkout latency below 120 ms on the local benchmark while keeping the correctness suite green.

Success criteria:
- The checkout benchmark reports p95 latency under 120 ms.
- The correctness test suite exits 0.

Evidence and review requirements:
- Benchmark command and final output.
- Test command and final output.
- Files or diffs inspected before claiming completion.

Constraints:
- Do not change public API behavior.
- Keep changes limited to the checkout performance path unless evidence shows another bottleneck.

Blocked or incomplete handling:
- If the benchmark cannot run, report the blocker, the attempted command, and the next concrete unblock step.
```

Weak:

```text
Write docs for this feature.
```

Strong:

```text
Goal:
Produce a user-facing docs page for the feature that explains its purpose, setup, usage, and two realistic examples.

Success criteria:
- The docs page exists in the project's documentation location.
- The local docs build passes.
- All commands and examples match current behavior.

Evidence and review requirements:
- File path created or edited.
- Docs build command and result.
- Any source files or commands checked for accuracy.

Constraints:
- Do not invent unsupported behavior.
- Mark any missing product decisions as open questions instead of guessing.
```

Weak:

```text
Research whether this paper can be reproduced.
```

Strong:

```text
Goal:
Produce the strongest evidence-backed reproduction assessment possible from the available paper, code, data, and local resources.

Success criteria:
- Inventory the paper's headline claims.
- Map each claim to available evidence or missing materials.
- Reproduce or approximate feasible claims with local checks.
- End with a report separating reproduced results, approximate support, blocked exact replay, and remaining uncertainty.

Evidence and review requirements:
- Sources inspected.
- Commands, notebooks, scripts, or calculations run.
- Claim-by-claim status table.

Constraints:
- Do not describe approximate trained replacements as exact reproduction.
- Be explicit about unavailable seeds, checkpoints, data, or implementation details.
```

## Output Requirements

When using this skill:

- Provide the ready-to-use goal prompt first.
- Produce one primary goal prompt by default.
- Do not ask the user to choose Claude, Codex, or review output types.
- Include platform-specific syntax or separate variants only when the user explicitly requests them.
- Keep the complete response under 4,000 characters total. If the draft would exceed the cap, shorten the goal prompt first, omit optional sections, and drop explanatory notes before removing necessary success criteria or evidence requirements.
- Keep explanatory notes brief and separate from the prompt.
- Preserve the user's actual intent; strengthen weak input without silently changing the job.
