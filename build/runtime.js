const root = document.getElementById("root");

function renderElement(elem) {
    const tag = elem[0];

    if (tag === "text") {
        const text = elem[1];
        return document.createTextNode(text);
    }

    const attrs = elem[1], children = elem[2];

    let e = document.createElement(tag);
    for (let child of children) e.appendChild(renderElement(child));
    for (let attr of attrs) e.setAttribute(attr[0], attr[1]);

    return e
}

function renderRoute() {
    let loc = document.location.hash.split("#")[1] || "/";
    let page = site[loc] || site["/error404"];
    while (root.firstChild) root.removeChild(root.firstChild)
    root.appendChild(renderElement(page));
}

window.addEventListener("hashchange", renderRoute);
window.addEventListener("load", renderRoute);

