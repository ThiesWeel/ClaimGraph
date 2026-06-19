# ClaimGraph

A minimal, single-file GUI for editing structured reasoning graphs.

## How to run

Open `index.html` in a browser. No server, no install, no build step.

If you open it directly from the filesystem (`file://`), the app loads the bundled default graph.
If you serve the folder over HTTP (e.g. `python -m http.server 8080`), it will fetch `graph.json` on first load.

## Features

- Left panel: node list with type badges
- Right panel: edge list with rationale preview
- Centre: SVG canvas with draggable nodes and coloured arrows
- Edit panel: click any node or edge to edit its fields inline
- Isolated nodes (no edges) are marked with a yellow dot
- Edges without rationale are shown as dashed lines
- Import / Export JSON via header buttons
- State is auto-saved to browser localStorage

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

### Node types
`claim` `evidence` `argument` `assumption` `question`

### Edge types
`supports` `depends_on` `attacks` `contradicts` `refines`

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

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire application |
| `graph.json` | Example / seed data (imported on first load when served over HTTP) |
| `README.md` | This file |
