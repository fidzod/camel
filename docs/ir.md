# Camel IR

Reference for the JSON intermediate representation Camel compiles the DSL to.
This doc just covers what's implemented so far (`Elem`, `Fragment`, and `Text`)
- state, actions, and events will be designed separately once they exist.

## Shape

Every node is a JSON object with a `type` field - including root, which is a
`Fragment`.

`children` fields are always flat arrays of nodes. A sequence of nodes never
appears nested as the sole child of another node, it is spliced into
whichever array it occurs in. `Fragment` exists for positions
where there is no enclosing array to splice into (currently just the root of a
compiled tree). Any future construct that can produce zero-or-more nodes
with no wrapping element (e.g. a loop or a conditional with no match)
resolves to this same `Fragment` convention.

## Node types

### Elem

```json
{"type": "Elem", "tag": "div", "classes": ["card", "featured"], "children": [...]}
```

| field    | type     |
|----------|----------|
| tag      | string   |
| classes  | string[] |
| children | Node[]   |

### Fragment

```json
{"type": "Fragment", "children": [...]}
```

| field    | type   |
|----------|--------|
| children | Node[] |

### Text

```json
{"type": "Text", "contents": "Camel.py"}
```

| field    | type   |
|----------|--------|
| contents | string |

