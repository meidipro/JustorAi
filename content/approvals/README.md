# Citizen guide approval records

One optional JSON file per guide may be placed in `content/approvals/guides/`:

```text
001.json
002.json
...
060.json
```

Each record is locale-specific and must use the current content hash emitted in
`content/private/generated/guides/NNN.json`. A timestamp or publish-gate label
alone never earns a badge or makes a guide publishable.

The frontend build reads these records only while generating public artifacts.
They are not imported by the browser bundle.
