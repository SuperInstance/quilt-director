# Deploying the organism landing page to Cloudflare Pages

## The files

```
site/
├── index.html              ← landing page (links to the others)
├── fleet-organism.html     ← 37 receipts, 7 substrates
└── jev-organism.html       ← JEV sessions rendered
```

Total: ~28KB self-contained HTML. No build step. No JS dependencies (D3.js
loaded from CDN at view time).

## Option A: Direct upload via dashboard

1. Log into https://dash.cloudflare.com
2. Go to Pages → Create a project → Direct Upload
3. Drag the `site/` directory onto the upload zone
4. Project name: `quilt-organism`
5. Click Deploy
6. Available at `quilt-organism.pages.dev`

## Option B: Wrangler CLI

```bash
cd /workspace/repos/quilt-director/site
npx wrangler pages deploy . --project-name=quilt-organism
```

## Option C: Git integration

1. Push `quilt-director/site/` to a separate repo
2. Cloudflare Pages → Connect to Git
3. Build command: (none)
4. Build output: `site`
5. Root directory: `/`

## After deploy

Verify the landing page renders:
- `https://quilt-organism.pages.dev/` — landing
- `https://quilt-organism.pages.dev/fleet-organism.html` — main visualization
- `https://quilt-organism.pages.dev/jev-organism.html` — JEV sessions

The D3.js force-directed graph should be interactive.

## Updating

```bash
cd /workspace/repos/quilt-director
PYTHONPATH=../quilt-trace/src python3 spirals/07_fleet_landing.py
```

Then re-upload the `site/` directory. The whole process takes <5 seconds.
