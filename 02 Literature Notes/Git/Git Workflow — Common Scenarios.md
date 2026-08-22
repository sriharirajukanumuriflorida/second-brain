## Source
- Track: Git Workflow (self-directed, reference guide)
- Reference reading: Pro Git Book by Scott Chacon; Git documentation; Atlassian Git Tutorial; GitHub Flow Guide
- Date: 2026-07-29

---

## 1. Mental Model

**Common Git scenarios are the recurring patterns that developers encounter daily.** The mental model is a decision tree where each scenario has a standard solution. Mastering these scenarios transforms Git from a source of frustration to a powerful tool that flows naturally with your workflow.

> Key intuition: **Git scenarios have canonical solutions** — learn the patterns, not individual commands.

## 2. Update Develop Branch

### Scenario: You're on develop and need the latest changes
```bash
# Option 1: Pull (merge approach)
git checkout develop
git pull origin develop

# Option 2: Fetch + merge (safer, see what's coming)
git fetch origin develop
git log HEAD..origin/develop --oneline
git merge origin/develop

# Option 3: Reset (if you want exact remote state)
git fetch origin develop
git reset --hard origin/develop
```

**When to use:** Regularly updating your local develop branch to stay in sync with the team.

## 3. Update Feature Branch from Develop

### Scenario: You're working on a feature branch and need latest develop changes
```bash
# Option 1: Merge approach (preserves history)
git fetch origin develop
git checkout feature/my-feature
git merge origin/develop

# Option 2: Rebase approach (linear history, recommended)
git fetch origin develop
git checkout feature/my-feature
git rebase origin/develop

# Option 3: Interactive rebase (clean up commits)
git fetch origin develop
git checkout feature/my-feature
git rebase -i origin/develop
```

**When to use:** Before merging your feature branch to ensure it works with latest changes.

## 4. Undo Last Commit

### Scenario: You just committed but want to undo it
```bash
# Undo commit but keep changes staged
git reset --soft HEAD~1

# Undo commit and unstage changes
git reset HEAD~1

# Undo commit and discard changes (dangerous)
git reset --hard HEAD~1

# Undo commit and create new commit (preserves history)
git revert HEAD
```

**When to use:** Fixing mistakes in the last commit. Use `--soft` to keep changes, `revert` for shared branches.

## 5. Undo Multiple Commits

### Scenario: You want to undo several recent commits
```bash
# Undo last 3 commits but keep changes
git reset --soft HEAD~3

# Undo last 3 commits and unstage changes
git reset HEAD~3

# Undo last 3 commits and discard changes
git reset --hard HEAD~3

# Revert last 3 commits (creates new commits)
git revert HEAD~3..HEAD
```

**When to use:** Fixing multiple recent commits. Use `revert` for shared branches to preserve history.

## 6. Stash Work Temporarily

### Scenario: You need to switch branches but have uncommitted changes
```bash
# Stash current work
git stash

# Stash with message
git stash save "Work in progress on feature X"

# Stash including untracked files
git stash -u

# Stash including ignored files
git stash -a

# List stashes
git stash list

# Apply most recent stash
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Drop specific stash
git stash drop stash@{2}

# Clear all stashes
git stash clear
```

**When to use:** Interrupting work to handle something urgent, switching branches with dirty working directory.

## 7. Cherry-Pick Specific Commit

### Scenario: You want a specific commit from another branch
```bash
# Cherry-pick single commit
git cherry-pick abc1234

# Cherry-pick without committing
git cherry-pick --no-commit abc1234

# Cherry-pick multiple commits
git cherry-pick abc1234 def5678

# Cherry-pick with edits
git cherry-pick -e abc1234

# Cherry-pick range
git cherry-pick abc1234..def5678
```

**When to use:** Bringing specific fixes or features from one branch to another without full merge.

## 8. Squash Commits

### Scenario: You have multiple related commits that should be one
```bash
# Interactive rebase to squash
git rebase -i HEAD~5

# In the editor, change 'pick' to 'squash' for commits to combine
# Save and exit, edit combined commit message

# Squash last N commits into one
git reset --soft HEAD~N
git commit -m "Combined commit message"
```

**When to use:** Cleaning up commit history before creating PR/MR, combining related work.

## 9. Fix Commit Message

### Scenario: You made a typo in your last commit message
```bash
# Amend last commit message
git commit --amend -m "Corrected commit message"

# Amend last commit (opens editor)
git commit --amend

# If already pushed, force push
git push --force-with-lease
```

**When to use:** Fixing typos, improving commit message clarity. Only for unpushed commits or private branches.

## 10. Move Commit to Different Branch

### Scenario: You committed on wrong branch
```bash
# Reset wrong branch
git checkout wrong-branch
git reset HEAD~1

# Checkout correct branch and commit
git checkout correct-branch
git add .
git commit -m "Your commit message"

# Or cherry-pick approach
git checkout correct-branch
git cherry-pick wrong-branch
git checkout wrong-branch
git reset --hard HEAD~1
```

**When to use:** Accidentally committing on develop instead of feature branch.

## 11. Resolve Merge Conflicts

### Scenario: Merging branches and encountering conflicts
```bash
# Start merge
git merge feature-branch

# View conflicts
git status

# Resolve conflicts manually
# Edit files with <<<<<<< HEAD markers
# Choose which version to keep or combine both

# Stage resolved files
git add resolved-file.txt

# Complete merge
git commit

# Or abort if you can't resolve
git merge --abort
```

**When to use:** Any merge operation that results in conflicts.

## 12. Clean Up Local Branches

### Scenario: You have many stale local branches
```bash
# List merged branches
git branch --merged

# List unmerged branches
git branch --no-merged

# Delete merged branches (except current)
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d

# Delete all branches merged to develop
git branch --merged develop | grep -v "\*" | xargs -n 1 git branch -d

# Force delete branch (if unmerged)
git branch -D stale-branch
```

**When to use:** Regular cleanup to keep branch list manageable.

## 13. Recover Lost Commits

### Scenario: You accidentally deleted commits
```bash
# Find lost commits in reflog
git reflog

# Show specific lost commit
git show abc1234

# Create branch from lost commit
git branch recovery-branch abc1234

# Reset to lost commit
git reset --hard abc1234
```

**When to use:** Accidental reset, rebase gone wrong, force push mistakes.

## 14. Change Remote URL

### Scenario: Repository moved or you want to change authentication
```bash
# Show current remotes
git remote -v

# Change remote URL
git remote set-url origin https://github.com/newurl/repo.git

# Switch from HTTPS to SSH
git remote set-url origin git@github.com:username/repo.git

# Switch from SSH to HTTPS
git remote set-url origin https://github.com/username/repo.git
```

**When to use:** Repository moved, changing authentication method, fork updates.

## 15. Work with Submodules

### Scenario: Project includes Git submodules
```bash
# Clone repository with submodules
git clone --recursive https://github.com/user/repo.git

# Initialize and update submodules
git submodule update --init --recursive

# Update submodule to latest commit
git submodule update --remote

# Remove submodule
git submodule deinit path/to/submodule
git rm path/to/submodule
rm -rf .git/modules/path/to/submodule
```

**When to use:** Projects that depend on other Git repositories.

## 16. Large File Handling

### Scenario: Need to handle large files (use Git LFS)
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.psd"
git lfs track "*.zip"

# Track by extension
git lfs track "*.mp4"

# View tracked patterns
git lfs track

# Push LFS files
git push origin main
```

**When to use:** Repositories with large binary files (images, videos, datasets).

## 17. Partial Commits

### Scenario: You want to commit only part of a file
```bash
# Interactive staging
git add -p path/to/file

# Stage specific hunks
# Type 'y' to stage, 'n' to skip, 's' to split

# Commit staged hunks
git commit -m "Partial commit message"
```

**When to use:** When one file contains multiple unrelated changes.

## 18. Ignore Files After Committing

### Scenario: You accidentally committed files that should be ignored
```bash
# Add to .gitignore
echo "node_modules/" >> .gitignore

# Remove from tracking (keep local files)
git rm --cached path/to/file

# Remove from tracking (delete local files)
git rm path/to/file

# Commit the removal
git commit -m "Stop tracking ignored files"
```

**When to use:** Accidentally committing build artifacts, credentials, or other ignore-worthy files.

## 19. Work with Tags

### Scenario: You need to mark releases
```bash
# Create lightweight tag
git tag v1.0.0

# Create annotated tag with message
git tag -a v1.0.0 -m "Version 1.0.0 release"

# Create tag for specific commit
git tag -a v1.0.0 abc1234 -m "Version 1.0.0 release"

# List tags
git tag

# Show tag details
git show v1.0.0

# Push tags to remote
git push origin v1.0.0
git push origin --tags

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

**When to use:** Marking releases, milestones, or important commits.

## 20. Bisect for Bug Finding

### Scenario: You need to find which commit introduced a bug
```bash
# Start bisect
git bisect start

# Mark current commit as bad
git bisect bad

# Mark known good commit
git bisect good abc1234

# Git will checkout commits, test each, mark good/bad
# Repeat until bug is found

# End bisect and return to original state
git bisect reset
```

**When to use:** Finding regression points, identifying which commit broke functionality.
