# Troubleshooting Log — 2026-08-23

Record of a debugging session: deployed app showed "no functionality" and a
"messy layout" at `https://second-brain-six-pied.vercel.app/`, plus a GitHub
push that repeatedly failed with `HTTP 503` from this network. Kept for
future reference since both issues (and their fixes) are easy to hit again.

## Issue 1: App showed no data ("no functionality")

**Symptom:** Login and the landing page worked, but Dashboard showed
`Total Notes: 0`, `Last Sync Status: Unknown`, `Vault Path: Not configured`.
Notes and Search pages were empty.

**Root cause:** Not a bug — the app had never successfully synced. The
entire content model depends on `backend/app/services/github_service.py`
cloning a vault repo (`GITHUB_REPO_URL` + `GITHUB_PAT`) into Postgres before
any note appears. `GITHUB_REPO_URL` defaults to `""` in
`backend/app/config.py` and was missing from the Render env var list
(`render.yaml` only declared `GITHUB_PAT`). GitHub OAuth *login* is a
completely separate credential (`GITHUB_OAUTH_CLIENT_ID/SECRET`) from the
vault-sync credential (`GITHUB_REPO_URL`/`GITHUB_PAT`) — login working says
nothing about whether sync is configured.

**Fix:** Added `GITHUB_REPO_URL` to the `render.yaml` env var list, then set
the actual value in the Render dashboard and triggered a sync from the
Dashboard page's "Trigger Sync" button.

```diff
# render.yaml
       - key: GITHUB_PAT
         sync: false
+      # Git URL of the Obsidian vault repo to sync notes from (e.g. this repo).
+      - key: GITHUB_REPO_URL
+        sync: false
```

## Issue 2: `GET /api/v1/status` returned 500

**Symptom:** Confirmed live via browser dev tools: `POST /api/v1/sync`
returned `200` (`sync_id: 2`), but the immediately following
`GET /api/v1/status` returned `500 Internal Server Error`. This made the
Dashboard show "Unknown"/"Not configured" instead of real data or even a
clean error, and would keep failing even after a successful sync.

**Root cause:** `backend/app/api/status.py` passed
`vault_path=settings.vault_path` into `StatusResponse`. `settings.vault_path`
is typed `Path` in `backend/app/config.py`
(`vault_path: Path = Path("./vault_clone")`), but `StatusResponse.vault_path`
in `backend/app/schemas.py` is typed `str`. FastAPI's response-model
validation rejected the `Path` object on every call.

**Fix:**

```diff
# backend/app/api/status.py
     return StatusResponse(
         total_notes=total_notes,
         last_sync_at=last_sync.started_at if last_sync else None,
         last_sync_status=last_sync.status if last_sync else None,
-        vault_path=settings.vault_path
+        vault_path=str(settings.vault_path)
     )
```

**Regression test added** in `backend/tests/test_integration_api.py`
(`TestStatusEndpoint::test_status_returns_ok`) — verified it fails against
the old code and passes against the fix before committing.

## Issue 3 (latent, found alongside #2): sync bugs that would mask failures

Two additional bugs found while investigating the sync path — neither
caused Issue 1/2 directly, but both would corrupt error reporting once sync
started running for real:

- `backend/app/services/index_service.py` called
  `existing_note.last_indexed_at = datetime.utcnow()` when updating an
  existing note, but `datetime` was never imported in that file — would
  `NameError` starting on the *second* sync of any given note (first sync
  of a fresh vault is unaffected, since that hits the "create" branch).
  Fix: added `from datetime import datetime` to imports.
- `backend/app/api/sync.py`'s exception handler used
  `datetime.now(timezone.utc)` (timezone-aware) while the success path used
  `datetime.utcnow()` (naive) for the same `completed_at` column — mixing
  aware/naive datetimes in one column risks comparison errors later. Fix:
  made the failure path consistent with the success path
  (`datetime.utcnow()`).

## Issue 4: `git push` intermittently failed with `HTTP 503`

**Symptom:**

```
error: RPC failed; HTTP 503 curl 22 The requested URL returned error: 503
send-pack: unexpected disconnect while reading sideband packet
fatal: the remote end hung up unexpectedly
Everything up-to-date
```

`git ls-remote origin HEAD` and the initial `info/refs` handshake
(`GET .../info/refs?service=git-receive-pack`) always succeeded — auth and
basic connectivity were fine. The failure happened specifically on the
`POST .../git-receive-pack` request (the actual push payload), which came
back as an immediate `HTTP 503` with `Connection: close`
(confirmed via `GIT_CURL_VERBOSE=1`).

**Root cause:** Transient flakiness on the push path (likely GitHub-side or
an intermediate proxy on this network), not something wrong with the repo,
credentials, or commit content. Ruled out payload size as the deciding
factor — a single 92-line new-file commit failed 3 retries in a row, while
a 218-line multi-file commit succeeded on the very next retry. There was no
reliable correlation between commit size/content and success — it was pure
intermittent flakiness on the write path.

**What did NOT reliably fix it on its own:**
- `--no-thin`
- `-c http.postBuffer=524288000` (larger POST buffer)
- `-c http.version=HTTP/1.1` (forcing HTTP/1.1)

**What worked: plain retries, with commits kept reasonably small.**
Splitting one large multi-file commit into several smaller commits and
retrying each a few times got everything through. No git config change was
actually necessary in the end — persistence was the fix.

```bash
# Retry loop that got a stuck push through:
for i in 1 2 3 4 5; do
  echo "Attempt $i..."
  if git push --no-thin origin feature/add_llm_wraper 2>&1; then
    echo "SUCCESS"
    break
  fi
  sleep 5
done
```

**If this happens again:**
1. Try a plain `git push` 2-3 times first — most 503s here cleared within
   1-2 retries.
2. If a specific commit keeps failing after several retries, split it into
   smaller commits (`git reset --soft HEAD~1`, then `git add` a subset of
   files, commit, push, repeat for the rest) and retry each independently.
   Smaller commits are *not* guaranteed to succeed, but they narrow the
   blast radius and reduce how much you redo per failed attempt.
3. Verify sync state with `git fetch origin <branch>` and
   `git rev-parse HEAD` vs `git rev-parse origin/<branch>` — a failed push
   with `HTTP 503` does **not** partially update the remote ref, so it's
   always safe to retry without risk of a corrupt/partial remote state.
4. To split a commit safely: confirm it hasn't already reached the remote
   first (`git log` vs `git log origin/<branch>`) before running
   `git reset --soft HEAD~1` — that command is safe only for commits that
   are still local-only.
