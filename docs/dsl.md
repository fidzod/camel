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

`tag > child` appends `child`; repeated `>` keeps appending. `a + b` joins `a`
and `b` as siblings into a `Fragment`, flattening any nested `Fragment`s so
`children` stays flat. Attribute access (`div.card.featured`) appends a CSS
class per attribute, in the order accessed. Calling a tag (`a(href="...")`) sets
HTML attributes, and accumulates across repeated calls the same way class access
does. A plain `str` is a valid child anywhere - it compiles to `Text`.

## Vocabulary

`camel.prelude` exports a bare `Elem` per HTML tag: `h1`-`h6`, `p`, `b`, `a`,
`i`, `div`, `ul`, `li`, `button`, `input_`, `pre`, `code`. (`input_` dodges
the `input` builtin.)

## Styling

```python
(ul > state.tasks.each(lambda item: li > item)).style({
    "li": {"font-weight": "bold"},
    ".large:hover": {"color": "red"},
})
```

`.style(rules)` wraps the node it's called on in a `StyleScope`, scoping
`rules` to apply only within it - a selector in `rules` never matches
anything outside the node it was attached to, however the tree it's part
of is composed elsewhere. `StyleScope`s nest freely and accumulate
rather than override: a node inside two `.style(...)` calls picks up
both. `.style(...)` is usable as a child anywhere a `Node` is, same as
the node it wraps.

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

## Binding

```python
input_.bind(state.new)
```

`.bind(state_ref)` keeps an `input_` element's value synced with a named
state value, in both directions: typing into the element writes to
`state_ref`, and anything else that changes `state_ref` (an action,
another binding) updates the element. Only `input_` supports it -
`.bind(...)` on any other element raises `TypeError` immediately, at
construction, the same way `.on_click(42)` does.

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
value; `state.<name>.append(value)` builds an action that appends `value`
to the end of the named list; `state.<name>.restore()` builds an action
that resets the named value back to whatever it was seeded to in the
nearest enclosing `let(...)` - running any of these is the runtime's job,
not Python's. `amount`/`value` can be a literal or another `state.<name>`
reference; `restore()` takes no argument.

An `Action` is not a `Node` and can't be used as a child - it only ever
appears inside `.on_click(...)`.

## Lists

```python
state.tasks.each(lambda item: li > item)
```

`state.<name>.each(fn)` builds a `ForEach`: renders `fn`'s body once per
item in the named list, in order. `fn` must take exactly one argument -
its parameter name becomes the name the current item resolves under
inside the body, so `lambda item: ...` and `lambda task: ...` behave
identically, just naming the loop variable differently.

Inside `fn`'s body, the loop parameter (`item` above) resolves to the
current element - the loop equivalent of `state.<name>`, but scoped to
the nearest enclosing `.each(...)` rather than the nearest enclosing
`let(...)`.
