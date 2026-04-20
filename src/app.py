from camel import *

router = makeRouter()

router.route(
    "/",
    div(
        h1("Hello World"),
        p(
            "This is a simple static site in Camel ",
            pre("v0.1").style("display", "inline"),
            "!",
        ),
    ),
)

router.route("/error404", div(h1("Error 404: Page Not Found!")))

router.generate()
