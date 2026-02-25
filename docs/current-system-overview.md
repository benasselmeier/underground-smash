# Current System Overview

Project: Underground Smash Overlay  
Date analyzed: 2026-02-24  
Scope: Static repo/code inspection (no live server run in this pass)

## Assumptions

- This project is operated locally on macOS/LAN (as implied by `ipconfig`, `socketfilterfw`, and shell scripts).
- Filesystem behavior is case-insensitive in current usage. Several file name/path cases rely on that.
- Operators may use multiple entry scripts depending on event context.

## OBS Constraints To Preserve

- Treat current OBS integration patterns as compatibility constraints, not incidental tech debt.
- Overlay assets may intentionally remain self-contained (single-file HTML with inline CSS/JS) for OBS reliability and portability.
- Rewrite changes must preserve practical OBS Browser Source behavior:
  - predictable local file/URL loading behavior used on event machines
  - stable relative asset resolution used by current overlays
  - no additional runtime dependencies that complicate scene/source setup on event day
- If modularization is introduced internally, provide a build/export path that still emits OBS-friendly self-contained overlay artifacts.

## 1) Runtime Architecture (As Implemented)

### Primary processes

1. Main overlay/control server: `app.py`
   - Flask app serving desktop/mobile/tablet control UIs and text-file data API.
   - Core state source for overlays: `text-files/`.
2. Pick/Ban server: `pickban-server.py`
   - Flask app serving player tablet pick/ban UIs, admin UI, stage-bar overlay endpoint, and pick/ban API.
   - Pick/ban session is process memory (`current_session`), not file-backed.

### Entrypoints and startup scripts currently in use

- `start-smash-overlay.sh`: starts main server via `python -m flask run` on port `5000`.
- `start-smash-overlay-alt.sh`: starts main server via `python3 app.py` on port `8080`.
- `start-smash-overlay-port80.sh`: starts main server via `python -m flask run` on port `80` (sudo).
- `start-pickban-server.sh`: runs `python3 pickban-server.py` on port `5002` (foreground).
- `start-all-servers.sh`: starts `app.py` on `3000` and `pickban-server.py` on `5002` (background).
- `post-restart-setup.sh`: similar to `start-all-servers.sh` (`3000` + `5002`, nohup logs).

### Important operational reality

- Main server port is not fixed in practice (`5000`, `3000`, `8080`, or `80`) depending on script.
- Pick/Ban is mostly `5002`, but `network-diagnostics.sh` still references `5001` in guidance.
- `start-all-servers.sh` writes `.main_server.pid`/`.pickban_server.pid`; `stop-all-servers.sh` primarily kills by process name and optionally reads `server_pids.txt` (written by `post-restart-setup.sh`), so lifecycle tracking is inconsistent.

## 2) Route and Endpoint Map

## Main server (`app.py`)

Static/file-serving routes:
- `GET /text-files/<path:filename>`
- `GET /resources/<path:filename>`
- `GET /images/fighter-ui-slice/<path:filename>`
- `GET /images/fighter-portraits-stylized/cropped/<path:filename>`
- `GET /static/<path:filename>`

State/UI routes:
- `GET /api/overlay-state`
- `GET|POST /` (desktop control)
- `GET /view/<filename>` (raw editor utility)
- `POST /update/<filename>` (raw editor save utility)
- `POST /save-theme`
- `GET|POST /mobile`
- `GET|POST /tablet-dashboard`
- `GET /debug-static`

## Pick/Ban server (`pickban-server.py`)

Static/file-serving routes:
- `GET /resources/<path:filename>`
- `GET /images/<path:filename>`
- `GET /css/<path:filename>` (served from `templates/`)

UI routes:
- `GET /` (pick/ban hub)
- `GET /player/<int:player_id>`
- `GET /admin`
- `GET|POST /tablet-dashboard` (scoreboard + pick/ban ops view from pick/ban process)
- `GET /overlays/pick-ban`
- `GET /overlay/stage-bar` (alias)

Pick/Ban API routes:
- `GET /api/session`
- `POST /api/ban_stage` (alias to strike)
- `POST /api/strike_stage`
- `POST /api/pick_stage`
- `POST /api/set_first_striker`
- `POST /api/start_next_game`
- `POST /api/start_next_game_generic`
- `POST /api/gentleman_pick`
- `POST /api/reset`

Cross-origin behavior:
- Pick/Ban server sets permissive CORS headers (`Access-Control-Allow-Origin: *`) on responses.

## 3) Data Model and State Flow

### Persistent state (main overlay stack)

Primary persistence is plaintext in:
- `text-files/info/`
- `text-files/player-1/`
- `text-files/player-2/`
- `text-files/casters/`

Examples used in active flows:
- `text-files/player-1/Player1-Score.txt`
- `text-files/player-2/Player2-Score.txt`
- `text-files/player-1/Player1-Fighter.txt`
- `text-files/player-2/Player2-Fighter.txt`
- `text-files/info/Current-Round.txt`
- `text-files/info/Bracket-Name.txt`
- `text-files/info/Theme.txt`
- `text-files/info/event-info.txt`
- `text-files/info/Startgg-Slug.txt`

### Pick/Ban state (non-persistent)

`pickban-server.py` keeps a single in-memory `current_session` with:
- phase state (`flow_phase`, `current_player`, `game_number`, etc.)
- stage pools and strike history
- selected stage and picker

Session is reset on process restart.

### Data flow: control UI -> storage -> overlay rendering

1. Operator edits fields in:
   - `templates/home.html`
   - `templates/mobile.html`
   - `templates/tablet_dashboard.html`
2. JS auto-save submits form POST to current page (`/`, `/mobile`, or `/tablet-dashboard`) with `X-Requested-With: XMLHttpRequest`.
3. `app.py` iterates known files from each text-files directory and writes posted values into matching files.
4. Overlay pages poll every second:
   - Scoreboard (`overlays/scoreboard/scoreboard.html`) prefers `GET /api/overlay-state`, falls back to per-file text polling.
   - Other overlays (`overlays/casters/casters.html`, `overlays/vs screen/vs.html`, `overlays/standby/standby.html`) poll text files directly.

### Pick/Ban server interactions

1. Player UIs (`templates/pickban_player.html`) poll `/api/session` every second.
2. Strike/pick actions POST to `/api/strike_stage` and `/api/pick_stage`.
3. Admin (`templates/pickban_admin.html`) and hub (`templates/pickban_index.html`) call reset/next-game APIs.
4. Stream overlay (`overlays/pick-ban/pickban_overlay.html`) polls `/api/session` every second and renders stage strike/pick tiles.
5. Tablet dashboard bridge:
   - `templates/tablet_dashboard.html` includes Pick/Ban controls with configurable base URL defaulting to `http://{location.hostname}:5002`.
   - This enables one-device operations that touch both scoreboard text files and pick/ban session APIs.

## 4) Current Coverage vs V2 Goals

## Goal 1: Single-command startup + lifecycle

Already partially present:
- `start-all-servers.sh` and `post-restart-setup.sh` start both services and print URLs.

Gaps:
- Multiple startup paths with conflicting ports and inconsistent stop semantics.
- No single authoritative `start/stop/status` command set for non-dev operators.
- Inconsistent PID handling between start/stop scripts.

## Goal 2: Stream Deck support

Already partially present:
- `resources/stream_deck_config.streamDeckProfile` exists.
- Many Stream Deck actions map to local shell scripts in `scripts/set-fighters/p1/`.
- Scripts write fighter selections directly to text files.

Gaps:
- Current profile appears focused on fighter assignment (mostly P1), not comprehensive match ops (scores, swap, round reset, etc.).
- File-path based script triggers are brittle across machines/paths.
- Some scripts have inconsistent relative write paths (notably Corrin scripts), increasing portability risk.
- No explicit HTTP API contract designed for deck actions.

## Goal 3: First-class remote control UX (LAN mobile/tablet)

Already partially present:
- Dedicated mobile control (`/mobile`) and tablet dashboard (`/tablet-dashboard`).
- Host binding to `0.0.0.0` in startup flows.
- mDNS registration logic exists in both servers.
- Network diagnostic scripts exist.

Gaps:
- URL/port clarity is fragmented (`5000` vs `3000` vs `8080`; outdated `5001` mention).
- mDNS only registers when running `app.py` directly; `flask run` path does not execute `if __name__ == '__main__'` registration logic.
- Diagnostics are script-based, not surfaced inside operator UI.

## 5) Top Rewrite Risks (Live Event Priority)

1. Concurrent operator overwrite risk
- Form autosave posts full forms; simultaneous operators can overwrite each other with stale fields.

2. Startup/lifecycle ambiguity under time pressure
- Multiple scripts and port permutations create avoidable setup errors at event start.

3. Pick/Ban volatility on process restart
- `current_session` is in memory only; restart resets flow mid-set.

4. Path/case portability brittleness
- Current behavior depends on local path conventions and case-insensitive filesystem assumptions.

5. UI behavior tightly coupled to existing DOM and polling rhythm
- Quick-action UX and overlay update cadence are embedded directly in template JS, making accidental regressions likely during rewrite.

## 6) Must-Preserve Behaviors for Rewrite

- Fast update loop for on-stream data visibility (current norm: ~1s overlay polling).
- Touch-first mobile/tablet usability for live operator workflows.
- Quick actions:
  - score +/-
  - swap players
  - reset scoreboard
  - new round reset
  - manual save
- Character assignment UX parity (grid selection and tablet token workflow).
- Theme switching through operator UI and overlay reflection.
- Pick/Ban rules state machine parity:
  - Game 1 strike pattern `[1,2,1]`
  - post-game winner strikes 3, loser picks
  - generic next-game fallback
  - explicit reset and first-striker controls
- Stream-facing pick/ban overlay behavior (including stage-selected display/fade timing).
- OBS compatibility behavior for overlays, including cases where single-file HTML/CSS/JS is intentional.

## 7) Migration Baseline Checklist (Before Rebuild)

## A. Freeze current behavior baseline

- [ ] Record one canonical event-day startup path used in practice (today) and keep it stable until cutover.
- [ ] Capture working URLs/ports used by operators for desktop, mobile, P1/P2 pick/ban, admin, and overlay sources.
- [ ] Run and record a full set workflow (bo5) including winner/loser pick/ban transitions.

## B. Define parity acceptance tests (manual, event-realistic)

- [ ] Desktop/mobile/tablet update same match fields and reflect on overlays within acceptable latency.
- [ ] Quick actions verified end-to-end.
- [ ] Pick/Ban phase transitions validated for: game 1, post-game winner flow, generic next-game flow, reset.
- [ ] Overlay pages validated in intended OBS load mode (file or URL) for both servers.
- [ ] Overlay artifacts and paths validated against actual OBS Browser Source setup used at events.

## C. Stabilize startup/lifecycle for V2

- [ ] Introduce one operator command with explicit `start`, `stop`, `status`, `urls`.
- [ ] Standardize ports and remove conflicting legacy paths or clearly deprecate them.
- [ ] Add health checks for both services and include readiness output.
- [ ] Keep simple logs accessible in known locations for event troubleshooting.

## D. Stream Deck migration baseline

- [ ] Inventory current deck actions from `resources/stream_deck_config.streamDeckProfile`.
- [ ] Keep backward-compatible action coverage for at least current fighter assignment and core match ops.
- [ ] Prefer HTTP action endpoints in V2 over filesystem script writes.
- [ ] Define a minimal command API for deck use: score inc/dec, swap, reset, new round, set fighter, set winner/next-game.

## E. Remote UX baseline

- [ ] Provide a single “operator landing page” with all live URLs and status.
- [ ] Include in-app LAN diagnostics (host IP, reachable ports, pick/ban connectivity).
- [ ] Keep responsive touch controls and avoid tiny tap targets.
- [ ] Ensure reconnection behavior is clear when one service is unreachable.

## F. Cutover safety

- [ ] Run one full local dress rehearsal with real devices on LAN.
- [ ] Keep current version launchable as rollback path during first V2 events.
- [ ] Document rollback trigger conditions and exact rollback steps in a one-page runbook.

## Repo Paths Referenced

- `app.py`
- `pickban-server.py`
- `templates/home.html`
- `templates/mobile.html`
- `templates/tablet_dashboard.html`
- `templates/pickban_player.html`
- `templates/pickban_admin.html`
- `templates/pickban_index.html`
- `overlays/scoreboard/scoreboard.html`
- `overlays/pick-ban/pickban_overlay.html`
- `overlays/casters/casters.html`
- `overlays/standby/standby.html`
- `overlays/vs screen/vs.html`
- `text-files/`
- `resources/Stages.txt`
- `resources/Fighters.txt`
- `resources/stream_deck_config.streamDeckProfile`
- `scripts/set-fighters/`
- `start-smash-overlay.sh`
- `start-smash-overlay-alt.sh`
- `start-smash-overlay-port80.sh`
- `start-pickban-server.sh`
- `start-all-servers.sh`
- `stop-smash-overlay.sh`
- `stop-smash-overlay-port80.sh`
- `stop-pickban-server.sh`
- `stop-all-servers.sh`
- `post-restart-setup.sh`
- `network-diagnostics.sh`
- `network-test.sh`
- `fix-network.sh`
