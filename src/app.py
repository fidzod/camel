from camel import *

camel = Router()

camel.route("/")(
    h1("Shopping List"),
    ul(
        each(state.shoppingList)(
            li(
                var.item,
                " ",
                button("X").onClick(delete(state.shoppingList, var.index)),
            )
        )
    ),
    input_().bind(state.newItem).placeholder("Add item..."),
    button("Add").onClick(
        append(state.shoppingList, state.newItem), set_(state.newItem, "")
    ),
).useState(shoppingList=[], newItem="")

camel.generate()
