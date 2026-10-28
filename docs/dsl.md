# Camel DSL

Reference for the Python DSL (`camel.dsl` + `camel.prelude`) used to build
the tree that `camel.ir.to_ir` compiles. Covers what's implemented so far.

## Shape

Every node is immutable - every operator returns a new node (via
`dataclasses.replace`), never mutating the one it was called on.

A child (anywhere `>`, `+`, `.in_()`, `.then()`, or `.otherwise()` attaches
one) must be a `Node` or a plain `str`; anything else raises `TypeError`
immediately, at the point of construction, not later at compile time.

`bool(node)` raises, for any `Node` and for `Condition` - a chain built with
`>`/`+` has no truth value, so an accidental `if` fails loudly rather than
silently picking a branch.

Every node compares and hashes structurally, including nodes that contain a
`Condition` - two separately built trees with the same shape are equal.

## Elements

`tag > child` appends `child`; repeated `>` keeps appending. `a + b` joins
`a` and `b` as siblings into a `Fragment`, flattening any nested `Fragment`s
so `children` stays flat. Attribute access (`div.card.featured`) appends a
CSS class per attribute, in the order accessed. A plain `str` is a valid
child anywhere - it compiles to `Text`.

## Vocabulary

`camel.prelude` exports a bare `Elem` per HTML tag: `h1`-`h6`, `p`, `b`, `a`,
`i`, `div`, `ul`, `li`, `button`, `input_`, `pre`, `code`. (`input_` dodges
the `input` builtin.)

## State

```python
let(clicks=0).in_(h3 > "...")
```

`let(name=initial, ...)` declares one or more named, reactive values;
`.in_(child)` attaches them to `child`, forming a lexical scope. `let(...)`
nests freely - two separately built subtrees declaring the same name are
independent of each other.

`state.<name>` builds a reference to a named value, resolved against the
nearest enclosing `let(...)`, innermost first. It's usable as a child
anywhere a `Node` is.

`let(...)` alone, before `.in_()`, is not a `Node` and can't be used as a
child - there's no sensible way to render bindings without a subtree yet.

## Conditionals

```python
if_(state.clicks == 1).then("click").otherwise("clicks")
```

`state.<name> == value` builds a `Condition` rather than comparing
anything - evaluating it is the runtime's job, not Python's.

`if_(condition).then(consequent)` is already a complete, usable node -
`otherwise` defaults to `Empty` (renders nothing). `.otherwise(alternate)`
replaces that default.

A `Condition`, and the result of `if_(...)` before `.then()`, are not
`Node`s and can't be used as a child, for the same reason `let(...)` alone
can't.

## Events

```python
(button > "Click Me!").on_click(state.clicks.add(1))
```

`.on_click(*actions)` attaches one or more actions to an `Elem`, run in
order when it's clicked. Each argument must be an `Action`; anything else
raises `TypeError`.

## Actions

`state.<name>.add(amount)` builds an action that adds `amount` to the named
value - running it is the runtime's job, not Python's. `amount` can be a
literal or another `state.<name>` reference.

An `Action` is not a `Node` and can't be used as a child - it only ever
appears inside `.on_click(...)`.
