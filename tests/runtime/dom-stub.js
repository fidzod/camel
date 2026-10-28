// A small hand-rolled DOM stub - just enough to exercise what runtime.js
// actually uses (sibling chains, fragment flattening, text/class mutation,
// event listeners) without a jsdom dependency. Grow it only when a test
// genuinely needs something it doesn't yet support.

class FakeNode {
  constructor(kind) {
    this.kind = kind;
    this.parentNode = null;
    this.childNodes = [];
    this.tag = null;
    this.text = null;
    this._cls = "";
    this._listeners = {};
  }

  get nextSibling() {
    if (!this.parentNode) return null;
    const i = this.parentNode.childNodes.indexOf(this);
    return this.parentNode.childNodes[i + 1] ?? null;
  }

  set className(v) { this._cls = v; }
  get className() { return this._cls; }

  set textContent(v) { this.text = v; }
  get textContent() { return this.text; }

  _flatten(node) {
    return node.kind === "fragment" ? [...node.childNodes] : [node];
  }

  append(...nodes) {
    nodes.forEach(node => {
      this._flatten(node).forEach(real => {
        if (real.parentNode) real.remove();
        real.parentNode = this;
        this.childNodes.push(real);
      });
      if (node.kind === "fragment") node.childNodes = [];
    });
  }

  before(...nodes) {
    const parent = this.parentNode;
    const i = parent.childNodes.indexOf(this);
    const flat = nodes.flatMap(node => this._flatten(node));
    flat.forEach(real => {
      if (real.parentNode) real.remove();
      real.parentNode = parent;
    });
    parent.childNodes.splice(i, 0, ...flat);
    nodes.forEach(node => { if (node.kind === "fragment") node.childNodes = []; });
  }

  remove() {
    if (!this.parentNode) return;
    const i = this.parentNode.childNodes.indexOf(this);
    this.parentNode.childNodes.splice(i, 1);
    this.parentNode = null;
  }

  addEventListener(type, fn) { this._listeners[type] = fn; }
  dispatch(type) { if (this._listeners[type]) this._listeners[type](); }

  toString() {
    if (this.kind === "text") return this.text;
    if (this.kind === "comment") return `<!--${this.text}-->`;
    if (this.kind === "fragment") return this.childNodes.map(c => c.toString()).join("");
    const cls = this._cls ? ` class="${this._cls}"` : "";
    return `<${this.tag}${cls}>${this.childNodes.map(c => c.toString()).join("")}</${this.tag}>`;
  }
}

// A fresh document per call - tests should never share one, so state from
// one test can't leak into another even though the required runtime.js
// module itself is cached and shared across the whole test run.
function makeDocument() {
  const root = new FakeNode("elem");
  root.tag = "div";
  return {
    createElement(tag) { const n = new FakeNode("elem"); n.tag = tag; return n; },
    createTextNode(text) { const n = new FakeNode("text"); n.text = text; return n; },
    createComment(text) { const n = new FakeNode("comment"); n.text = text; return n; },
    createDocumentFragment() { return new FakeNode("fragment"); },
    getElementById() { return root; },
    addEventListener() {}, // DOMContentLoaded - tests call render() directly, never need this to fire
    _root: root,
  };
}

module.exports = { makeDocument };
