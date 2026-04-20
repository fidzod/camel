# Camel 🐪

A reactive Python-native UI framework that compiles to a self-contained vanilla JS bundle.

## Project Status

Early development. Core reactivity and state are working in v2.

## Structure

`camel/`   — the framework

`src/`     — your app (edit app.py to build your site)

`build/`   — generated output, do not edit

## CLI

Install with `pip install -e .`

`cml build`    — compile src/ to build/

`cml watch`    — build and serve with live reload at localhost:5000

`cml format`   — format src/ with black

## V1 Example

```python
from camel import *

camel = Router()

camel.route('/',
    p("Clicks: ", state.clicks),
    button("Click Me!").onClick(increment(state.clicks))
).useState(clicks = 0)

camel.generate()
```

## Roadmap

- ~~Page state and reactivity~~
- ~~Event handlers (onClick, onInput)~~
- Conditional rendering (showIf)
- Loops (each)
- Fetch and post actions
