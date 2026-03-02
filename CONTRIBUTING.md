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

### 2) One branch per feature or person

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
git merge main
git push -u origin your-branch-name   # first push, updates your branch to remote repository on github
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
# Pushes your branch to github
```

### 2) Open a pull request into `main`

PR title format (something descriptive)

- `feature: add room-to-room shortest path`
- `fix: handle missing node in route lookup`
- `docs: add contribution workflow`

### 3) PR Description

Include details about what changed and why

### 4) Review with someone

Make sure that the code is good code, it works, and that there are no conflicts.

### 5) Merge PR (no direct commits to `main`)

Once approved and checks pass, merge through GitHub.

---

## Handling Merge Conflicts

Conflicts are normal and expected.

When conflict happens:

1. Run:

```bash
git merge main
```

2. Open conflicted files and choose the correct final code
3. Test locally
4. Mark as resolved and commit

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