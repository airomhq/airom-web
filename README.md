# airom-web

The web properties for [**AIROM**](https://github.com/airomhq/airom), the
open-source AI Bill of Materials scanner.

| Directory | Deploys to | What it is |
|---|---|---|
| [`www/`](www) | **[airom.dev](https://airom.dev)** | The landing page. One self-contained HTML file, no build step. |
| [`docs-site/`](docs-site) | **[docs.airom.dev](https://docs.airom.dev)** | The documentation, built with [Mintlify](https://mintlify.com). |

The scanner itself — Go source, rule packs, and the reference markdown under
`docs/` — lives in [airomhq/airom](https://github.com/airomhq/airom). This repo
holds only what gets served over HTTP.

## Why two sites and not one

Not preference — a constraint. `mint export` emits **absolute** asset paths
(`/_next/static/…`) and the Next.js runtime builds chunk URLs from an empty
`assetPrefix` that `mint export` gives no way to set. The docs therefore have to
be served from a **domain root**. At `airom.dev/docs` the first page renders and
every chunk 404s. So the docs take a subdomain and the landing page takes the
apex.

## Working on the landing page

```bash
open www/index.html
```

That is the entire loop. No install, no build, no dependencies. See
[`www/README.md`](www/README.md).

## Working on the docs

Mintlify does **not** run on Node 25 or newer. `docs-site/package.json` pins
`engines.node` to `24.x`; use a matching local Node.

```bash
cd docs-site
npx mint@latest dev          # live preview on localhost
npx mint@latest validate     # strict: fails on warnings too
npx mint@latest broken-links
bash build.sh                # the real build → docs-site/dist/
```

`build.sh` is the single build definition — CI and Vercel both run it. Two
copies would drift, and the copy CI checks would stop being the copy that ships.

## Deployment

Two Vercel projects under the `airom` team, both deploying from this repo on
every push to `main`, with a preview URL per pull request:

| Project | Root directory | Domain |
|---|---|---|
| `airom-www` | `www` | `airom.dev`, `www.airom.dev` |
| `airom-docs` | `docs-site` | `docs.airom.dev` |

Configuration lives in each directory's `vercel.json` — build command, output
directory, and response headers — so deployment behaviour is reviewable in a
pull request rather than buried in a dashboard.

## Keeping this in step with the scanner

Splitting the site out of the code repo bought a cleaner scanner repo and cost
the guarantee that docs ship with the behaviour they describe. Things that now
need a change in **both** repos:

- **A release.** The version appears in `docs-site/installation.mdx` (twice) and
  in the scanner's `README.md`, `docs/project-status.md`, and Python SDK.
- **A behaviour change with user-visible docs** — a new flag, a new output
  format, a changed default. The scanner PR and the docs PR are separate now;
  land them together.
- **Counts and claims** on the landing page (rule totals, detector totals,
  supported languages). Re-derive rather than edit from memory:

  ```bash
  airom rules list | tail -1
  airom detectors list | tail -n +2 | wc -l
  ```

## History

`www/` and `docs-site/` were extracted from `airomhq/airom` with their full
commit history and their original paths intact, so `git log` and `git blame`
reach back past the split:

```bash
git log -- docs-site/quickstart.mdx    # back to 2026-07-17
```

## License

[Apache License 2.0](LICENSE), matching the scanner. © AIROM contributors
