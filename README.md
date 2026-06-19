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
      "documents": ["path/to/paper.pdf", "https://link"]
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

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire application |
| `graph.json` | Example / seed data (imported on first load when served over HTTP) |
| `README.md` | This file |
