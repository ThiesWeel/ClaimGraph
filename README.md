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
`level` (`admin` / `summary` / `full`) that tells an AI agent walking the graph whether, and
which, attached document it actually needs to read for that node (see
[Documents](#documents)). The same token-economy idea applies at the structural level: once
a chain of nodes has settled, it can be folded into one summary node so an agent revisiting
the graph reads one node instead of the whole chain (see
[Folding a chain into one node](#folding-a-chain-into-one-node)).

`serve.py` is optional scaffolding around this: a static file server plus two endpoints
(`/graphs`, `/save?graph=NAME`) so the browser can list and persist graph files to disk.
Without it (`file://`), the app still works, just backed by localStorage instead of files.

## How to run

Run `python serve.py` from this folder and open `http://localhost:8080`. This is required for
multi-graph support (listing/saving `graphs/*.json`) to work against real files.

You can also open `index.html` directly from the filesystem (`file://`) with no server at all;
in that mode graphs are stored in browser localStorage instead of on disk.

## Features

- Left panel: node list with type badges
- Right panel: edge list with rationale preview
- Centre: SVG canvas with draggable nodes and coloured arrows
- Edit panel: click any node or edge to edit its fields inline
- Isolated nodes (no edges) are marked with a yellow dot
- Edges without rationale are shown as dashed lines
- Import / Export JSON via header buttons
- State is auto-saved to browser localStorage
- Multiple named graphs ("tabs") per project, switchable from the header dropdown
- Long, settled chains of nodes can be folded into a single summary node, and expanded back

## Data model

```json
{
  "nodes": [
    {
      "id": "C001",
      "title": "Short claim title",
      "type": "claim",
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
  ]
}
```

A node may optionally carry `"collapsed": true` and a `"children": { nodes, edges, boundaryEdges, pos }`
object — this is how a [folded chain](#folding-a-chain-into-one-node) is represented. Don't set these
by hand; use the Fold/Expand UI.

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

### Documents

Both nodes and edges can carry a list of `documents`. Each document entry has a `level` and
up to two local file paths:

| Field | Meaning |
|---|---|
| `level: "admin"` | Linked for administrative completeness only. An AI agent traversing the graph does not need to read it. |
| `level: "summary"` | When an AI agent is following this node, it must read the file in `summary`. |
| `level: "full"` | When an AI agent is following this node, it must read the original file in `reference`. |
| `reference` | Local path to the original source document, expected under `references/`. |
| `summary` | Local path to a condensed summary of that document, expected under `summaries/`. |

A single document entry may set both `reference` and `summary` (e.g. so the same source has
both a quick summary and the full original available); `level` decides which one matters when
an agent is actively reasoning over that node.

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

## Folding a chain into one node

Once a chain of reasoning has settled (no longer actively disputed, or just very long), you can
fold it into a single node so an AI revisiting the graph only has to read one summary instead of
the whole chain:

1. Ctrl+click (or Cmd+click) each node you want to fold — they get a dashed gold outline.
2. Click **Fold into node** in the header (appears once 2+ nodes are selected).
3. A new node is created with `collapsed: true`. Edit its `title`/`body` to be the summary an AI
   should read by default.
4. The original nodes and the edges between them are preserved verbatim under the new node's
   `children` field — nothing is deleted. Any edges that crossed the boundary (pointed in from or
   out to a node outside the folded set) are kept as live edges, just re-pointed at the new node.
5. Click **Expand** on a folded node at any time to restore the original nodes/edges exactly,
   including their canvas positions and the original endpoints of boundary edges.

A folded node's `documents` and `body` behave exactly like any other node — set its document
`level` the same way you would for an unfolded claim.

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire application |
| `serve.py` | Static file server plus `/graphs` (list) and `/save?graph=NAME` (persist) endpoints |
| `graphs/main.json` | Example / seed data (imported on first load when served over HTTP) |
| `README.md` | This file |
