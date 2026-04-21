from camel import *

camel = Router()

camel.route("/")(
    h3(state.clicks, if_(eq(state.clicks, 1), " click", " clicks")),
    button("Click Me!").onClick(increment(state.clicks)),
).useState(clicks=0)

camel.generate()
