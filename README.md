# Camel 🐪

A reactive Python-native UI framework that compiles to a self-contained vanilla JS bundle.

## Project Status

Early development. Core reactivity, state, and conditional rendering are working in v2.5.

## History
v1 was a rewrite of a single-file static site generator written by me in 2017. v2 is a
ground-up redesign with a new API and a reactive runtime.

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

## Roadmap

- ~~Page state and reactivity~~
- ~~Event handlers (onClick)~~
- ~~Conditional rendering (if_, eq)~~
- ~~bind and set_~~
- ~~Loops (each)~~
- Fetch and post actions
