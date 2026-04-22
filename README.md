# Camel 🐪

A reactive Python-native UI framework that compiles to a self-contained vanilla JS bundle.

## Project Status

v4 is complete and stable. Camel supports state, reactivity, events, list operations,
loop rendering, input binding, and API integration via fetch and post.

## History
v1 was a refactor of a single-file static site generator written by me in 2017. v2 is a
ground-up redesign with a new API and a reactive runtime. v3 introduced lists, loops,
input binding and additional primitives. v4 introduces API integration via fetch and post.

## Structure

`camel/`   — the framework

`src/`     — your app (edit app.py to build your site)

`build/`   — generated output, do not edit

## CLI

Install with `pip install -e .`

`cml build`    — compile src/ to build/

`cml watch`    — build and serve with live reload at localhost:5000

`cml format`   — format src/ with black

## Examples

### Clicker - state, conditional rendering, events
```python
from camel import *

camel = Router()

camel.route('/')(
    h3(state.clicks, if_(eq(state.clicks, 1), " click", " clicks")),
    button("Click Me!").onClick(increment(state.clicks))
).useState(clicks = 0)

camel.generate()
```

### Shopping List - lists, loops, input binding
```python
camel.route('/')(
    ul(
        each(state.list)(
            li(var.item)
        )
    ),
    input_().bind(state.new),
    button('Add').onClick(
        append(state.list, state.new),
        set_(state.new, '')
    )
).useState(list=[], new='')
```

### Todos - API integration
```python
camel.route("/")(
    h3("Todo:"),
    ul(
        each(state.todos).as_(var.todo)(
            li(
                var.todo.text,
                " ",
                button("X").onClick(
                    post(API, "todos", var.todo.id).method("DELETE")
                ),
            )
        )
    ),
    input_().placeholder("New todo...").bind(state.new),
    button("Add").onClick(post(API, "todos", text=state.new)),
).useState(todos=fetch(API, "todos"), new="")
```

## Roadmap

- ~~Page state and reactivity~~
- ~~Event handlers (onClick)~~
- ~~Conditional rendering (if_, eq)~~
- ~~bind and set_~~
- ~~Loops (each)~~
- ~~Fetch and post actions~~
- Multi-page routing examples
