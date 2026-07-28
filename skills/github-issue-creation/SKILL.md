---
name: github-issue-creation
description: Create GitHub issues from any working directory, infer the target repository from local git context or github-issues.yml, attach issues to GitHub Projects when configured, and help projects create or update their github-issues.yml issue-creation config.
---

# GitHub Issue Creation

Use this skill when the user wants to create a GitHub issue, draft a GitHub issue for creation, attach an issue to a GitHub Project board, or set up project-local issue defaults with `github-issues.yml`.

Keep the workflow generic. Do not hardcode product names, repo families, labels, project boards, or routing rules in this skill. Put project-specific behavior in `github-issues.yml`.

## Core workflow

1. Resolve the issue context before creating anything.
   - Run `scripts/resolve_issue_context.py --cwd "$PWD" --issue-text "<user request>"` when local context matters.
   - If the user names an explicit repo, pass it as `--explicit-repo owner/repo`.
2. Draft a focused issue title and Markdown body from the user's request.
   - Use config defaults for labels, assignees, milestone, project, and body guidance.
   - If required fields are ambiguous, ask before creating an externally visible issue.
3. If project attachment is configured, preflight GitHub CLI auth before issue creation.
   - Run `gh auth status`.
   - If auth fails or project access is missing, stop before creating the issue and tell the user to run `gh auth refresh -s project`.
4. Create the issue.
   - Prefer the GitHub connector `_create_issue` when available.
   - Use `repository_full_name`, `title`, `body`, `labels`, `assignees`, and `milestone` from the resolved context.
   - If the connector is unavailable, fall back to `gh issue create --repo OWNER/REPO --title TITLE --body BODY` plus labels, assignees, and milestone as needed.
5. If project attachment is configured, attach the created issue URL directly:

```sh
gh project item-add <project_number> --owner <project_owner> --url <issue_url>
```

Report the issue URL, repository, project attachment result, and any skipped optional defaults. Never imply the issue is on a project board unless the attachment command succeeded or the user explicitly chose an auto-add-only workflow.

## Repository resolution

Search from the current directory upward for `github-issues.yml`.

Resolution precedence:

1. Explicit repo in the user request.
2. `repository` in the nearest `github-issues.yml`.
3. Current git repo `origin` remote.
4. Parent workspace `routing` from the nearest `github-issues.yml`.
5. Ask the user if still ambiguous.

For non-git parent workspaces, the resolver can discover child git repos and use `routing` hints from `github-issues.yml`. If multiple routes match equally well, ask the user.

## `github-issues.yml`

Use `github-issues.yml` for project-local defaults. YAML is preferred over Markdown because these values are configuration, not long-form documentation.

Supported fields:

```yaml
repository: owner/repo

labels:
  - enhancement

assignees:
  - "@me"

milestone: null

project:
  owner: owner-or-org
  number: 1

routing:
  api: owner/api-repo
  ios: owner/ios-repo
  android: owner/android-repo
  docs: owner/product-repo

issue:
  body_guidance: |
    Include acceptance criteria when the request has enough detail.
    Keep the issue focused on one deliverable.
```

Notes:

- `repository` should be `owner/repo`.
- `labels` and `assignees` are optional lists.
- `milestone` is optional and should be a milestone number when using the connector.
- `project.owner` is the GitHub user or organization that owns the Project.
- `project.number` is the Project v2 number shown in the project URL.
- `routing` maps words or short domains to repositories for parent workspaces.
- `issue.body_guidance` gives local writing preferences for the issue body.

## Config authoring workflow

Use this skill when the user asks to create, update, or get guidance for `github-issues.yml`.

1. Inspect the current directory first.
   - If inside a git repo, read the `origin` remote and default `repository` to that repo.
   - If in a parent folder, discover immediate child git repos and suggest `routing` entries.
2. Start from `templates/github-issues.yml`.
3. Fill only verified stable values.
   - Do not invent labels, assignees, milestones, project owners, or project numbers.
   - Leave unknown optional values as commented examples or `null`.
4. If the user does not know the Project owner or number, explain:
   - For a user project URL like `https://github.com/users/octocat/projects/7`, owner is `octocat` and number is `7`.
   - For an organization project URL like `https://github.com/orgs/acme/projects/7`, owner is `acme` and number is `7`.

## Helper script

`scripts/resolve_issue_context.py` provides deterministic context resolution and config suggestions.

Examples:

```sh
python3 scripts/resolve_issue_context.py --cwd "$PWD" --issue-text "Add API pagination"
python3 scripts/resolve_issue_context.py --cwd "$PWD" --explicit-repo owner/repo
python3 scripts/resolve_issue_context.py --cwd "$PWD" --suggest-config
```

The script does not create issues or write files. It only prints JSON or a suggested YAML config.

## Safety

- Creating issues and adding project items are externally visible. Confirm the resolved target when user intent is incomplete.
- If project attachment is required but cannot be preflighted, pause before issue creation.
- Do not include secrets, tokens, private keys, or sensitive customer/user data in issue titles or bodies.
