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
likewise one file, combining every page's `StyleScope` rules. Both live under
a reserved `_camel/` directory in the build output, alongside the runtime -
`_camel/site.js`, `_camel/style.css`, `_camel/runtime.js` - so nothing Camel
generates can collide with a file you put in `static/`.

## Output

Camel builds a single-page app: `write_site` writes exactly one `index.html`
shell at the build root, referencing `_camel/site.js`/`style.css`/`runtime.js`
by root-absolute path.

Because it's a single file, the host serving `build/` has to be configured to
return that same shell for any path a browser requests directly (a deep link,
a shared URL, a hard refresh) rather than 404ing - a rewrite rule on
Netlify/Vercel/Cloudflare Pages, `try_files` on nginx, and similar. Dropping
`build/` on a plain static host with no such rule no longer works out of the
box the way a per-route build did.

Anything in `static/` copies into `build/` as-is, at the same path - so
`static/favicon.ico` becomes `build/favicon.ico`, `static/robots.txt` becomes
`build/robots.txt`, and so on. A file named `index.html` in `static/` is no
exception: it overrides the generated shell at `build/index.html`, same as
any other static file landing where its name says.

## Navigation

On load, the runtime matches `location.pathname` against `site` - stripping a
trailing slash first, so `/about` and `/about/` resolve to the same entry, and
renders whichever page matches. Internal links are ordinary, un-intercepted `<a
href="...">` elements: a click is a normal full-page navigation. There's no
client-side routing layer sitting in front of native navigation.

## Not Found

`pages/404/app.py` is a route like any other which compiles to `/404` through
the same mechanism as any other page. If there is no 404 route provided then a
default will be built in its place. Alongside the single shell, the build also
writes `build/404.html`, identical to `build/index.html` (including a
`static/index.html` override) - some static hosts, GitHub Pages included,
only know how to fall back to a file specifically named `404.html`, so it's
kept as a second entry point to the same shell for hosts that need it. The
runtime's fallback is the same mechanism as an ordinary route miss: whatever
`location.pathname` doesn't match in `site` renders `site["/404"]` instead.
