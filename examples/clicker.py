from camel import *

clicker = let(clicks=0).in_(
    (h3.red > (
        state.clicks
            + " "
            + if_(state.clicks == 1).then("click").otherwise("clicks")
    ))
    + (button > "Click Me!").on_click(state.clicks.add(1))
)

generate(clicker)
