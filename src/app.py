# Cml build runs this file
from camel import *

site = (
    (h1.brand_color > "Camel.py") +
    (p > ("Camel" + (pre > "v6") + "demo")) +
    (div.card.featured >
        ((h2 > "What's new in v6?") +
            (ul > (
                (li > "More reactive features") +
                (li > "A smarter IR") +
                (li > "Nicer, emmet-inspired, syntax")
            ))
        )
    )
)

print(to_ir(site))
