## Contributing Guide

This document explains how we will contribute together in this project.

### Overview

- Everyone works on their own feature branch.
- We keep branches up to date with `main` often.
- We use pull requests (PRs) to merge code into `main`.
- We do **not** commit directly to `main`.

---

## Team Workflow (Quick Version)

1. Start from the latest `main`
2. Create a feature branch
3. Make small commits often
4. Merge `main` into your branch regularly
5. Open a Pull Request (PR) when your feature is ready
6. Get review, fix feedback, then merge PR into `main`

---

## Branch Rules

### 1) Never work directly on `main`

`main` should always stay stable.

### 2) One branch per feature

Use one branch for one feature.

Branch name examples:

- `feature/pathfinding-same-room`
- `feature/map-polyline-animation`
- `fix/start-end-validation`
- `docs/contributing-workflow`
- `simon/map-animation`

### 3) Keep branch scope small

Focus on one feature, don't edit across the whole codebase, smaller branches are easier to review, test, and merge.

---

## Session Git Routine

Run this flow every time you start and finish work.

### Start of session

```bash
git checkout main
git pull origin main # pull new commits from remote repository

# If starting new work
git checkout -b feature/short-description

# If continuing existing work
git checkout your-existing-branch
git merge main # merge stable features from main into your branch
```

### During session

- Commit often
- Keep commits focused on one idea
- Write clear commit messages

```bash
git add .
git commit -m "Add validation when start and end room match"
```

### End of session

```bash
git checkout main
git pull origin main # pulls latest changes from remote repo
git checkout your-branch-name # switch back to your branch
git merge main # merge updated main branch into your branch
git push -u origin your-branch-name   # first push, updates your branch to remote repository on GitHub
# later pushes can just be:
git push
```

---

## Why We Merge `main` Often

Regularly running `git merge main` in your branch helps:

- Catch conflicts early
- Keep your feature compatible with teammate changes
- Make final PR merge smoother

Recommended:

- Before writing new code
- Always before opening a PR
- Any time `main` receives updates

---

## Commit Guidelines

### Commit often

- Commit after tiny, working changes.


### Commit messages should describe intent

Good:

- `Add shortest-path fallback for disconnected nodes`
- `Fix map line not rendering on mobile width`
- `Update README setup steps for uv sync`

Avoid:

- `fix stuff`
- `changes`
- `update`

### Keep commits clean

- Do not mix unrelated changes in one commit
- Avoid committing generated files unless needed
- Never commit secrets (API keys, passwords, tokens)

---

## Pull Request (PR) Process

### 1) Push your branch


```bash
git push -u origin your-branch-name
# Pushes your branch to GitHub
```

### 2) Open a pull request into `main`

PR title format (something descriptive)

- `feature: add room-to-room shortest path`
- `fix: handle missing node in route lookup`
- `docs: add contribution workflow`

### 3) PR Description

Include details about what changed and why

### 4) Review with someone

Before approving the PR, confirm that:
- The code is working, tests pass
- You and the reviewer both understand the change
- There are no merge conflicts with `main`


### 5) Merge PR (no direct commits to `main`)

Once approved and checks pass, merge through GitHub.

---

## Handling Merge Conflicts

Conflicts are normal and expected.

When `git merge main` reports conflicts (after you've updated your local `main` from `origin/main`):

1. Open conflicted files and choose the correct final code
2. Test locally
3. Mark as resolved and commit

```bash
git add .
git commit -m "Resolve merge conflicts with main"
```

---


## Protect `main` on GitHub

Repository settings can enforce workflow automatically:

- Require pull requests before merging
- Require at least 1 approval
- Block force pushes to `main`
- Require branch to be up to date before merge

This is strongly recommended for team projects.

---

## Quick Command Reference

```bash
# update local main
git checkout main
git pull origin main

# create feature branch
git checkout -b feature/your-feature

# commit often
git add .
git commit -m "Your clear message"

# keep branch fresh
git merge main

# push branch
git push -u origin feature/your-feature
```

---

## VS Code / GitHub Desktop Cheatsheet

An alternative to using git in the terminal is VS Code or GitHub Desktop.
This follows the same team rules and gives the same result.

### Golden Rules (Same as Terminal Workflow)

- Work on your own feature branch
- Do not commit directly to `main`
- Keep your branch updated with `main` often
- Open PRs from `feature/...` -> `main` only

---

## VS Code Workflow

### 1) Start of session (update your local `main`)

1. Open VS Code in project folder
2. Open **Source Control** (branch icon on left)
3. Make sure branch is `main` (bottom-left branch name)
4. Click `...` -> **Pull**

This is equivalent to:

```bash
git checkout main
git pull origin main
```

### 2) Create a new feature branch

1. Click current branch name (bottom-left)
2. Choose **Create new branch**
3. Name it like `feature/short-description`

Equivalent:

```bash
git checkout -b feature/short-description
```

### 3) Continue existing branch and merge `main` into it

1. Switch to your feature branch (click branch name)
2. Click `...` -> **Branch** -> **Merge Branch...**
3. Select `main`
4. If conflicts appear, use VS Code Merge Editor and choose final code carefully
5. Save files, then commit conflict resolution

Equivalent:

```bash
git checkout your-branch
git merge main
```

### 4) Commit changes

1. In Source Control, stage changed files (`+`)
2. Write a clear commit message
3. Click **Commit**

Equivalent:

```bash
git add .
git commit -m "Your clear message"
```

### 5) Push branch

1. Click **Publish Branch** (first time) or **Push/Sync Changes** (later)

Equivalent:

```bash
git push -u origin your-branch-name
# later
git push
```

---

## GitHub Desktop Workflow (Alternative)

If VS Code Source Control feels confusing, GitHub Desktop is simpler for many people:

1. Fetch origin
2. Switch to `main` and pull latest
3. Switch back to your feature branch
4. Use **Branch** -> **Update from main**
5. Commit + Push
6. Open PR to `main`

---

## Important PR Rule

- Correct PR direction: `feature/...` -> `main`
- Avoid opening PRs like `main` -> `feature/...` manually
- If GitHub shows **Update branch** on your feature PR, using that button is okay (it updates your feature branch safely)

---

## Conflict Checklist (When Merge Fails)

1. Resolve all conflict markers in files
2. Run project locally and test
3. Commit with message like: `Resolve merge conflicts with main`
4. Push branch
5. Re-check PR

---

## Terminal Command ↔ VS Code Action Map

- `git pull origin main` -> Source Control `...` -> **Pull**
- `git checkout -b feature/x` -> Branch name -> **Create new branch**
- `git checkout my-branch` -> Branch name -> **Switch branch**
- `git merge main` -> `...` -> **Branch** -> **Merge Branch...** -> `main`
- `git commit -m "msg"` -> Stage files + Commit message + **Commit**
- `git push` -> **Push** / **Sync Changes**
