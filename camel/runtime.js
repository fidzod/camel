const root = document.getElementById("root");

function renderElement(elem) {
    const type = elem[0];

    if (type === "text") {
        const text = elem[1];
        return document.createTextNode(text);
    }

    const tag = elem[1], attrs = elem[2], children = elem[3];

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

