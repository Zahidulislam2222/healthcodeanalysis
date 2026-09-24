# Third-party notices

This repository's own source code is released under the [MIT License](LICENSE). It includes or depends on the third-party components below, each under its own licence.

## Bundled in this repository

| Component | Files | Licence |
|---|---|---|
| DM Sans (Regular, Medium, SemiBold, Bold) | `frontend/assets/fonts/dm-sans.woff2`, `font-0.ttf`–`font-3.ttf` | SIL Open Font License 1.1: `frontend/assets/fonts/dmsans-OFL.txt` |
| Instrument Serif (Regular, Italic) | `frontend/assets/fonts/instrument-serif*.woff2`, `font-4.ttf`, `font-5.ttf` | SIL Open Font License 1.1: `frontend/assets/fonts/instrumentserif-OFL.txt` |
| Demonstration article images | `frontend/assets/images/` | Imported from the original demonstration site. **Provenance and rights must be verified before commercial reuse.** |
| AI-generated hero artwork | `frontend/assets/neural-generated.webp`, `neural-film.mp4`, `neural-film-poster.webp` | Created for this project; see [AI transparency](docs/legal/AI-TRANSPARENCY.md) |
| Blender-rendered prototype artwork | `frontend/assets/evidence-atlas.*`, `neural-frontier.*` (from `frontend/artwork/render_*.py`) | Created for this project under the repository licence |

## Runtime platforms (not bundled; installed from official sources)

| Component | Licence |
|---|---|
| WordPress | GPL-2.0-or-later |
| Elementor (Free) | GPL-3.0 |
| Advanced Custom Fields (free) | GPL-2.0-or-later |
| Two Factor | GPL-2.0-or-later |
| Ultimate Addons for Elementor / header-footer builder (free) | GPL-2.0-or-later |
| Hello Elementor theme | GPL-3.0 |
| NGINX | BSD-2-Clause |
| Caddy | Apache-2.0 |
| MySQL-compatible database image | As published by its vendor |

## Python dependencies (`requirements.txt`)

| Package | Licence |
|---|---|
| requests | Apache-2.0 |
| Jinja2 | BSD-3-Clause |
| beautifulsoup4 | MIT |
| Pillow | MIT-CMU (HPND) |
| tinycss2 | BSD-3-Clause |

## JavaScript tooling

| Package | Licence |
|---|---|
| wrangler (dev dependency of `workers/askme`) | MIT OR Apache-2.0 |

Licence information was compiled from each project's published licence at the time of writing. The licence text shipped with each component is authoritative. Open an issue if an attribution is missing or wrong.
