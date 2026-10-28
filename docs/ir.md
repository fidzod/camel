# Camel IR

Reference for the JSON intermediate representation Camel compiles the DSL to.
This doc just covers what's implemented so far (`Elem`, `Fragment`, `Text`,
`State`, `StateRef`) - conditionals, actions, and events will be designed
separately once they exist.

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

### State

```json
{"type": "State", "initial": {"clicks": 0}, "child": {...}}
```

| field   | type                        |
|---------|-----------------------------|
| initial | dict[string, int \| string] |
| child   | Node                        |

Introduces a lexical scope over `child`: each entry in `initial` declares a
named, reactive value, initialised to the given value. `State` nests freely
- there is no requirement that it only appear at the root of a tree.

### StateRef

```json
{"type": "StateRef", "name": "clicks"}
```

| field | type   |
|-------|--------|
| name  | string |

Resolves `name` by walking outward through enclosing `State` nodes, innermost
first.
