# HealthCode — Neural Frontier

## Brief and acceptance criteria

Build a local, complete, browsable medical-technology publication preview. Preserve all existing content routes, the WordPress source snapshot, and the public deployment. A one-image/one-video pilot was separately approved with a $5 maximum and used $1.891935. Cloud deployment is not authorized.

1. Consistent HealthCode publication identity across homepage, archives, articles, tools, About, and policy pages; no clinic claims, unsolicited login, or unsupported counters.
2. Custom scientific hero artwork, deliberate editorial hierarchy, and responsive layouts for desktop and mobile.
3. Every previous public route is generated locally, including Unicode slugs; unknown paths return a real 404.
4. Search and category filters return actual matching content, with useful empty states.
5. Reading-list controls save and remove articles on this device, including persistence and blocked-storage feedback.
6. Tools have real local input/output behavior; clinical calculations are educational and source-linked, with no patient-data storage.
7. All navigation, dialogs, buttons, menus, image assets, and keyboard interactions function; no missing WordPress chunks or font dependencies.
8. Motion is bounded and optional; reduced motion, keyboard focus, small screens, and media failure remain usable.
9. All copy, limits, routes, asset manifests, and runtime settings have explicit owners; no API credentials or paid requests enter the browser.
10. Local HTTP preview, automated tests, types/lint/security/build checks, and fresh-context review are reported with their actual results. Deployment remains pending user review.

## Art direction

The current revision follows `artwork/REVISION-BRIEF.md`: graphite surfaces, electric mint accents, copper-lit neural artwork, expressive DM Sans typography, a scroll-controlled film, stacked review cards, and a pale practical-tool directory. The medicine/technology metaphor presents an editorial illustration, not a diagnostic product.

The previous ivory Evidence Atlas direction was rejected by the owner. Functional test success was insufficient evidence of design quality. Its source is retained for history, not presented as accepted work.

Desktop uses the eight-second film with native scroll seeking and a pause control. Small screens, reduced motion, and media failure use a still and ordinary document flow. Search, reading lists, and all six tools remain local.

## Configuration ownership

- `site.config.json`: typed build paths, local host/port, runtime limits, image dimensions, content grouping, and client behavior configuration.
- `data/site.json`: brand, routes, page copy, notices, labels, editorial curation, and tool descriptions.
- `data/library.json`: normalized imported WordPress content, retained IDs, image references, source route mapping, and readable content blocks.
- `data/tools.json`: educational equation coefficients, input bounds, worksheet prompts and source URLs.
- `styles/tokens.css`: visual tokens, typography, spacing, surfaces, and motion timing.
- `artwork/scene.json`: local Blender composition/render settings. Editable scene stays local; optimized output is a frontend asset.
- `media.config.json`: offline provider/model IDs, endpoints, budget, timeout, prompts and output paths.
- Secret material: private OpenRouter key in ignored environment/recovery files only.

## Publishing boundary

`scripts/build_frontend.py` renders source templates and normalized content into the ignored local preview directory. `scripts/import_frontend_content.py` can refresh normalized content from an explicit WordPress export snapshot. Generated HTML is never the authoring source. The existing publisher is deliberately unchanged until the owner reviews the local frontend.

## Verification references

- Jinja autoescaping: https://jinja.palletsprojects.com/en/stable/api/
- Blender rendering: https://docs.blender.org/manual/en/latest/render/output/animation.html
- Browser progressive enhancement: https://developer.mozilla.org/en-US/docs/Web/API/View_Transition_API
- Clinical tool source links are recorded alongside their equations in data/tools.json.
