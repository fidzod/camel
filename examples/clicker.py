from camel import *

"""
clicker = with_ (clicks = 0) .in_ (
    (h3 > (
        state.clicks +
        (state.clicks == 1).then("click").otherwise("clicks")
    )) +
    (btn > "Click Me!").on_click(state.clicks.add(1))
)
"""

clicker = let(clicks=0).in_(
    (h3 > (
        state.clicks
            + " "
            + if_(state.clicks == 1).then("click").otherwise("clicks")
    ))
    + (button > "Click Me!")
)

print(to_ir(clicker))
