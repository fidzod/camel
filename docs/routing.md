# Camel Routing

Reference for how `camel.route.load_pages` discovers pages under
`src/pages/` and compiles them into the routed site `camel.site.write_site`
produces. Covers what's implemented so far.

## Shape

A route is a directory under `src/pages/` containing a file named
`app.py` that exports a module-level `page: Node`. The route's path is
the directory's path relative to `src/pages/`, not the filename -
`app.py` is the same reserved name at every depth, so nesting is just
nesting directories deeper (`pages/foo/bar/app.py` → `/foo/bar`).
`pages/app.py` itself, at zero depth, is the root route (`/`).

`load_pages` walks `src/pages/` for every `app.py`, independent of
anything else under `src/` - a page never registers itself anywhere,
and there's no central list of routes to keep in sync by hand.

A page that fails to import, or imports but doesn't export `page`,
doesn't abort discovery at the first one found - every broken page is
collected and raised together, as one `ExceptionGroup`, and nothing
compiles if any page failed.

## Compiling

Every discovered page compiles into one `site.js`, keyed by route path, so a
visitor's first page load already has every route's `Node` tree on hand; moving
between routes never needs a second fetch mid-navigation. `style.css` is
likewise one file, combining every page's `StyleScope` rules.

## Output

A client-rendered site only works on a plain static host (GitHub Pages
and similar) if there's a real file sitting at every path a browser
might request directly, otherwise a hard refresh or a shared link
404s before any JS gets a chance to run. So `write_site` writes one
`index.html` shell per route (`build/about/index.html` for `/about`),
not just one at the root. Every shell is identical, referencing the one
shared `site.js`/`runtime.js`/`style.css` by root-absolute path
(`/site.js`, not `site.js`), so it doesn't matter which depth a given
shell is served from.

## Navigation

On load, the runtime matches `location.pathname` against `site` - stripping a
trailing slash first, so `/about` and `/about/` resolve to the same entry, and
renders whichever page matches. Internal links are ordinary, un-intercepted `<a
href="...">` elements: a click is a normal full-page navigation. There's no
client-side routing layer sitting in front of native navigation.

## Not Found

`pages/404/app.py` is a route like any other which compiles to `/404` through
the same mechanism as any other page. If there is no 404 route provided then a
default will be built in its place. `write_site` writes `build/404.html`,
identical to every other shell, because that's the filename static hosts look
for when nothing else matches a request. The runtime's fallback is the same
mechanism as an ordinary route miss: whatever `location.pathname` doesn't
match in `site` renders `site["/404"]` instead.
