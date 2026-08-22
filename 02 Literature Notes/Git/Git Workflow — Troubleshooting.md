## Source
- Track: Git Workflow (self-directed, reference guide)
- Reference reading: Pro Git Book by Scott Chacon; Git documentation; Atlassian Git Tutorial; GitHub Flow Guide
- Date: 2026-07-29

---

## 1. Mental Model

**Git troubleshooting is about understanding the internal state and restoring it to a working condition.** The mental model is that Git maintains multiple parallel states (working directory, staging area, HEAD, branches, refs) and problems occur when these states become inconsistent or corrupted. The solution is usually to identify which state is wrong and reset it appropriately.

> Key intuition: **Git rarely loses data permanently** — most problems can be recovered from the reflog or object database.

## 2. Common Error Messages

### "fatal: not a git repository"
```bash
# Problem: Not in a Git repository
# Solution: Navigate to repository root or initialize
cd path/to/repository
# or
git init
```

### "fatal: refusing to merge unrelated histories"
```bash
# Problem: Merging repositories with different root commits
# Solution: Allow unrelated histories
git merge branch-name --allow-unrelated-histories
```

### "error: failed to push some refs"
```bash
# Problem: Remote has commits you don't have
# Solution: Pull first, then push
git pull origin main
git push origin main

# Or force push (if you're certain)
git push --force-with-lease origin main
```

### "fatal: 'origin' does not appear to be a git repository"
```bash
# Problem: Remote origin not configured
# Solution: Add remote
git remote add origin https://github.com/user/repo.git
```

### "warning: refname 'HEAD' is ambiguous"
```bash
# Problem: Multiple references named HEAD
# Solution: Specify full ref name
git checkout refs/heads/main
```

## 3. Merge Conflicts

### Scenario: Merge conflicts prevent completion
```bash
# View conflicts
git status

# View conflict markers in files
# <<<<<<< HEAD
# your changes
# =======
# their changes
# >>>>>>> branch-name

# Resolve conflicts manually
# Edit files to resolve conflicts
# Remove conflict markers

# Stage resolved files
git add resolved-file.txt

# Complete merge
git commit

# Or abort merge if you can't resolve
git merge --abort
```

### Strategy: Use merge tool for complex conflicts
```bash
# Configure merge tool
git config --global merge.tool vscode
git config --global mergetool.vscode.cmd 'code --wait $MERGED'

# Use merge tool
git mergetool
```

### Strategy: Accept one side entirely
```bash
# Accept current branch (HEAD)
git checkout --ours path/to/file
git add path/to/file

# Accept incoming branch
git checkout --theirs path/to/file
git add path/to/file
```

## 4. Detached HEAD State

### Scenario: HEAD is not pointing to a branch
```bash
# Check current state
git status
# Output: "HEAD detached at abc1234"

# Solution 1: Create branch to save work
git checkout -b rescue-branch

# Solution 2: Return to previous branch
git checkout @{-1}

# Solution 3: Return to main branch
git checkout main
```

### Recovery: If you made commits in detached HEAD
```bash
# Find lost commits in reflog
git reflog

# Create branch from lost commit
git branch recovery-branch abc1234

# Merge recovery branch into main
git checkout main
git merge recovery-branch
```

## 5. Lost Commits

### Scenario: Accidentally deleted commits with reset
```bash
# View reflog (Git's safety net)
git reflog

# Find the commit you want to recover
# abc1234 HEAD@{2}: commit: Add feature

# Create branch from lost commit
git branch recovery-branch abc1234

# Or reset to lost commit
git reset --hard abc1234
```

### Scenario: Force push overwrote important commits
```bash
# Find lost commits in reflog
git reflog origin/main

# Create branch from lost remote commit
git branch recovery-branch origin/main@{5}

# Push recovery branch
git push origin recovery-branch
```

### Scenario: Deleted wrong branch
```bash
# Find branch in reflog
git reflog | grep "checkout: from"

# Recreate branch from last commit
git branch recovered-branch abc1234

# Or recover from remote
git checkout -b recovered-branch origin/lost-branch
```

## 6. Corrupted Repository

### Scenario: Git reports corruption
```bash
# Check repository integrity
git fsck

# Repair loose objects
git fsck --full

# Recover lost objects
git fsck --lost-found
# Check .git/lost-found/ for recovered objects

# Clone repository as backup
git clone --mirror original-url backup-repo
```

### Scenario: .git directory corrupted
```bash
# If .git is corrupted but working directory is intact
# Create new repository in different location
git init new-repo
cd new-repo

# Copy files from old repository
cp -r ../old-repo/* .
cp -r ../old-repo/.gitignore .

# Add and commit
git add .
git commit -m "Recover from corruption"

# Add remote and push
git remote add origin original-url
git push -f origin main
```

## 7. Authentication Issues

### Scenario: SSH authentication failing
```bash
# Test SSH connection
ssh -T git@github.com

# Check SSH keys
ls -la ~/.ssh

# Generate new SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Add SSH key to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key and add to GitHub/GitLab
cat ~/.ssh/id_ed25519.pub
```

### Scenario: HTTPS authentication failing
```bash
# Configure credential helper
git config --global credential.helper store

# Or use cache (temporary)
git config --global credential.helper 'cache --timeout=3600'

# Clear stored credentials
git config --global --unset credential.helper

# Use personal access token instead of password
# Generate token in GitHub/GitLab settings
# Use token as password when prompted
```

### Scenario: Wrong remote URL
```bash
# Check current remote
git remote -v

# Change remote URL
git remote set-url origin https://github.com/correct-user/repo.git

# Switch to SSH
git remote set-url origin git@github.com:user/repo.git
```

## 8. Large File Issues

### Scenario: Repository too large, push rejected
```bash
# Check repository size
du -sh .git

# Find large files
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '/^blob/ {print substr($0,6)}' | sort -k2 -n -r | head -n 10

# Remove large files from history
git filter-branch --tree-filter 'rm -f path/to/large-file' HEAD

# Or use BFG (faster)
java -jar bfg.jar --delete-files path/to/large-file.git

# Clean up and garbage collect
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Scenario: Use Git LFS for large files
```bash
# Install Git LFS
git lfs install

# Track large files
git lfs track "*.psd"
git lfs track "*.zip"

# Migrate existing large files to LFS
git lfs migrate import --include="*.psd,*.zip"

# Push LFS files
git push origin main
git push origin --all
git lfs push origin main --all
```

## 9. Branch Issues

### Scenario: Cannot delete branch (unmerged)
```bash
# Force delete branch
git branch -D feature-branch

# If you want to preserve commits, merge first
git checkout main
git merge feature-branch
git branch -d feature-branch
```

### Scenario: Branch name contains spaces or special characters
```bash
# Delete branch with special name
git branch -D "feature/branch with spaces"

# Or escape special characters
git branch -D feature/branch\ with\ spaces
```

### Scenario: Remote tracking branch issues
```bash
# Set upstream tracking
git branch --set-upstream-to=origin/main main

# Remove stale remote tracking branches
git fetch --prune

# Update remote tracking
git remote set-branches origin '*'
git fetch
```

## 10. Submodule Issues

### Scenario: Submodule not initialized
```bash
# Initialize submodules
git submodule update --init --recursive

# Update submodule to latest commit
git submodule update --remote

# Remove submodule completely
git submodule deinit path/to/submodule
git rm path/to/submodule
rm -rf .git/modules/path/to/submodule
```

### Scenario: Submodule detached HEAD
```bash
# Checkout branch in submodule
cd path/to/submodule
git checkout main

# Update parent repository
cd ..
git add path/to/submodule
git commit -m "Fix submodule to branch"
```

## 11. Performance Issues

### Scenario: Git operations are slow
```bash
# Check file count in repository
git ls-files | wc -l

# Enable file system monitor (faster status)
git config core.fsmonitor true

# Disable git hooks temporarily
git config core.hooksPath /dev/null

# Shallow clone for large repositories
git clone --depth 1 https://github.com/user/repo.git
```

### Scenario: Too many loose objects
```bash
# Run garbage collection
git gc

# Aggressive garbage collection
git gc --aggressive --prune=now

# Check repository size
du -sh .git
```

## 12. Working Directory Issues

### Scenario: Accidentally deleted files
```bash
# Restore deleted files
git checkout -- path/to/deleted-file.txt

# Restore all deleted files
git checkout -- .

# If files were committed, restore from commit
git checkout abc1234 -- path/to/deleted-file.txt
```

### Scenario: Working directory in bad state
```bash
# Discard all changes
git reset --hard HEAD

# Discard changes in specific file
git checkout HEAD -- path/to/file

# Clean untracked files
git clean -f

# Clean untracked files and directories
git clean -fd
```

### Scenario: Cannot switch branches (uncommitted changes)
```bash
# Stash changes
git stash

# Switch branches
git checkout other-branch

# Apply stashed changes
git stash pop

# Or commit changes
git add .
git commit -m "WIP"
git checkout other-branch
```

## 13. Configuration Issues

### Scenario: Wrong user.name or user.email
```bash
# Check current configuration
git config user.name
git config user.email

# Set global configuration
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set local configuration (repository-specific)
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Fix author of last commit
git commit --amend --author="Your Name <your.email@example.com>"
```

### Scenario: Line ending issues (CRLF vs LF)
```bash
# Check current configuration
git config core.autocrlf

# Set to true (Windows: convert CRLF to LF on commit)
git config core.autocrlf true

# Set to input (Mac/Linux: convert CRLF to LF on commit)
git config core.autocrlf input

# Set to false (no conversion)
git config core.autocrlf false

# Normalize line endings in repository
git add --renormalize .
```

## 14. Recovery Procedures

### Complete Repository Recovery
```bash
# 1. Check if repository is corrupted
git fsck --full

# 2. Clone as backup if possible
git clone --mirror original-url backup-repo

# 3. Check reflog for lost commits
git reflog

# 4. Create recovery branch if needed
git branch recovery abc1234

# 5. Verify repository state
git status
git log --oneline -10

# 6. Push to safe remote
git push origin recovery-branch
```

### Emergency Repository Reset
```bash
# WARNING: This destroys local changes
# Only use if you're certain

# Reset to exact remote state
git fetch origin
git reset --hard origin/main
git clean -fd
```

## 15. Prevention Strategies

### Regular Backups
```bash
# Push to multiple remotes
git remote add backup https://backup-url/repo.git
git push backup main

# Or use git bundle for offline backup
git bundle create backup.bundle --all
```

### Branch Protection
```bash
# Configure protected branches (via GitHub/GitLab UI)
# Require pull requests
# Require status checks
# Require review from code owners
```

### Pre-commit Hooks
```bash
# Use husky for pre-commit checks
npm install husky --save-dev
npx husky install
npx husky add .husky/pre-commit "npm test"
```

### Regular Maintenance
```bash
# Regular garbage collection
git gc --aggressive --prune=now

# Clean up remote branches
git fetch --prune

# Clean up local branches
git branch --merged | grep -v "\*" | xargs -n 1 git branch -d
```
