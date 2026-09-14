# HealthCode — Neural Frontier

A local editorial frontend for the existing WordPress content snapshot. Graphite, mint and copper; a generated neural illustration and scroll-controlled eight-second film; locally served fonts and browser-only tools.

This directory preserves the design source and local static preview. The public release now uses native WordPress/Elementor; see `../wordpress-native/README.md` and its verification record for current deployment status. The local validation history below does not describe the current public serving stack.

## Preview

From the project root, using Python with the root requirements installed:

```sh
python scripts/build_frontend.py
python scripts/preview_frontend.py
```

The server prints its local URL. Host and port are configured in `frontend/site.config.json`. The generated `frontend-preview/` directory is ignored by Git. No cloud deployment command is part of this workflow.

## Source ownership

- `data/library.json`: normalized imported editorial content, original IDs, and routes. Refresh explicitly with `python scripts/import_frontend_content.py` when a new WordPress export is ready.
- `data/site.json`: publication identity, navigation, curated selections, and interface copy.
- `data/tools.json`: tool definitions, educational coefficients, source references, validation messages, and maintained usage guides. Imported tool articles remain in the normalized source; current tool pages display instructions matching their implemented behavior.
- `site.config.json` and `scripts/frontend_settings.py`: build paths, local server settings, limits, and typed configuration loading. The browser makes no paid API calls. Offline media production uses `media.config.json` and a private `OPENROUTER_API_KEY` documented in `.env.example`.
- `templates/`: page structures and presentation copy. Jinja autoescaping remains enabled for imported content.
- `styles/`: visual design and motion. `frontier.css` supplies the current visual system over the retained base styles; homepage-only `hero.css` owns the refined hero composition.
- `scripts/`: search, reading list, dialog/menu behavior, local tools, and bounded motion.
- `artwork/`: Blender prototype source and the revision brief. The final image/video were generated through the approved paid pilot; raw media stays ignored. Fonts and their open-source licenses are in `assets/fonts/`.

The build manifest removes obsolete generated files on subsequent builds and preserves unmanaged files. Keep manual changes in source files instead of editing generated HTML.

## Checks

```sh
python -m unittest discover -s tests -p test_frontend.py
node --test frontend/tests/calculations.test.mjs
node --check frontend/scripts/app.mjs
```

See `VALIDATION.md` for the recorded local verification and its limits.
