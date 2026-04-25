# Camel 🐪

Camel is a tool for building small reactive SPAs in python. Your website is
a single Python file that compiles to a small, self-contained, vanilla JS bundle.

```python
from camel import *

camel = Router()

camel.route("/")(
    h1("Hello, ", state.name),
    input_().bind(state.name),
).use_state(name="World!")

camel.generate()
```

Camel compiles your app into an intermediate representation in JSON: typed atoms
describe the UI tree, state, events, and actions. A small JS runtime interprets
this IR, renders the initial DOM, listens for state changes, re-renders only
affected UI nodes (state references, ForEach loops, If conditions, bound inputs)
and executes actions (fetch, post, increment, append...) when events fire.

This is an experimental project, and doesn't claim to be a production framework.
Though being intentionally minimal might make it ideal for personal projects, small
dashboards, etc.

## Project Status

v5 is complete and stable. Camel supports hash-based routing, state, reactivity,
events, list operations, loop rendering, input binding, and API integration via
fetch and post.

## History
v1 was a refactor of a single-file static site generator written by me in 2017. v2 is a
ground-up redesign with a new API and a reactive runtime. v3 introduced lists, loops,
input binding and additional primitives. v4 introduced API integration via fetch and post.
v5 entailed a full rewrite of the serialisation layer introducing a typed atom system.

## Structure

`camel/`   — the framework

`src/`     — your app (edit app.py to build your site)

`build/`   — generated output, do not edit

## CLI

Install with `pip install -e .`

`cml build`    — compile src/ to build/

`cml watch`    — build and serve with live reload at localhost:5000

`cml format`   — format src/ with black

## More Examples

### Clicker - state, conditional rendering, events
```python
camel.route('/')(
    h3(
        state.clicks,
        if_(eq(state.clicks, 1))
            .then(" click")
            .else_(" clicks")
    ),
    button("Click Me!")
        .on_click(increment(state.clicks))
).use_state(clicks = 0)
```

### Shopping List - lists, loops, input binding
```python
camel.route('/')(
    ul(
        for_each(state.list)(li(var.item))
    ),
    input_()
        .bind(state.new),
    button('Add')
        .on_click(
            append(state.list, state.new),
            set_(state.new, '')
        )
).use_state(list=[], new='')
```

### Todos - API integration
```python
API = "http://localhost:8000"

camel.route("/")(
    h3("Todo:"),
    ul(
        for_each(state.todos).as_('todo')(
            p(
                button("X")
                    .on_click(delete(API, "todos", var.todo.id))
                    .style("margin-right", "10px"),
                var.todo.text,
            )
        )
    ),
    input_()
        .placeholder("Add something")
        .bind(state.newItem),
    button("Add")
        .on_click(
            post(API, "todos", text=state.newItem),
            set_(state.newItem, "")
        ),
).use_state(todos=fetch(API, "todos"), newItem="")
```

