---
name: tether-release
description: Cut and publish a new Tether iOS release with the repository-specific release flow. Use when preparing an App Store or TestFlight release for Tether, bumping the app version or build number, creating the release branch and tag, running the release script, or verifying that the shipped app version is represented in GitHub.
---

# Tether Release

## Overview

Use this skill only for the Tether app release workflow.

The source of truth for the release process is:
- `/Users/michaeldanko/Projects/Tether/scripts/testflight_release.sh`

Prefer following and improving that script over inventing ad hoc release steps.

## Preconditions

Before cutting a release:
- work in `/Users/michaeldanko/Projects/Tether`
- verify the tracked worktree is clean before any version bump
- confirm the branch you want to release from is the intended source branch
- do not hide unrelated local changes behind a version bump commit
- treat `Tether/Info.plist` version changes as release metadata that must be committed

If the worktree is not clean, stop and resolve that first.

## Release conventions

When a marketing version is provided:
- create branch `release/<version>`
- create tag `v<version>`
- ensure both refs are pushed to `origin`

The release branch and tag should represent the code that shipped, not just the plist bump.

## Workflow

### 1. Inspect release state

Check:
- current branch
- git status
- current `CFBundleShortVersionString`
- current `CFBundleVersion`
- whether `origin` exists and is reachable

Use exact values in the response.

### 2. Validate the release request

Confirm these inputs:
- marketing version, if changing
- build number
- whether upload should be skipped

If a version bump is requested, require a clean tracked worktree first.

### 3. Use the script, not a manual sequence

Run the release through:
- `/Users/michaeldanko/Projects/Tether/scripts/testflight_release.sh`

Examples:

```bash
scripts/testflight_release.sh --version 1.0.2 --build-number 6
scripts/testflight_release.sh --build-number 6 --skip-upload
```

Do not manually edit `Tether/Info.plist` for a real release unless you are fixing the script itself.

## Expected script behavior

For a versioned release, the script should:
1. require a clean tracked worktree
2. update `Tether/Info.plist`
3. create or switch into `release/<version>` as needed
4. commit the version metadata change
5. archive and export successfully before publishing release refs
6. create tag `v<version>`
7. push the release branch and tag to `origin`
8. upload to App Store Connect unless `--skip-upload` is set

If the script does not do this, fix the script before using manual workarounds.

## Guardrails

- Do not create a release branch from a dirty tracked worktree.
- Do not create a version bump commit that does not match the code being shipped.
- Do not push release refs before the archive or export path succeeds.
- Do not assume the release succeeded just because the plist changed.
- If upload is skipped, still ensure the branch and tag accurately capture the release candidate.

## Reporting

When finishing a Tether release task, report:
- current version and build
- release branch name
- release tag name
- whether refs were pushed to GitHub
- whether upload was performed or skipped
- any blockers or follow-up needed

## When to update this skill

Update this skill whenever the Tether release script changes meaningfully, especially around:
- branch naming
- tag naming
- version bump rules
- commit requirements
- export or upload gating
- App Store Connect tooling
