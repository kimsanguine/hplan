# Private Distribution

`kimsanguine/hplan`은 private repo로 유지하고, 수강생 설치는 Cloudflare Worker로 제공한다. 현재 운영안은 R2 없이 Worker Static Assets에 private package를 같이 배포한다.

## Student Command

강의에서는 아래 한 줄만 공유한다.

```bash
bash <(curl -fsSL https://habix.ai/hplan/install.sh)
```

학생은 별도 GitHub access token이나 `HPLAN_TOKEN`을 입력하지 않는다.

## Flow

```text
private GitHub repo
  -> GitHub Actions
  -> scripts/build-installer-package.sh
  -> scripts/prepare-worker-assets.sh
  -> Cloudflare Worker Static Assets
  -> https://habix.ai/hplan/install.sh
  -> ~/hplan
```

Worker asset paths:

- `hplan/install.sh`
- `hplan/version.json`
- `hplan/hplan-package.tar.gz`

## What Gets Installed

The package installs the current private repo content needed for the hplan ADK:

- `hplan`, `discover`, `architect`, `deliver`, `operate`
- `hooks`
- `harness`
- `profiles`
- `scripts`
- `docs`, `assets`
- root docs such as `README.md`, `README-ko.md`, `GUIDE-ko.md`, `CLAUDE.md`

Generated caches, bytecode, personal profiles, and local env files are excluded.

## Optional Link Control

By default, the link is public-by-obscurity: anyone who has the URL can install the package, but the GitHub repo stays private.

If cohort-level control is needed, set Worker secret `HPLAN_ACCESS_TOKEN` and share a cohort path:

```bash
bash <(curl -fsSL https://habix.ai/hplan/fc-2026/install.sh)
```

In that mode `fc-2026` must match the Worker secret. Students still run one command; they do not type a separate token.

## Cloudflare Setup

Deploy the Worker:

```bash
bash scripts/prepare-worker-assets.sh
npx wrangler deploy --config infra/cloudflare/hplan-installer/wrangler.toml
```

`infra/cloudflare/hplan-installer/wrangler.toml` routes `habix.ai/hplan/*` to the installer Worker:

```toml
routes = [
  { pattern = "habix.ai/hplan/*", zone_name = "habix.ai" }
]
```

## GitHub Secrets

Required:

- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_API_TOKEN`

## Manual Publish

```bash
bash scripts/prepare-worker-assets.sh
npx wrangler deploy --config infra/cloudflare/hplan-installer/wrangler.toml
```

## R2 Alternative

If R2 is enabled later, the same package can be moved from Worker Static Assets to a private R2 bucket. The Worker already keeps an `HPLAN_R2` fallback path, but the current `wrangler.toml` uses only static assets because it makes the one-line installer work without enabling R2 first.
