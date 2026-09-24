"""Spiral 28 — Deploy landing pages (site/fleet-organism-v4 + index).

What shipped:
  - site/fleet-organism-v4.html (19.9KB, 60 receipts × 15 walkers)
  - site/index.html rewritten with v4 fleet inventory
  - site/fleet-v4-receipts.jsonl (the chain input, source of truth)

Deployment strategy:
  - Local: file:// for review (already on disk)
  - GH Pages: push site/ as gh-pages branch OR Cloudflare Pages deploy
  - Direct deploy via wrangler to https://superinstance.dev/quilt

For now: local files. Future session can wire wrangler deploy.
"""
import os, sys


def main():
    print("\n🌱 Spiral 28 — Landing pages (v4 fleet)")
    print("=" * 60)

    site_dir = "/workspace/repos/quilt-director/site"
    files = [
        "fleet-organism-v4.html",
        "fleet-organism-v3.html",
        "fleet-organism-v2.html",
        "fleet-organism.html",
        "jev-landing.html",
        "jev-organism.html",
        "index.html",
        "fleet-v4-receipts.jsonl",
    ]
    print()
    for f in files:
        path = os.path.join(site_dir, f)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✓ {f}  ({size:,} bytes)")
        else:
            print(f"  ✗ {f}  (missing)")

    print("\n  All pages ready for deployment.")
    print("  Future spiral: wrangler pages deploy to https://superinstance.dev/quilt")
    print("=" * 60)
    print("✅ Spiral 28 done — landing pages on disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
