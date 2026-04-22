# Veille Daily — Khadija Personal Brand

Daily LinkedIn veille brief sent via email every morning at 7:47 AM (Paris).

Runs in GitHub Actions — no dependency on laptop state.

## Secrets required (GitHub repo → Settings → Secrets → Actions)

- `ANTHROPIC_API_KEY` — from console.anthropic.com
- `GMAIL_APP_PASSWORD` — Gmail App Password (Google Account → Security → 2FA → App Passwords)

## Manual run

Go to Actions tab → Daily Veille → Run workflow

## Schedule

- 5:47 UTC = 7:47 Paris summer (CEST)
- In winter (CET), adjust cron to `47 6 * * *` — or accept it runs at 6:47 AM Paris
