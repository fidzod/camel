# Camel 🐪

Camel is a tool for building small reactive sites and SPAs in Python. You
write pages as plain Python, and Camel compiles them to a small,
self-contained, vanilla JS bundle.

```python
from camel import *

page = let(name="World!").in_(
    (h1 > ("Hello, " + state.name))
    + input_.bind(state.name)
)
```

Camel compiles your pages into a JSON intermediate representation: typed
nodes describe the UI tree, state, events, and actions. A small JS
runtime interprets this IR, renders the initial DOM, listens for state
changes, re-renders only affected UI (state references, `ForEach` loops,
`If` conditions, bound inputs), and runs actions when events fire.

This is an experimental project, and doesn't claim to be a production
framework. Being intentionally minimal might make it ideal for personal
projects, small dashboards, and the like.

## What's new in v6

v6 is a ground-up rewrite of v5. The headline changes:

- **A cleaner API.** Classes are emmet-style attribute access
  (`div.card.featured`), trees compose with `>` (append a child) and `+`
  (join as siblings), every node is immutable, and `.style(...)` gives you
  CSS scoped to the subtree it's attached to. `Elem(**attrs)` sets
  HTML attributes (`a(href="...")`) - see `docs/dsl.md`.
- **No more invisible elements.** v5 wrapped every reactive value, and
  every `If`/`ForEach`, in an extra `<span>` that never appeared in the
  tree you wrote - which could silently break a `:nth-child` selector or
  a flex/grid layout depending on sibling position. In v6, a reactive
  value is a real text node, and `If`/`ForEach` use HTML comment markers
  as their boundaries instead of a wrapper element.
- **Routing, not hash routing.** Hash routing has been replaced. Pages live
  under `src/pages/` (one directory per route, see `docs/routing.md`), and
  routes use clean URLs via the History API. `cml build` produces a single-page
  app - one `index.html` shell for the whole site - so your host needs to be
  configured to serve that shell for any path (a rewrite rule on
  Netlify/Vercel/Cloudflare Pages, `try_files` on nginx, and similar). An
  identical `build/404.html` is also written for hosts (GitHub Pages included)
  that only know that filename-based fallback, not a rewrite rule.
  Trade-off: navigating between pages is a real page load, not an instant
  client-side swap - nothing currently intercepts link clicks.
- **A cleaner, documented IR.** v6's IR follows explicit rules
  about shape, discriminated variants, and how absence is represented,
  documented in full in `docs/ir.md`.
- **A real build story.** `cml init` scaffolds a new project; `cml build`
  needs nothing calling it from inside your pages (no more an explicit
  `generate()` call at the bottom of a script).

## Project Status

v6 is under active development and not yet published anywhere - install
from a clone of this repository. See Known Limitations and Issues below
before reaching for it beyond personal projects and experiments.

## Install & CLI

```sh
git clone <this repo>
cd camel
pip install -e .
```

`cml init`  - scaffold a new project in the current directory

`cml build` - compile `src/pages/` to `build/`

`cml watch` - build and serve with live reload at localhost:5000

`cml fmt`   - format the current directory with black

## Project Structure

This repository (the framework itself):

`camel/`  - the framework

`tests/`  - tests for the framework

`docs/`   - reference docs for the DSL, the IR, routing, and examples

A project you build with Camel (e.g. via `cml init`) is a separate
directory, structured like:

`src/pages/`      - one directory per route, each containing an `app.py` that exports `page`

`src/components/` - shared pieces your pages import

`static/`         - files copied into `build/` as-is

`build/`          - generated output, do not edit

## Examples

```python
from camel import *

page = let(clicks=0).in_(
    (h3 > (
        state.clicks
            + " "
            + if_(state.clicks == 1).then("click").otherwise("clicks")
    ))
    + (button > "Click Me!").on_click(state.clicks.add(1))
)
```

More - lists, input binding, scoped styles, composition - in
`docs/examples.md`.

## Docs

- `docs/dsl.md` - the Python DSL (`camel.dsl` + `camel.prelude`): elements,
  attributes, state, binding, conditionals, events, actions, lists.
- `docs/ir.md` - the JSON IR every page compiles to.
- `docs/routing.md` - how pages become routes, how a site compiles and
  builds, and the `/404` convention.
- `docs/examples.md` - example pages and components.

## Known Limitations and Issues

- Not published to PyPI - installing means cloning this repo.
- Needs a host configured to serve `index.html` for every path (SPA
  fallback) - dropping `build/` on an unconfigured static host no longer
  works out of the box the way a per-route build would (though
  `build/404.html` gives GitHub-Pages-style hosts a fallback - see above).
- No dynamic route segments yet (eg. `pages/blog/[slug]/app.py`)
- No content pre-rendering or hydration - every route's shell is empty
  until JS loads, which isn't ideal for SEO or no-JS clients.
- Navigating between routes is always a full page load - there's no
  client-side transition.
- Attribute values (`a(href=...)`) are fixed strings - no reactive,
  state-bound attribute yet.
- No API integration (`fetch`/`post`) - this existed in v5 and hasn't
  been ported to v6 yet.
- Deploying under a subpath (e.g. a GitHub Pages *project* site served
  from `/reponame/` rather than the domain root) isn't supported - asset
  references are root-absolute, assuming the site is served from `/`.

## Next Steps

- Dynamic route segments (`[slug]`).
- Publish to PyPI.
- Possibly content pre-rendering/hydration.

## History

v1 was a refactor of a single-file static site generator written by me in
2017. v2 is a ground-up redesign with a new API and a reactive runtime. v3
introduced lists, loops, input binding and additional primitives. v4
introduced API integration via fetch and post. v5 entailed a full rewrite
of the serialisation layer introducing a typed atom system. v6 is a
ground-up rewrite introducing file-based routing, a cleaner and documented
IR, and an API with no hidden elements in the rendered DOM.
