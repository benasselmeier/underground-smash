# Event Runbook

This is the canonical event-day operation flow for the current rewrite state.

## 1. Preflight (before venue opens)

From repo root:

```bash
./overlayctl doctor
```

Expected:

- required files/directories exist
- no unexpected port conflicts on `3000` and `5002`
- no critical doctor failures

If doctor fails:

1. fix missing files/dependencies
2. free conflicting ports or change `MAIN_PORT`/`PICKBAN_PORT`
3. rerun `./overlayctl doctor`

## 2. Start services

```bash
./overlayctl start
./overlayctl status
./overlayctl urls
```

Expected:

- main server healthy on `:3000`
- pick/ban server healthy on `:5002`

## 3. Smoke test on LAN devices

Use URL output from `./overlayctl urls`.

Check:

1. desktop control loads
2. mobile control loads on tablet/phone
3. pick/ban player 1 and player 2 pages load
4. pick/ban admin loads

## 4. Smoke test quick actions (critical)

From desktop or mobile/tablet:

1. score +/-
2. swap players
3. reset scoreboard
4. new round
5. theme save

Confirm overlay changes appear within expected polling window (~1s).

## 5. OBS source validation

Before going live:

1. scoreboard overlay updates values and fighters
2. casters overlay updates
3. vs overlay updates
4. standby overlay updates
5. pick/ban overlay updates stage state and fade timing

## 6. During event troubleshooting

Use:

```bash
./overlayctl status
./overlayctl logs
```

Tail logs:

```bash
tail -f logs/main.log
tail -f logs/pickban.log
```

## 7. Stop services

```bash
./overlayctl stop
```

## 8. Rollback strategy (storage layer)

If sqlite-backed mode causes instability, switch to legacy text-file mode:

```bash
./overlayctl stop
STATE_BACKEND=textfiles ./overlayctl start
```

This keeps current routes and OBS behavior while bypassing sqlite canonical state.

## 9. Rollback trigger conditions

Rollback immediately if any of these happen during live ops:

1. command actions fail repeatedly (score/swap/reset/new-round)
2. overlay state desync persists > 10 seconds
3. pick/ban tablet actions stop reflecting on overlay/API
4. service health repeatedly flaps during a set

## 10. Known canonical defaults

- main server port: `3000`
- pick/ban server port: `5002`
- lifecycle command: `./overlayctl`
- command API base: main server (`/api/commands/*`)
