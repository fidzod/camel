from camel import *

camel = Router()

API = "http://localhost:8000"

camel.route("/")(
    h3("Todo:"),
    ul(
        for_each(state.todos).as_('todo')(
            p(
                button("X")
                    .on_click(delete(API, "todos", var.todo.id))
                    .style("margin-right", "10px"),
                var.todo.text,
            )
        )
    ),
    input_()
        .placeholder("Add something")
        .bind(state.newItem),
    button("Add")
        .on_click(
            post(API, "todos", text=state.newItem),
            set_(state.newItem, "")
        ),
).use_state(todos=fetch(API, "todos"), newItem="")

camel.generate()
