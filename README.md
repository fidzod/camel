# Camel 🐪

A reactive Python-native UI framework that compiles to a self-contained vanilla JS bundle.

## Project Status

Early development. The v1 API is working and v2 (reactivity, state, events) is in progress.

## Structure

camel/   — the framework
src/     — your app (edit app.py to build your site)
build/   — generated output, do not edit

## CLI

pip install -e .

cml build    — compile src/ to build/
cml watch    — build and serve with live reload at localhost:5000
cml format   — format src/ with black

## V1 Example

```python
from camel import *

router = makeRouter()

router.route("/", div(
    h1("Hello from Camel!")
))

router.generate()
```

## Roadmap

- Page state and reactivity
- Event handlers (onClick, onInput)
- Conditional rendering (showIf)
- Loops (each)
- Fetch and post actions
