## Source
- Track: Git Workflow (self-directed, reference guide)
- Reference reading: Pro Git Book by Scott Chacon; Git documentation; Atlassian Git Tutorial; GitHub Flow Guide
- Date: 2026-07-29

---

## 1. Mental Model

**Git quick reference is the cheat sheet for commands you use daily but can never remember.** The mental model is command categories: getting info, making changes, moving around, and fixing mistakes. This guide is for when you know what you want to do but can't recall the exact syntax.

> Key intuition: **Git commands follow predictable patterns** — once you learn the pattern, you can construct commands even if you forget the exact syntax.

## 2. Essential Commands

### Repository Info
```bash
git status                    # Show working directory status
git log                       # Show commit history
git log --oneline             # Show commit history (one line)
git log --graph --oneline     # Show commit history with graph
git branch                    # Show local branches
git branch -a                 # Show all branches (local + remote)
git remote -v                 # Show remote repositories
git diff                      # Show unstaged changes
git diff --staged             # Show staged changes
git show HEAD                 # Show last commit
```

### Branch Operations
```bash
git branch feature-name       # Create new branch
git checkout feature-name     # Switch to branch
git checkout -b feature-name  # Create and switch to branch
git branch -d feature-name    # Delete branch (merged)
git branch -D feature-name    # Delete branch (force)
git branch -m new-name        # Rename current branch
git branch --show-current     # Show current branch name
```

### Staging & Committing
```bash
git add file.txt              # Stage file
git add .                     # Stage all changes
git add -p file.txt           # Stage file interactively
git commit -m "message"       # Commit staged changes
git commit -am "message"      # Stage and commit all changes
git commit --amend            # Amend last commit
git reset file.txt            # Unstage file
git reset HEAD .              # Unstage all files
```

### Remote Operations
```bash
git fetch origin              # Fetch from remote
git pull origin main          # Pull and merge
git pull --rebase origin main # Pull and rebase
git push origin main          # Push to remote
git push -u origin feature    # Push and set upstream
git push --force-with-lease   # Force push (safer)
git push --all                # Push all branches
```

### Undo Changes
```bash
git checkout -- file.txt       # Discard file changes
git checkout -- .             # Discard all changes
git reset --soft HEAD~1       # Undo commit, keep changes staged
git reset HEAD~1              # Undo commit, unstage changes
git reset --hard HEAD~1       # Undo commit, discard changes
git revert HEAD               # Revert last commit (new commit)
git clean -f                  # Remove untracked files
```

## 3. One-Liners for Common Tasks

### Update develop branch
```bash
git checkout develop && git pull origin develop
```

### Update feature branch from develop
```bash
git fetch origin develop && git rebase origin/develop
```

### Undo last commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Squash last 3 commits
```bash
git reset --soft HEAD~3 && git commit -m "Combined message"
```

### Stash current work
```bash
git stash save "Work in progress"
```

### Apply stashed work
```bash
git stash pop
```

### Cherry-pick commit
```bash
git cherry-pick abc1234
```

### Show changed files between branches
```bash
git diff --name-only develop feature-branch
```

### Show commits in feature not in develop
```bash
git log develop..feature-branch --oneline
```

### Delete all merged branches
```bash
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d
```

## 4. Workflow Cheat Sheets

### Feature Branch Workflow
```bash
# Start
git checkout develop
git pull origin develop
git checkout -b feature/my-feature

# Work
# ... make changes ...
git add .
git commit -m "Add feature"

# Sync with develop
git fetch origin develop
git rebase origin/develop

# Push
git push -u origin feature/my-feature

# Merge (via PR/MR)
# ... create pull request ...
```

### Hotfix Workflow
```bash
# Start from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# Fix and commit
# ... fix bug ...
git add .
git commit -m "Fix critical bug"

# Merge to main
git checkout main
git merge hotfix/critical-bug
git push origin main

# Merge to develop
git checkout develop
git merge hotfix/critical-bug
git push origin develop

# Cleanup
git branch -d hotfix/critical-bug
```

### Rebase Workflow
```bash
# Before merging to develop
git fetch origin develop
git rebase origin/develop

# If conflicts, resolve and continue
# ... resolve conflicts ...
git add resolved-file.txt
git rebase --continue

# Force push (since you rebased)
git push --force-with-lease origin feature-branch
```

## 5. Diff Cheat Sheet

```bash
git diff                    # Working directory vs staging
git diff --staged           # Staging vs HEAD
git diff HEAD               # Working directory vs HEAD
git diff branch1 branch2    # Branch vs branch
git diff commit1 commit2    # Commit vs commit
git diff --stat             # Show statistics only
git diff -U5                # Show 5 lines of context
git diff file.txt           # Diff specific file
```

## 6. Log Cheat Sheet

```bash
git log                       # Full commit history
git log --oneline             # One line per commit
git log --graph               # Show branch graph
git log -n 10                 # Last 10 commits
git log --author="John"       # Commits by author
git log --since="2024-01-01" # Commits since date
git log --grep="fix"          # Search commit messages
git log --file.txt            # History of specific file
git log -p file.txt           # Show diffs for file
```

## 7. Branch Comparison

```bash
git log develop..feature      # Commits in feature not in develop
git log feature..develop      # Commits in develop not in feature
git log develop...feature     # Commits in either but not both
git diff develop feature      # Diff between branches
git diff --stat develop feature  # Changed files between branches
```

## 8. Conflict Resolution

```bash
git merge branch-name         # Start merge
# ... resolve conflicts ...
git add resolved-file.txt     # Stage resolved files
git commit                   # Complete merge
# OR
git merge --abort            # Cancel merge
```

## 9. Stash Operations

```bash
git stash                    # Stash current work
git stash save "message"     # Stash with message
git stash list               # List stashes
git stash pop                # Apply and remove most recent
git stash apply              # Apply without removing
git stash drop               # Remove stash
git stash clear              # Remove all stashes
```

## 10. Remote Management

```bash
git remote add origin URL    # Add remote
git remote -v                # Show remotes
git remote remove origin     # Remove remote
git remote set-url origin URL  # Change remote URL
git fetch --all              # Fetch all remotes
git fetch --prune            # Clean up stale remotes
```

## 11. Tag Operations

```bash
git tag v1.0.0               # Create lightweight tag
git tag -a v1.0.0 -m "msg"   # Create annotated tag
git tag                      # List tags
git show v1.0.0              # Show tag details
git push origin v1.0.0       # Push tag
git push origin --tags       # Push all tags
git tag -d v1.0.0            # Delete local tag
git push origin --delete v1.0.0  # Delete remote tag
```

## 12. Reset vs Revert vs Checkout

| Command | What it does | When to use |
|---------|--------------|-------------|
| `git reset --soft HEAD~1` | Undo commit, keep changes staged | Fix last commit before push |
| `git reset HEAD~1` | Undo commit, unstage changes | Undo commit but keep work |
| `git reset --hard HEAD~1` | Undo commit, discard changes | Complete undo (dangerous) |
| `git revert HEAD` | Create new commit undoing changes | Undo on shared branch |
| `git checkout -- file.txt` | Discard file changes | Undo file changes |
| `git checkout branch` | Switch branches | Move between branches |

## 13. Force Push Safety

```bash
# SAFE: Force push with lease
git push --force-with-lease origin branch

# DANGEROUS: Force push (can overwrite others)
git push --force origin branch

# NEVER: Force push shared branches
git push --force origin main  # DON'T DO THIS
```

## 14. Common Aliases

```bash
# Add to ~/.gitconfig
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --graph --oneline --all
```

## 15. Quick Troubleshooting

```bash
# Show current branch
git branch --show-current

# Show upstream branch
git branch -vv

# Show remote tracking
git remote show origin

# Show untracked files
git ls-files --others

# Show ignored files
git ls-files --others --ignored

# Check repository size
du -sh .git

# Check file count
git ls-files | wc -l

# Find large files
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | sort -k2 -n -r | head -n 10
```

## 16. Emergency Commands

```bash
# Recover lost commits
git reflog

# Undo force push
git reflog origin/main
git branch recovery origin/main@{5}

# Fix detached HEAD
git checkout -b rescue-branch

# Abort merge
git merge --abort

# Abort rebase
git rebase --abort

# Abort cherry-pick
git cherry-pick --abort

# Clean working directory
git reset --hard HEAD
git clean -fd
```

## 17. Configuration

```bash
# Set user info
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Set default branch name
git config --global init.defaultBranch main

# Set line endings
git config --global core.autocrlf true  # Windows
git config --global core.autocrlf input # Mac/Linux

# Set merge tool
git config --global merge.tool vscode

# Set editor
git config --global core.editor "code --wait"

# Show all config
git config --list
```

## 18. Quick Reference Card

| Task | Command |
|------|---------|
| Check status | `git status` |
| Stage file | `git add file.txt` |
| Commit | `git commit -m "msg"` |
| Push | `git push origin main` |
| Pull | `git pull origin main` |
| Create branch | `git branch name` |
| Switch branch | `git checkout name` |
| Merge branch | `git merge branch` |
| Rebase branch | `git rebase branch` |
| Show log | `git log --oneline` |
| Show diff | `git diff` |
| Undo file | `git checkout -- file.txt` |
| Undo commit | `git reset --soft HEAD~1` |
| Stash | `git stash` |
| Unstash | `git stash pop` |
