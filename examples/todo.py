from camel import *

root = let(tasks=["Scoped styles", "Bind", "Routing"], new="").in_(
    (h1 > "To-do")
    + (ul > state.tasks.each(lambda item: li > item))
    + input_.bind(state.new)
    + (button > "Add").on_click(state.tasks.append(state.new))
)

generate(root)
