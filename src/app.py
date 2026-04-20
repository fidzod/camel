from camel import *

camel = Router()

camel.route("/",
    h1("Hello World"),
    p(
        "This is a simple static site in Camel ",
        pre("v0.1").style("display", "inline"),
        "!",
    ),
)

camel.route("/error404",
    h1("Error 404"),
    p("Page not found.")
)

camel.generate()
