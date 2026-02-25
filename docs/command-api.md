# Command API (Milestone 2)

Base URL: main server (`http://<host>:3000`)

All endpoints return JSON with `success` and `overlay_state` on success.

## Score Commands

### `POST /api/commands/score`
Set score by `delta` or absolute `value`.

Request body JSON:

```json
{ "player": 1, "delta": 1 }
```

or

```json
{ "player": "p2", "value": 2 }
```

Notes:
- `player` accepts: `1`, `2`, `p1`, `p2`, `player1`, `player2`, `player-1`, `player-2`
- score is clamped to `0..3`

## Fighter Commands

### `POST /api/commands/set-fighter`

Request body JSON:

```json
{ "player": 1, "fighter": "Sora" }
```

## Match Ops Commands

### `POST /api/commands/swap-players`
Swaps:
- sponsor
- name
- score
- fighter
- losers flag

Request body JSON:

```json
{}
```

### `POST /api/commands/reset-scoreboard`
Resets:
- `Player1-Score.txt` -> `0`
- `Player2-Score.txt` -> `0`
- `Player1-Fighter.txt` -> `Random`
- `Player2-Fighter.txt` -> `Random`

Request body JSON:

```json
{}
```

### `POST /api/commands/new-round`
Resets:
- both sponsors -> empty
- both names -> empty
- then runs reset-scoreboard

Request body JSON:

```json
{}
```

## Compatibility Notes

- Commands write through shared backend (`runtime/state.db`) and mirror to `text-files/*`.
- Existing routes and form-post workflows remain unchanged.
- Fallback mode: set `STATE_BACKEND=textfiles` to bypass sqlite.
