# Action and Failure Snapshots

`robo-appian` inherits snapshot evidence from `robo-automation`. Appian components do not implement their own screenshot pipeline; their underlying browser actions are observed by the common `SnapshotService`.

```ini
CAPTURE_ACTION_SNAPSHOTS=N
CAPTURE_FAILURE_SNAPSHOTS=Y
SNAPSHOT_PATH=${EVIDENCE_PATH}/actions
```

When action capture is enabled, each instrumented browser action has only `before` and `after` phases. Failed actions use `after` with `status=failed`. A high-level Appian operation can execute multiple browser actions, so it can produce multiple before/after pairs. State queries such as `is_checked()`, `is_selected(value)`, and immediate state reads are not mutating actions unless they invoke an instrumented browser action internally.

Failure capture is independently usable when action capture is off. When both flags are on, a pytest failure matching an already captured failed action is deduplicated rather than captured twice.

Evidence is stored under one root:

```text
${SNAPSHOT_PATH}/
├── screenshots/<worker>/<process>/
├── html/<worker>/<process>/
└── metadata/<worker>/<process>/
```

Appian rerenders do not change this contract: component code re-resolves controls as needed, while the common browser action layer captures the actual browser actions.
