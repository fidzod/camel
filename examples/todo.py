from camel import *

root = let(tasks=["Implement scoped styles"], new="").in_(
    (h1 > "To-do")
    + (ul > state.tasks.each(lambda item: li > item))
    + input_.bind(state.new)
    + (button > "Add").on_click(
        state.tasks.append(state.new),
        state.new.restore())
)

generate(root)
