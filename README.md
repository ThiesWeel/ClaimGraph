# ClaimGraph

A minimal, single-file GUI for editing structured reasoning graphs.

## How it works

The whole app is one HTML file (`index.html`): markup, styles, and JS in a single page, no
build step and no dependencies. It holds an in-memory graph `G = { nodes, edges }` and a
`pos` map of canvas coordinates, and re-renders the node/edge panels and SVG canvas from
that state on every change.

A project is meant to hold several independent reasoning threads at once, so the graph
itself is the unit that's swapped, not the page: each thread is a JSON file under `graphs/`,
and a header dropdown switches `G` between them (see [Multiple graphs](#multiple-graphs-tabs)).

Each node/edge can point at local files in `references/` and `summaries/`, tagged with a
`level` (`admin` / `summary` / `full`). This is design intent rather than a built-in agent:
ClaimGraph itself doesn't read documents or walk the graph, but the field exists so that an
AI agent doing so can decide whether, and which, attached document it actually needs to read
for a given node (see [Documents](#documents)). The same token-economy idea applies at the
structural level: once a chain of nodes has settled, it can be consolidated into one summary
node, so an agent revisiting the graph later only needs to read that summary instead of the
whole chain (see [Consolidating chains](#consolidating-chains-fold-vs-extract)).

`serve.py` is optional scaffolding around this: a static file server plus endpoints for
listing/saving graph files (`/graphs`, `/save?graph=NAME`) and for the consolidation audit
log (`/consolidations`) so the browser can persist them to disk. Without it (`file://`), the
app still works, just backed by localStorage instead of files. It's a local development tool,
not a hardened server — see [Files](#files) for the one safety property it does guarantee.

## How to run

Run `python serve.py` from this folder and open `http://localhost:8080`. This is required for
multi-graph support and consolidation logging (listing/saving `graphs/*.json`,
`consolidations.json`, and `taskboard.md`) to work against real files.

You can also open `index.html` directly from the filesystem (`file://`) with no server at all;
in that mode graphs are stored in browser localStorage instead of on disk.

## Features

- Left panel: node list with type badges
- Right panel: edge list with rationale preview
- Centre: SVG canvas with draggable nodes and coloured arrows. Left-click-drag on empty canvas
  rubber-band selects nodes (ctrl/cmd/shift adds to the selection); right-click-drag pans the
  view. Pan resets on graph switch — it's a viewport offset, not part of the saved graph.
- Edit panel: click any node or edge to edit its fields inline
- Isolated nodes (no edges) are marked with a yellow dot
- Edges without rationale are shown as dashed lines
- Import / Export JSON via header buttons
- State is auto-saved to browser localStorage
- Multiple named graphs ("tabs") per project, switchable from the header dropdown
- Long, settled chains of nodes can be consolidated into a single summary node, either folded
  in place (expandable later) or extracted into their own graph file (a "portal" node)
- Every consolidation is logged to `consolidations.json`, and the resulting summary node shows
  a small white badge with its consolidation number
- Each node carries a `status` (open / active / settled / rejected / needs_test), shown as a coloured dot
- **Validate** button checks the graph for unknown types, dangling edges, and document invariant violations

## Data model

```json
{
  "schema_version": "0.1.0",
  "nodes": [
    {
      "id": "C001",
      "title": "Short claim title",
      "type": "claim",
      "status": "open",
      "body": "Full explanation.",
      "documents": [
        { "level": "full", "reference": "references/paper.pdf", "summary": "summaries/paper.md" }
      ]
    }
  ],
  "edges": [
    {
      "id": "E001",
      "from": "C001",
      "to": "C002",
      "type": "supports",
      "rationale": "Why this edge exists.",
      "documents": []
    }
  ],
  "pos": {
    "C001": { "x": 220, "y": 140 }
  }
}
```

This is the full shape of every file in `graphs/`, and of an Export JSON download:
`schema_version`, `nodes`, `edges`, and `pos` (canvas layout) all live together, so a saved
graph is a self-contained, reproducible reasoning object rather than content plus a layout
that only exists in browser localStorage. `schema_version` will be bumped whenever this shape
changes; files saved without `pos` (pre-dating this) are still loaded fine, just re-laid-out.

A node may optionally carry consolidation fields — `"collapsed": true` plus either a
`"children": { nodes, edges, boundaryEdges, pos }` object (fold-in-place) or `"portal": true` and
`"target_graph": "..."` (extract-to-new-graph), and in both cases a `"consolidation_id"`
referencing a record in `consolidations.json`. See
[Consolidating chains](#consolidating-chains-fold-vs-extract). Don't set these by hand; use the
Fold/Extract/Expand UI.

### Node types

| Type | Meaning |
|---|---|
| `claim` | A statement you currently believe or want to evaluate |
| `hypothesis` | A testable empirical claim |
| `question` | An open uncertainty |
| `assumption` | A condition required for a claim/model to hold |
| `evidence` | Result from literature, simulation, backtest, or notebook |
| `test` | Concrete experiment to run |
| `counterfactual` | "What if this assumption is false?" |
| `failure_mode` | A way the reasoning/model can break |
| `model_choice` | A chosen modelling approach, e.g. OU, ECM, Kalman |
| `metric` | Evaluation quantity, e.g. Sharpe, CRPS, forecast error |
| `dataset_scope` | Universe, window, frequency, liquidity filter, etc. |
| `decision` | Human judgement or selected next direction |

### Edge types

| Type | Meaning |
|---|---|
| `depends_on` | One node requires another to hold |
| `supports` | Evidence or reasoning increases belief in a claim |
| `weakens` | Evidence decreases belief in a claim |
| `refutes` | Evidence directly contradicts a claim |
| `tests` | A test evaluates a claim/hypothesis/assumption |
| `controls_for` | A test removes or checks a confounder |
| `alternative_to` | One model/explanation competes with another |
| `fails_under` | A claim/model breaks under this condition |
| `motivates` | One node suggests another direction/question/test |
| `operationalizes` | Turns an abstract idea into a measurable quantity |

`derived_from` and `implements` are deliberately left out until notebook/code integration
becomes part of the workflow.

### Node status

| Status | Meaning |
|---|---|
| `open` | Default. Not yet worked, no judgement made. |
| `active` | Currently being investigated or argued. |
| `settled` | Resolved enough to build on without re-deriving it. |
| `rejected` | Considered and discarded. |
| `needs_test` | Believed plausible, but blocked on a `test` node to confirm. |

This is the field most useful for triaging a graph at a glance, by hand or by an agent —
"what's still open" is usually a more actionable question than a numeric confidence score.
Edges don't have a `status` yet; add it if a concrete need for it shows up.

### Documents

Both nodes and edges can carry a list of `documents`. Each document entry has a `level` and
up to two local file paths:

| Field | Meaning |
|---|---|
| `level: "admin"` | Linked for administrative completeness only. An agent traversing the graph does not need to read it. |
| `level: "summary"` | An agent following this node is expected to read the file in `summary`. |
| `level: "full"` | An agent following this node is expected to read the original file in `reference`. |
| `reference` | Local path to the original source document, expected under `references/`. |
| `summary` | Local path to a condensed summary of that document, expected under `summaries/`. |

A single document entry may set both `reference` and `summary` (e.g. so the same source has
both a quick summary and the full original available); `level` decides which one matters when
an agent is actively reasoning over that node. The invariant a document entry should satisfy:

- if `level` is `"summary"`, `summary` should be set
- if `level` is `"full"`, `reference` should be set
- if `level` is `"admin"`, neither path is required

This isn't currently enforced by the app — entries that violate it just won't have anything
useful for an agent to read at that level.

## Validation

Click **Validate** in the header (or import a JSON file, which runs it automatically) to check
the current graph for:

- unknown node/edge `type`
- unknown node `status`
- edges whose `from`/`to` point at a node id that doesn't exist
- documents whose `level` doesn't match the invariant above (e.g. `level: "full"` with no `reference`)
- a `consolidation_id` that doesn't resolve to a record in `consolidations.json`

This is non-blocking by design: a graph with issues still loads and saves fine, Validate just
surfaces them so you can decide whether to fix them. Every graph is also silently checked on
load, logging a console warning if it has issues — open devtools if something seems off.

## Folders

| Folder | Purpose |
|---|---|
| `references/` | Original source documents (papers, proposals, notes) linked from nodes/edges at `level: "full"`. |
| `summaries/` | Condensed summaries of documents in `references/`, linked at `level: "summary"`. |
| `graphs/` | One JSON file per graph/tab, e.g. `graphs/main.json`. |

## Multiple graphs (tabs)

A project usually accumulates more than one independent thread of reasoning. Each thread is a
separate graph file under `graphs/`, picked from the dropdown next to the ClaimGraph title.
`+ Graph` creates a new, empty one. Switching graphs autosaves the one you're leaving first.
Offline (`file://`) mode keeps the same per-graph separation in localStorage, just without the
files on disk.

## Consolidating chains: fold vs. extract

Once a chain of reasoning has settled (no longer actively disputed, or just very long), you can
consolidate it into a single summary node. The intent is that an agent revisiting the graph only
has to read that one node by default instead of the whole chain — consolidating is a manual
action you take, not something the app decides on its own. There are two modes:

1. Select the nodes you want to consolidate, either by ctrl+click (or Cmd+click) on each one,
   or by click-and-drag on empty canvas to rubber-band select everything in a rectangle (hold
   ctrl/cmd/shift while releasing to add to the current selection instead of replacing it).
   Selected nodes get a dashed gold outline.
2. With 2+ nodes selected, the header shows three options:
   - **Fold into node** — keeps everything in the current graph, you write the summary.
   - **Extract to new graph** — moves the selected nodes into a brand new graph file.
   - **Consolidate via agent** — queues the summarizing work for an AI agent instead of writing
     it yourself (see [Consolidate via agent](#consolidate-via-agent-taskboardmd) below).

### Fold into node

A new node is created in the same graph with `collapsed: true`. The original nodes and the
edges between them are preserved verbatim under the new node's `children` field — nothing is
deleted. Any edges that crossed the boundary (pointed in from or out to a node outside the
folded set) are kept as live edges, just re-pointed at the new node. Edit the new node's
`title`/`body` to be the summary an AI should read by default.

Click **Expand** on a folded node at any time to restore the original nodes/edges exactly,
including their canvas positions and the original endpoints of boundary edges.

### Extract to new graph

You're prompted for a new graph name and a summary label. The selected nodes and the edges
between them are written out as their own file under `graphs/`, exactly like
[creating a new graph](#multiple-graphs-tabs) would — they are no longer duplicated anywhere in
the current graph. In their place, a **portal node** is left behind: `collapsed: true`,
`portal: true`, `target_graph: "<new graph name>"`. Boundary edges are re-pointed at the portal
node, same as folding.

Unlike fold-in-place, there's no local `children` backup to expand — instead, click the portal
node's **Open `<graph>`** button (or just pick it from the graph dropdown) to switch into the
extracted graph and see the original nodes/edges directly. This is the right choice once a
chain is big enough, or independent enough, that it deserves to be its own thread rather than
buried inside another one.

A consolidated node's `documents` and `body` behave exactly like any other node — set its
document `level` the same way you would for an unconsolidated claim.

### Consolidate via agent (`taskboard.md`)

ClaimGraph does not call an AI agent itself — there is no API key, no model call, anywhere in
this app. "Consolidate via agent" instead does a normal fold-in-place (same mechanics as
**Fold into node**: the original nodes/edges are preserved under the new node's `children`),
but leaves the summary for later:

- The new node's `body` is set to the literal placeholder `[CONSOLIDATION TASKED]`, and its
  `status` is `needs_test`.
- A task is appended to `taskboard.md` (created at the project root if it doesn't exist) with
  the consolidation id, the summary node's id, the source node ids, and step-by-step
  instructions for whatever reads the file next: read the folded node's `children`, write a
  self-contained summary, optionally attach `documents`, replace the placeholder, and mark
  both the consolidation record and the task as done.

The idea is that some external process — a human, or an agent you point at this repo — picks
up `taskboard.md` on its own schedule and does the actual writing; ClaimGraph's job ends at
"queue the task and make the queued state visible." Until that happens, the node's edit panel
shows an explicit "waiting for an agent" notice, and the placeholder text in `body` makes it
obvious at a glance (in the JSON, in the UI, or to an agent skimming the graph) that this node
isn't a real summary yet.

### The white consolidation badge

Every node created by folding or extracting gets a small white circular badge in its
bottom-right corner showing the numeric part of its `consolidation_id` (e.g. `CS003` → `3`).
It's purely a visual cross-reference to `consolidations.json` — there's no interaction on the
badge itself, just at-a-glance confirmation that "this node is a summary of something, and
here's its audit record."

### Consolidations (`consolidations.json`)

A single, project-wide (not per-graph) JSON array logging every fold and extract operation.
Each record:

| Field | Meaning |
|---|---|
| `id` | `CS001`, `CS002`, ... |
| `created_at` | ISO timestamp |
| `mode` | `fold_in_place` or `extract_to_new_graph` |
| `source_graph` | Graph the consolidated nodes came from |
| `target_graph` | Same as `source_graph` for a fold; the new graph's name for an extract |
| `source_node_ids` | The node ids that were consolidated |
| `source_edge_ids` | The internal edge ids that were consolidated (edges with both endpoints in `source_node_ids`) |
| `summary_node_id` | The id of the resulting summary/portal node |
| `target_start_node_id` | For extracts, which node in the new graph is the natural entry point (the first node you selected); `null` for folds |
| `label` | The summary node's title/label at the time of consolidation |
| `status` | `active`, or `expanded` once a fold-in-place node has been expanded back |

This file is an **audit/index, not the source of structural truth** — deleting or corrupting it
doesn't break any graph; it just makes past consolidations harder to trace. The actual graph
content always lives in `graphs/*.json`. Validate (see [Validation](#validation)) flags any node
whose `consolidation_id` doesn't resolve to a record here.

### How an AI should traverse consolidated nodes

By default, read the summary node's `body` and stop there — that's the whole point of
consolidating a chain. Only go further if the task genuinely requires the original detail:

- For a folded node (`collapsed: true` with a `children` field): expand it, or read
  `children.nodes`/`children.edges` directly without mutating the graph, to see the original
  chain.
- For a portal node (`collapsed: true`, `portal: true`): follow `target_graph` to the
  corresponding file under `graphs/` to see the original chain there instead.

In both cases, `consolidations.json` is what makes "where did this come from" reconstructable
even after the fact — look up the node's `consolidation_id` there for `source_node_ids`,
`source_edge_ids`, and `mode` if the node itself doesn't have enough context.

One exception: if `body` is literally `[CONSOLIDATION TASKED]`, it is **not** a real summary —
treat it the same as an unconsolidated chain and read `children` directly, or better, pick up
the matching task in `taskboard.md` and do the consolidation properly.

## AI suggestion protocol (design intent, not implemented)

ClaimGraph has no built-in agent today. Everything in this section is a sketch of how an
external agent *should* propose changes to a graph, written down now so future integration
work has a shape to converge on rather than reinventing it ad hoc.

The idea: an agent reads a graph (respecting `documents[].level` as described above), then
proposes a small batch of mutations as data rather than editing `graphs/*.json` directly:

```json
{
  "graph": "main",
  "suggestions": [
    {
      "action": "add_node",
      "node": { "title": "...", "type": "hypothesis", "status": "open", "body": "..." },
      "rationale": "Why this node should exist."
    },
    {
      "action": "add_edge",
      "edge": { "from": "C001", "to": "C004", "type": "weakens", "rationale": "..." },
      "rationale": "Why this edge should exist."
    },
    {
      "action": "update_node",
      "id": "C007",
      "patch": { "status": "settled" },
      "rationale": "Why this change is warranted."
    },
    {
      "action": "fold",
      "ids": ["C010", "C011", "C012"],
      "summary": "Proposed body for the resulting folded node.",
      "rationale": "Why this chain is settled enough to fold."
    },
    {
      "action": "extract",
      "ids": ["C020", "C021", "C022"],
      "target_graph": "new-thread-name",
      "summary": "Proposed label for the portal node left behind.",
      "rationale": "Why this chain deserves to be its own graph rather than folded in place."
    }
  ]
}
```

Two properties this is meant to preserve:

- **Every suggestion carries a `rationale`**, the same as edges do — a suggestion without one
  is exactly as unhelpful as a `motivates` edge without one.
- **Suggestions are proposals, not direct writes.** A human (or a review step) applies them
  through the normal UI/API rather than the agent calling `/save` itself; this is what keeps
  `serve.py`'s no-auth, local-only design (see [Files](#files)) acceptable.

None of `action`, `suggestions`, or an apply-endpoint exist in the code yet. The next concrete
step, if/when this gets built, is a "Suggest moves for selected node" action in the UI that
asks an agent to produce one or more of the suggestion shapes above for the currently selected
node.

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire application |
| `serve.py` | Static file server plus `/graphs`, `/save?graph=NAME`, `/consolidations`, and `/taskboard` endpoints |
| `graphs/main.json` | Example / seed data (imported on first load when served over HTTP) |
| `consolidations.json` | Project-wide audit log of fold/extract/agent operations, see [Consolidations](#consolidations-consolidationsjson) |
| `taskboard.md` | Queued work for an AI agent, see [Consolidate via agent](#consolidate-via-agent-taskboardmd) |
| `README.md` | This file |

`serve.py` is meant for local development only — there's no auth and it's not hardened for
exposure beyond localhost. The one safety property it does enforce: `graph` names passed to
`/save` are validated against `[A-Za-z0-9_-]+` before being used as a filename, so a request
can't write outside `graphs/`.
