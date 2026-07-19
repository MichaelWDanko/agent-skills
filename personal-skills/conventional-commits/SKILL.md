---
name: conventional-commits
description: "Draft, refine, and validate Git commit messages that follow Conventional Commits by choosing an accurate type, scope, and concise summary from the actual changes. Use when the user wants help naming a commit, wants a commit created, or wants commit history to stay consistent with `type(scope): summary`."
---

# Conventional Commits

Use this skill when the user wants a commit message written, reviewed, or applied in Conventional Commits format.

Ground the message in the actual changes. Inspect the diff or staged changes before deciding on the commit type or scope.

## Workflow

1. Review the modified or staged files before drafting the message.
2. Identify the primary purpose of the change.
3. Choose the narrowest useful scope.
4. Write a short imperative summary.
5. Add breaking-change markers only when the change really breaks an external contract, workflow, or interface.

## Message format

Use this default shape:

```text
type(scope): short summary
```

Examples:
- `docs(skills): reorganize skills repo`
- `feat(models): add status check script`
- `fix(auth): handle expired refresh tokens`
- `refactor(jira-story-writing): simplify issue draft flow`

If a scope does not add clarity, use:

```text
type: short summary
```

## Type selection

Choose the type based on the dominant effect of the change:

- `feat`: adds user-facing behavior or a new capability
- `fix`: corrects incorrect behavior or a regression
- `docs`: changes documentation, skill instructions, or other prose-only content
- `refactor`: restructures code or content without changing behavior
- `test`: adds or updates tests
- `build`: changes packaging, dependencies, or build tooling
- `ci`: changes automation or CI workflows
- `perf`: improves performance without changing behavior
- `chore`: repository maintenance that does not fit the types above

Do not default to `chore` when a more specific type fits.

## Scope selection

Use a short lowercase scope that points to the changed area:

- repository or domain area such as `skills`, `models`, or `ios`
- feature or package name such as `auth`, `billing`, or `jira-story-writing`
- omit the scope when the change is repo-wide and no single scope improves clarity

Prefer one scope. Do not cram multiple areas into the scope.

For this repository:

- prefer `skills` for repo-wide skill-library changes
- use a specific skill name such as `conventional-commits` or `jira-story-writing` when the commit is narrowly about one skill
- changes limited to skill instructions, references, or UI metadata are usually `docs`, not `feat`

## Summary rules

- keep it concise and specific
- use imperative mood
- do not end with punctuation
- describe what changed, not why you are happy about it
- avoid vague summaries such as `update files` or `misc cleanup`

Good:
- `docs(skills): add conventional commits skill`
- `fix(sync): retry missing meeting imports`

Weak:
- `chore: stuff`
- `fix: make changes`

## Breaking changes

Use a breaking marker only when needed:

```text
type(scope)!: short summary
```

Add a `BREAKING CHANGE:` footer when the impact needs explanation.

Examples:
- `feat(api)!: remove legacy session endpoint`
- `refactor(config)!: rename default model keys`

Do not mark a commit as breaking for internal cleanup that does not change an external contract.

## Multi-part changes

When one commit mixes unrelated changes, prefer splitting the work into separate commits before naming them.

If the work must stay together, choose the type that best reflects the main effect and mention the secondary detail only if it fits cleanly in the summary.

## Output requirements

When using this skill:

- provide one best commit message first
- include one or two alternates only when there is real ambiguity
- call out any assumption briefly if the diff was incomplete or unclear
- if asked to commit, use the chosen message exactly unless the user requests a change
