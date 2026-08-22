"""
Generate a read-only, browser-bound, time-limited access link.

The owner runs this with the admin secret to mint a share link. The first person
to open the link claims it (binds to their browser) and gets read-only access
for the TTL (default 24h). See app/services/auth/access_service.py.

Usage (from backend/):
    python -m scripts.generate_access_link --secret <ADMIN_SECRET> \
        --base-url https://your-app.vercel.app [--hours 24] [--label "for Alex"]

The ADMIN_SECRET must match settings.admin_secret (env ADMIN_SECRET). Prints the
share link to hand out.
"""
import argparse
import sys

from app.config import settings
from app.database import SessionLocal
from app.services.auth.access_service import AccessTokenService


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a read-only access link.")
    parser.add_argument("--secret", required=True, help="Admin secret (must match ADMIN_SECRET).")
    parser.add_argument("--base-url", required=True, help="Frontend base URL, e.g. https://app.vercel.app")
    parser.add_argument("--hours", type=int, default=24, help="TTL in hours (default 24).")
    parser.add_argument("--label", default=None, help="Optional note, e.g. who it's for.")
    args = parser.parse_args()

    if not settings.admin_secret:
        print("ERROR: ADMIN_SECRET is not set on the server. Set it in .env first.")
        return 1
    if args.secret != settings.admin_secret:
        print("ERROR: provided --secret does not match ADMIN_SECRET.")
        return 1

    db = SessionLocal()
    try:
        token = AccessTokenService(db).generate(
            ttl_hours=args.hours, label=args.label, role="readonly"
        )
    finally:
        db.close()

    link = f"{args.base_url.rstrip('/')}/access?token={token.token}"
    print("Read-only access link (valid for {}h once opened):".format(args.hours))
    print(link)
    if args.label:
        print(f"Label: {args.label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
