# Underground Smash Overlay

Local LAN overlay/control system for Smash Ultimate events.

## Current canonical runtime

- Main server: `http://<host>:3000`
- Pick/Ban server: `http://<host>:5002`
- Lifecycle command: `./overlayctl`

## Quick start

```bash
cd /Users/benasselmeier/Workspace/underground-smash-overlay
./overlayctl start
./overlayctl status
./overlayctl urls
```

Stop:

```bash
./overlayctl stop
```

## Operator URLs

`./overlayctl urls` prints LAN-ready links for:

- Main Control (`/`)
- Mobile Control (`/mobile`)
- Tablet Dashboard (`/tablet-dashboard`)
- Pick/Ban Hub (`:5002/`)
- Pick/Ban Admin (`:5002/admin`)
- Pick/Ban Player 1/2 (`:5002/player/1`, `:5002/player/2`)

## Diagnostics

```bash
./overlayctl doctor
./overlayctl logs
```

- `doctor` checks required paths, ports, Python env, and service health.
- `logs` prints log paths (`logs/main.log`, `logs/pickban.log`).

## State backend modes

Default mode is sqlite-canonical with text-file mirror:

- Canonical DB: `runtime/state.db`
- OBS compatibility mirror: `text-files/*`

Fallback legacy mode:

```bash
STATE_BACKEND=textfiles ./overlayctl start
```

## Docs

- System overview: [docs/current-system-overview.md](/Users/benasselmeier/Workspace/underground-smash-overlay/docs/current-system-overview.md)
- Command API: [docs/command-api.md](/Users/benasselmeier/Workspace/underground-smash-overlay/docs/command-api.md)
- Event runbook: [docs/runbook.md](/Users/benasselmeier/Workspace/underground-smash-overlay/docs/runbook.md)
