from camel import *

root = let(tasks=["Scoped styles", "Bind", "Routing"], new="").in_(
    (h1 > "To-do")
    + (ul > state.tasks.each(lambda item: li > item))
    + (button > "Add").on_click(state.tasks.append("A camel's hump stores fat, not water"))
)

generate(root)
