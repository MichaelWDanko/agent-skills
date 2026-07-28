---
name: skill-optimizer
description: "Review, complete, and optimize partial or existing agent skills. Use when someone provides a skill folder, SKILL.md, or substantial draft and wants a technical review, needs to repair an incomplete skill, or wants to improve triggering, conditional routing, context management, progressive disclosure, deduplication, maintainability, validation, or compatibility across Codex, ChatGPT, Claude, and other skill-capable agents."
---

# Skill Optimizer

Produce a well-crafted skill whose intent is clear, conditional paths are explicit, context loads only when needed, and each durable rule has one source of truth.

## Working stance

- Assume the user is an agentic workflow SME unless they identify otherwise. Adapt explanations to their demonstrated skill-authoring experience.
- Inspect the conversation and available artifacts before asking questions. Reflect what is already clear, then ask only the one to three questions whose answers materially change the design.
- Treat the exchange as a working conversation, not an intake form. Offer a recommended default or example when useful, and proceed with explicit low-risk assumptions when more interviewing has little value.
- Treat repository and workspace context as technical evidence only. Do not infer an organization, business workflow, team, or ownership model from paths, neighboring skills, tools, or user identity.
- Preserve an existing skill's name and supported behavior unless the user authorizes a semantic change.
- Keep confidential data, credentials, customer details, and live operational state out of reusable skills.

## Scope from the evidence

Do not ask the user to select a process:

- If there is no usable skill artifact, route the request to the platform's native skill creator. Do not run a creation interview here.
- For notes, fragments, or an incomplete skill, preserve useful content, resolve material gaps, and optimize the smallest usable version.
- For a working skill with a broad request, establish its behavior baseline, audit it, and make the smallest effective refactor.
- For a focused request, inspect only the requested surface and dependencies required for correctness.
- For review-only work, return findings and a proposed target without editing.

Treat an artifact as usable when it states the intended capability and at least one trigger, workflow step, or constraint. Otherwise route it to the skill creator.

When uncertain, preserve what exists and choose the least destructive useful scope.

## Workflow

1. Read repository instructions and inventory the files, resources, and current behavior before changing anything.
2. Summarize a compact behavior baseline from available evidence, then ask only for missing information that blocks a safe or useful result:
   - what the skill enables and when it should trigger
   - expected inputs and outputs
   - important decisions, branches, and non-goals
   - safety or autonomy boundaries
   - evidence that would prove it works
3. For a partial artifact or broad optimization, read [references/review-checklist.md](references/review-checklist.md), review the portable behavior, and design the smallest structure that satisfies the baseline. For focused work, skip the full checklist unless the requested change depends on it.
4. Create or update only what the request needs:
   - keep shared rules and routing in `SKILL.md`
   - move genuinely task-specific detail into directly linked references
   - use scripts for fragile or repeatedly rewritten operations
   - use assets only for files consumed by the output
   - give every durable fact one canonical home
   Explain intentional behavior changes and do not silently discard useful source content.
5. When the work targets more than one vendor or changes vendor-facing files, read [references/vendor-compatibility.md](references/vendor-compatibility.md) and apply its offline checks.
6. Validate structure and realistic behavior, then review the final diff for intent drift, duplication, dangling references, stale state, and accidental vendor coupling. Use a common case, an important branch or edge case, and a near-miss when the scope warrants scenario testing.

## Vendor responsibility

Keep one provider-neutral behavioral core. Default compatibility targets to Codex, supported ChatGPT skill surfaces, and Claude unless the user or repository narrows them.

- Use the bundled compatibility standard to review OpenAI and Claude outputs even when only one vendor's tools or skills are available at runtime.
- Own the cross-vendor compatibility review. Confirm that required behavior, triggers, resources, links, and conditional paths remain usable on every target.
- Use available native creator, validator, or packaging tools to check current vendor syntax. Fall back to the bundled static rules when those tools are unavailable.
- Compare all vendor outputs against the same behavior baseline. Vendor-specific metadata may differ in form without changing the skill's capability.
- Distinguish portable review, bundled static checks, and native validation in the report. A missing native tool does not prevent an offline compatibility review, but it must not be reported as native validation.

## Report

Return only what helps the user evaluate the result:

- material findings and their resolution
- the resulting or proposed file tree
- behavior intentionally changed or explicitly preserved
- cross-vendor compatibility and native validation status
- remaining evidence gaps or decisions

For a focused request, report the relevant subset and confirm that broader behavior was not changed.
