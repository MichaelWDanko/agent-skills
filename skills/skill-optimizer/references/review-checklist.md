# Skill Review Checklist

Load this reference when completing a partial skill or performing a broad optimization. Apply judgment rather than turning every item into a required ceremony.

## Review order

Address issues in this order:

1. **Blocker:** The skill is unsafe, invalid, unusable, or missing behavior required for its main task.
2. **Major:** Common requests, important branches, triggering, or vendor compatibility are unreliable.
3. **Minor:** Context waste, duplication, stale guidance, or maintainability friction remains.

Do not equate length with quality. Keep detail that prevents meaningful errors and remove detail the agent can infer reliably.

## Review checks

### 1. Discoverable

- Make the frontmatter description state what the skill does and when it should trigger.
- Use realistic user intent and relevant artifacts, not a long keyword list.
- Cover adjacent near-misses so keyword overlap does not trigger an unsupported workflow.

### 2. Complete routes

- Give every supported request a clear path from trigger to result.
- State decision criteria and fallbacks for meaningful conditional branches.
- Keep focused requests narrow.
- Preserve useful behavior from an existing or partial artifact unless the user authorizes its removal.

### 3. Lean context

- Keep only shared behavior and routing in `SKILL.md`.
- Move detail only when a task can avoid loading it. Splitting files that normal work always reads does not improve context use.
- Link every instruction-bearing reference directly from `SKILL.md` and say when to load it.
- Avoid background explanations and general knowledge the agent already has.

### 4. One source of truth

- Give each durable rule, schema, identifier, example, or table one canonical home.
- Replace repeated instructions with a pointer rather than a paraphrased copy.
- Keep current status, open items, and dated project state in the system that owns them.

### 5. Appropriate resources and freedom

- Use guidance for judgment-heavy work.
- Use structured steps when sequence matters.
- Use a script when exactness, reliability, or repeated code matters, and execute it on a representative case.
- Include a reference or asset only when a repeated workflow consumes it.

### 6. Safe and maintainable

- Make external effects, destructive actions, approval boundaries, and unavailable-capability fallbacks explicit when relevant.
- Exclude credentials, private configuration, customer data, and surprising behavior.
- Follow the target repository's layout, style, and validation instructions.

### 7. Compatible across target vendors

Use [vendor-compatibility.md](vendor-compatibility.md) for the bundled Codex and Claude baseline. Confirm semantic parity yourself; use native creators and validators as additional evidence when available.

Different metadata formats are expected. Different capabilities or conditional behavior require an explicit decision.

### 8. Evidence

Always run repository-required structural checks. Add realistic scenarios in proportion to risk:

- a common request
- an important branch or edge case
- a near-miss that should not trigger or should route elsewhere
- an unavailable-capability case when tools or runtimes are required

Use independent forward tests or baseline comparisons only when they can reveal a meaningful regression or quality difference. Keep test inputs free of the intended answer and avoid external side effects without approval.

## Completion check

A skill is ready when its main behaviors and branches are executable, its context structure is justified, each target vendor has an honest validation status, and remaining uncertainty is visible to the user.
