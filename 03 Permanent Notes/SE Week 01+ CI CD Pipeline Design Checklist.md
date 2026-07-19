# SE Week 01+ CI CD Pipeline Design Checklist

A production CI/CD pipeline is executable release policy. Minimum checklist: least-privilege workflow permissions, pinned actions, lockfile-based dependency caching, matrix builds for supported runtimes, format/lint/type checks, unit and integration tests, coverage reporting with a realistic threshold, SAST and SCA scans, artifact upload, provenance/version metadata, branch protection, and protected environments for deploy.

Keep feedback tiers explicit: pre-commit for sub-10-second local checks; PR CI for merge blockers; nightly for expensive mutation/e2e/security depth; release pipeline for artifact promotion and environment approvals.

> One-liner: **the pipeline should make the safe path the shortest path from commit to rollbackable production.**


Related: [[02 Literature Notes/Software Engineering/Production Delivery Engineering]] · [[04 Code Snippets/Software Engineering/SE Week 01+ GitHub Actions Delivery Workflow Validator]]
