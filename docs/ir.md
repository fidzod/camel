# Camel IR

Reference for the JSON intermediate representation Camel compiles the DSL to.
This doc just covers what's implemented so far (`Elem`, `Fragment`, `Empty`,
`Text`, `State`, `StateRef`, `If`, `Condition`, `Literal`) - actions and
events will be designed separately once they exist.

## Shape

Every node is a JSON object with a `type` field - including root, which is a
`Fragment`.

`children` fields are always flat arrays of nodes. A sequence of nodes never
appears nested as the sole child of another node, it is spliced into
whichever array it occurs in. `Fragment` exists for positions
where there is no enclosing array to splice into (currently just the root of a
compiled tree).

Some node kinds are a closed family of variants playing one shared role
rather than a distinct kind of node in their own right - currently just
`Condition` (its `op` field distinguishes `Eq` from future comparison
kinds). These use a nested discriminator (`op`) alongside the outer `type`,
instead of a flat `type` per variant, because the variants have no
independent existence outside that role.

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

### Empty

```json
{"type": "Empty"}
```

No fields. Represents the absence of a node.

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

### If

```json
{"type": "If", "condition": {...}, "then": {...}, "otherwise": {...}}
```

| field     | type      |
|-----------|-----------|
| condition | Condition |
| then      | Node      |
| otherwise | Node      |

`then` resolves when `condition` holds, `otherwise` otherwise. `otherwise`
is `Empty` when none is given.

### Condition

```json
{"type": "Condition", "op": "Eq", "left": {...}, "right": {...}}
```

| field | type   |
|-------|--------|
| op    | string |
| left  | Value  |
| right | Value  |

`op` is currently always `"Eq"`. `left`/`right` are a `Value` - either a
`Literal` or a `StateRef` node. `Value` is not a node kind in its own right;
it only describes what can appear in these two fields.

### Literal

```json
{"type": "Literal", "value": 1}
```

| field | type          |
|-------|---------------|
| value | int \| string |
