from camel import *

root = let(tasks=["Scoped styles", "Bind", "Routing"], new="").in_(
    (h1 > "To-do")
    + (ul > state.tasks.each(lambda item: li > item))
)

generate(root)
