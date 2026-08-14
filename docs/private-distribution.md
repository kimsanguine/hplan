# Public Installer Distribution

`kimsanguine/hplan`은 공개 GitHub 저장소다. Habix installer와 package도 인증 없이 내려받을 수 있으며, 현재 배포 경로에 access control은 적용하지 않는다. 별도의 `hplan-core` 원본은 private/local로 유지되고, 공개 hplan package에는 검증용 pinned fixture만 포함된다.

## Student Command

강의에서는 아래 한 줄만 공유한다.

```bash
bash <(curl -fsSL https://habix.ai/hplan/install.sh)
```

사용자는 GitHub access token이나 `HPLAN_TOKEN`을 입력하지 않는다.

## Flow

```text
public GitHub repo
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

The package installs the public hplan content needed for the hplan ADK:

- `hplan`, `discover`, `architect`, `deliver`, `operate`
- `hooks`
- `harness`
- `profiles`
- `scripts`
- `docs`, `assets`
- `hplan-core.lock` and the pinned `hplan-core-fixture` used by the local doctor and CI parity checks
- root docs such as `README.md`, `README-ko.md`, `GUIDE-ko.md`, `CLAUDE.md`

Generated caches, bytecode, personal profiles, and local env files are excluded.

## Access Boundary

The current installer and package are public and unauthenticated. They are not cohort-gated or access-controlled. Do not describe the URL as private or share it as though it were protected.

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

R2 is not part of the current delivery path. Any future storage or access-policy change requires a separate operational decision and documentation update; the current `wrangler.toml` uses Worker Static Assets for the unauthenticated one-line installer.
