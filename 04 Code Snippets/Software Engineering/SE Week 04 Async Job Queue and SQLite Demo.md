# SE Week 04 Async Job Queue and SQLite Demo

> Week 04 · APIs, Integration & Backend Engineering. A local background-job queue using asyncio plus sqlite3 persistence; no server or network required.

```python
import asyncio, sqlite3

async def worker(queue, db):
    while True:
        job_id, payload = await queue.get()
        if job_id is None:
            queue.task_done()
            break
        result = payload.upper()
        db.execute("UPDATE jobs SET status=?, result=? WHERE id=?", ("done", result, job_id))
        db.commit()
        queue.task_done()

async def main():
    db = sqlite3.connect(":memory:")
    db.execute("CREATE TABLE jobs (id INTEGER PRIMARY KEY, status TEXT, result TEXT)")
    q = asyncio.Queue()
    task = asyncio.create_task(worker(q, db))
    for payload in ["parse file", "embed chunks"]:
        cur = db.execute("INSERT INTO jobs(status, result) VALUES (?, ?)", ("queued", None))
        await q.put((cur.lastrowid, payload))
    await q.put((None, None))
    await q.join()
    await task
    print(db.execute("SELECT id, status, result FROM jobs ORDER BY id").fetchall())

asyncio.run(main())
```


Related: [[03 Permanent Notes/SE Week 04 AuthN vs AuthZ and Token Patterns]]
