# ClaimGraph Taskboard

Tasks for an AI agent to pick up. See README "Consolidate via agent".

## Task CS002 — Consolidate nodes in graph "main"

- Status: pending
- Consolidation ID: CS002
- Graph: main
- Summary node: C014
- Source nodes: C006, C007

### Instructions

1. Open `graphs/main.json` and find node `C014`.
2. Read its `children.nodes` and `children.edges` — this is the original chain (titles,
   types, bodies, documents) that was consolidated into this node.
3. Write a single self-contained summary that captures the essential conclusion of that
   chain, and replace `C014`'s `body` field with it (remove the
   `[CONSOLIDATION TASKED]` placeholder; update its `title` too if useful).
4. Optionally attach one or more `documents` entries to `C014` referencing
   supporting material, with the correct `level` (see README → Documents).
5. In `consolidations.json`, set the record with id `CS002` to `"status": "done"`.
6. Mark this task's Status above as `done`.
