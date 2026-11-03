# Camel Examples

Full programs exercising the DSL end to end, each one exactly what a
`src/pages/.../app.py` would contain.

## Hello World

The smallest possible page: one element and one child.

```python
from camel import *

page = h1 > "🐪 Hello, world!"
```

## Homepage

A small homepage demonstrating classes and composition.

```python
from camel import *

page = (
    (h1.brand_color > "Camel.py")
    + (p > ("Camel" + (code > " v6 ") + "demo"))
    + (div.card.featured >
        ((h2 > "What's new in v6?")
            + (ul > (
                (li > "More reactive features")
                + (li > "A smarter IR")
                + (li > "Nicer, emmet-inspired, syntax")
            ))
        )
    )
)
```

## Clicker

Reactive state via `let(...).in_(...)`, with a conditional label and an
`on_click` handler.

```python
from camel import *

page = let(clicks=0).in_(
    (h3 > (
        state.clicks
            + " "
            + if_(state.clicks == 1).then("click").otherwise("clicks")
    ))
    + (button > "Click Me!").on_click(state.clicks.add(1))
)
```

## Todo

A simple, reactive to-do app demonstrating lists, input binding and actions.

```python
from camel import *

page = let(tasks=["Implement scoped styles"], new="").in_(
    (h1 > "To-do")
    + (ul > state.tasks.each(lambda item: li > item))
    + input_.bind(state.new)
    + (button > "Add").on_click(
        state.tasks.append(state.new),
        state.new.restore())
)
```

## Cards

Demonstrating scoped styles.

```python
from camel import *

data_row = lambda field, value: (
    p > ((span > (field + ": ")) + value)
).style({
    "span": {
        "opacity": "0.5",
    },
})

card = lambda title, body: (div.card > (
    data_row("Title", title)
    + data_row("Artist", body)
)).style({
    ".card": {
        "font-family": "sans-serif",
        "width": "fit-content",
        "padding": "10px 18px",
        "background-color": "black",
        "color": "white",
        "border-radius": "20px"
    }
})

page = (div.cards > (
    card("Red Light", "Bladee")
    + card("Starz", "Yung Lean").style({
        ".card": {
            "background-color": "green !important"
        }
    })
)).style({
    ".cards": {
        "margin": "36px",
        "display": "flex",
        "gap": "18px",
    }
})
```
