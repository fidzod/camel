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

cards = (div.cards > (
    card("Red Light", "Bladee") +
    card("Starz", "Yung Lean").style({
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

generate(cards)
