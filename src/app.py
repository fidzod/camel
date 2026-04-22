from camel import *

API = "http://127.0.0.1:8000"

camel = Router()

camel.route("/")(
    h3("Todo:"),
    ul(
        each(state.todos).as_(var.todo)(
            li(
                var.todo.text,
                " ",
                button("X").onClick(
                    post(API, "todos", var.todo.id).method("DELETE")
                ),
            )
        )
    ),
    input_().placeholder("New todo...").bind(state.new),
    button("Add").onClick(post(API, "todos", text=state.new)),
).useState(todos=fetch(API, "todos"), new="")

camel.generate()
