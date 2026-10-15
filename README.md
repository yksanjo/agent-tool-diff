# agent-tool-diff

Notice when an agent's tool inventory changes before a controller accepts the update.

Offline comparator for MCP-style `tools` manifests. Flags additions, removals, changed descriptions, input schemas and extension fields. Python 3.10+, standard library only, MIT. Never connects to a server or executes a tool.

## Try

```sh
python3 -m unittest -v
python3 demo.py
python3 tool_diff.py before.json after.json
```

CLI exits 0 for unchanged tools, 1 for review-required drift and 2 for invalid/unreadable input. Output is JSON. The demo uses synthetic in-memory tools only.

## Manifest format

```json
{"tools":[{"name":"fixture_lookup","description":"Read synthetic data","inputSchema":{"type":"object"}}]}
```

Save a trusted baseline and a newly observed inventory separately. All tool fields participate in comparison, including unknown extensions. Changed fields are reported with before/after SHA-256 fingerprints, not raw descriptions. Additions and removals list names. Duplicate names and duplicate JSON keys fail closed.

Reordering object keys does not create field drift; tool list order is ignored for drift classification. Whole-document fingerprints still reflect list order. Arrays inside schemas remain order-sensitive and may cause conservative review flags. Numeric representation differences can also cause flags.

## Controller use

1. Capture the manifest through a trusted connector.
2. Compare it with the protected baseline before the agent uses the changed inventory.
3. Have the owner inspect the actual changed manifest, server identity and access scope.
4. Replace the baseline only after review. This tool never approves or replaces it.

12 fixture tests cover description/schema/extension changes, additions/removals, name/key duplicates, malformed inputs, object order and null-versus-missing values.

## Limits

- Drift detector, not prompt-injection detection or a security sandbox. Identical manifests can hide changed server behavior; malicious text can already exist in the baseline.
- Does not authenticate servers, prove tool effects, validate JSON Schema semantics or enforce runtime access.
- Protect both captured inventory and baseline outside agent write access. A caller able to replace both can hide drift.
- No network client, server polling, signatures, automatic install, baseline update or executor.
- Manifest names and fingerprints can be sensitive metadata. Do not publish real private inventories. No file-size/depth cap; do not feed unlimited untrusted JSON.
- Intended for a trusted controller's preflight review, not a claim of safe autonomous operation.
