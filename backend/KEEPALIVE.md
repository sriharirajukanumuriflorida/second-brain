# Keeping the free Render backend warm (no cold starts)

Render's **free** web service spins down after **15 minutes** of no traffic, and the
next request then takes ~30–60s to wake up. We avoid that by pinging the health
endpoint every 10 minutes so the service never goes idle.

- **Cost:** $0
- **Ping target:** `https://<your-service>.onrender.com/health`
- **Response when healthy:** `{"status": "healthy"}`

---

## 1. Get your backend URL

After the service deploys on Render, copy its URL from the dashboard. It looks like:

```
https://fde-vault-backend.onrender.com
```

Your ping target is that URL + `/health`:

```
https://fde-vault-backend.onrender.com/health
```

Test it in a browser first — you should see `{"status":"healthy"}`.

---

## 2. Set up the pinger (cron-job.org — free, no card)

1. Sign up at https://cron-job.org (free).
2. **Create cronjob** with these settings:

   | Field                  | Value                                                       |
   |------------------------|-------------------------------------------------------------|
   | Title                  | `Keep FDE Vault backend warm`                               |
   | URL                    | `https://fde-vault-backend.onrender.com/health`             |
   | Schedule               | **Every 10 minutes** (`*/10 * * * *`)                        |
   | Request method         | `GET`                                                       |
   | Expected status        | `200`                                                       |

3. Save. Enable **failure notifications** so you get an email if the ping ever fails
   (that's your early warning that the service is down, not just cold).

> **Alternative:** UptimeRobot (https://uptimerobot.com) works the same way — create an
> HTTP(s) monitor pointing at `/health` with a 5-minute interval. Either tool is fine.

---

## 3. Why 10 minutes?

Render sleeps after **15 min** idle. A 10-min interval leaves a safe margin so a single
missed ping won't let it fall asleep.

## Cost note (free-hour budget)

The free tier includes **750 instance-hours/month**. A single always-warm service uses
~730 hrs/month (24×~30.4), which fits inside the free allowance — so one keep-alive'd
service stays free. Don't keep-alive a second free service at the same time or you'll
exceed 750 hrs.

## If you ever outgrow this

A keep-alive ping is the standard free-tier trick, but it's not bulletproof (if the
pinger lapses, you get one cold start). If you want guaranteed always-on, the cheapest
real option is **Fly.io at ~$2/month**.
