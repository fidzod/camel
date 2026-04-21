from camel import *

camel = Router()

camel.route('/')(
    p("Clicks: ", state.clicks),
    button("Click Me!").onClick(increment(state.clicks))
).useState(clicks = 0)

camel.generate()
