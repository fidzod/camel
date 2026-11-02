# Camel IR

Reference for the JSON intermediate representation Camel compiles the DSL to.
This doc just covers what's implemented so far (`Elem`, `Fragment`, `Empty`,
`Text`, `State`, `StateRef`, `If`, `Condition`, `Literal`, `Event`, `Action`,
`ForEach`, `VarRef`, `StyleScope`).

## Shape

Every node is a JSON object with a `type` field - including root, which is a
`Fragment`.

`children` fields are always flat arrays of nodes. A sequence of nodes never
appears nested as the sole child of another node, it is spliced into
whichever array it occurs in. `Fragment` exists for positions
where there is no enclosing array to splice into (currently just the root of a
compiled tree).

Some node kinds are a closed family of variants playing one shared role
rather than a distinct kind of node in their own right. There are two ways
this shows up, depending on whether the variants actually share a shape:

`Condition` is a nested discriminator on one shape: every comparison
operator takes a `left`/`right` pair, so `op` is the only thing that varies
between `Eq` and future comparisons like `Gt`/`Lt` - one `type`, one set of
fields, a second field (`op`) picks the variant.

`Action` is a union of independently-shaped variants, the same way `IRNode`
itself is a union of unrelated node shapes: `Add` needs a `target`/`amount`,
but a future `Set`/`Push`/etc. will need entirely different fields, so
there's no single shape to attach a discriminator to. Each variant gets its
own full `TypedDict` (`type: "Action"`, its own `name`, its own fields),
joined into one `ActionIR` union as they're added.

Use the first form only when every current *and clearly foreseeable*
variant genuinely shares the same fields - if that stops being true (e.g.
`Condition` grows a variant combining two conditions rather than two
values), it should be split the same way `Action` is.

## Node types

### Elem

```json
{"type": "Elem", "tag": "div", "classes": ["card", "featured"], "children": [...], "events": [...], "bind": {"type": "Empty"}, "attributes": [["href", "https://example.com"]]}
```

| field      | type                |
|------------|---------------------|
| tag        | string              |
| classes    | string[]            |
| children   | Node[]              |
| events     | Event[]             |
| bind       | StateRef \| Empty   |
| attributes | [string, string][]  |

`bind` is `Empty` on every `Elem` except an `input_` with `.bind(...)`
attached - same "nothing here" value `If.otherwise` defaults to, rather
than introducing `null` as a second way to say that. Unlike `events`, it
isn't routed through the `Action` system: it's a standing two-way link,
not a one-shot response to a DOM event - the runtime keeps the
element's value and the `StateRef` it names in sync in both directions
(state changes update the element; the user typing updates the state).
`bind` is always a `StateRef` - there's no sensible reading of "bind to
a literal," since binding reads *and* writes.

`attributes` is a flat list of `[name, value]` pairs rather than an
object keyed by name, since the DSL itself allows the same name to be
set more than once - each call accumulates onto the list rather than
replacing a prior entry for the same name. Values are always plain
strings, fixed at compile time - there's no reactive `StateRef` form
here, unlike `bind`.

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

| field   | type                                      |
|---------|-------------------------------------------|
| initial | dict[string, int \| string \| (int\|string)[]] |
| child   | Node                                       |

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

### Event

```json
{"name": "click", "actions": [{...}]}
```

| field   | type     |
|---------|----------|
| name    | string   |
| actions | Action[] |

No `type` field - every event has this exact shape, there's no variant to
distinguish, so there's nothing for a discriminator to do. Only ever
appears inside an `Elem`'s `events`, never as a tree child. `name` is a DOM
event name; `"click"` today.

### Action

```json
{"type": "Action", "name": "Add", "target": {...}, "amount": {...}}
{"type": "Action", "name": "Append", "target": {...}, "value": {...}}
{"type": "Action", "name": "Restore", "target": {...}}
```

Three variants so far.

`Add`:

| field  | type     |
|--------|----------|
| name   | "Add"    |
| target | StateRef |
| amount | Value    |

Adds `amount` to the value `target` refers to.

`Append`:

| field  | type     |
|--------|----------|
| name   | "Append" |
| target | StateRef |
| value  | Value    |

Appends `value` to the end of the list `target` refers to.

`Restore`:

| field  | type      |
|--------|-----------|
| name   | "Restore" |
| target | StateRef  |

Resets the value `target` refers to back to whatever it was seeded to
in the nearest enclosing `let(...)`. No operand - unlike `Add`/`Append`
there's nothing to supply, the value to restore to is already on
record.

All three: `target` is always a `StateRef` - there's no sensible reading
of "add to"/"append to"/"restore" a literal. `amount`/`value` (where
present) is a `Value` (a `Literal` or a `StateRef`), same as a
`Condition`'s operands. Only ever appears inside an `Event`'s `actions`,
never as a tree child.

### ForEach

```json
{"type": "ForEach", "list": {...}, "var": "item", "body": {...}}
```

| field | type     |
|-------|----------|
| list  | StateRef |
| var   | string   |
| body  | Node     |

Renders `body` once per item in the list `list` refers to, with `var`
naming the item for `VarRef`s inside `body` to resolve. `list` is always a
`StateRef` - there's no way to iterate a hardcoded list yet, since `Literal`
can't hold one. Widen `Literal` and `list` together the day that's actually
needed; typing `list` as a general `Value` now, ahead of that, would claim
more than the IR can actually represent.

### VarRef

```json
{"type": "VarRef", "name": "item"}
```

| field | type   |
|-------|--------|
| name  | string |

Resolves `name` against the current item of the nearest enclosing
`ForEach` - the loop equivalent of `StateRef`, but resolved against the
current iteration rather than a lexical `State` scope.

### StyleScope

```json
{"type": "StyleScope", "id": "238u2oehi", "child": {...}}
```

| field | type   |
|-------|--------|
| id    | string |
| child | Node   |

Associates every element rendered within `child` with `id`, for CSS to
target. Scopes accumulate rather than shadow: an element inside two
nested `StyleScope`s is associated with both ids, not just the
innermost - unlike `State`/`ForEach`, where a name collision picks the
innermost binding. `id` is opaque and unique per instance.
