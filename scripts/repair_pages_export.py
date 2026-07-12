from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "pages-demo"
HTML = PAGES / "index.html"


FALLBACK_CSS = """
<style id="hca-static-fixes">
  .jkit-menu .menu-item-has-children { position: relative; }
  .jkit-menu .menu-item-has-children > .sub-menu { display: none; }
  .jkit-menu .menu-item-has-children:hover > .sub-menu,
  .jkit-menu .menu-item-has-children.open > .sub-menu {
    display: block;
    opacity: 1;
    visibility: visible;
  }
  .jkit-menu-wrapper.active { left: 0 !important; }
  .hca-user-btn { display: none !important; }
  .nsl-container, .hca-social-area { display: none !important; }
</style>
"""


FALLBACK_JS = """
<script id="hca-static-fixes-js">
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.jkit-hamburger-menu').forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      var root = button.closest('.jeg-elementor-kit') || document;
      var wrapper = root.querySelector('.jkit-menu-wrapper');
      if (wrapper) wrapper.classList.add('active');
      button.setAttribute('aria-expanded', 'true');
    });
  });
  document.querySelectorAll('.jkit-close-menu').forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      var wrapper = button.closest('.jkit-menu-wrapper');
      if (wrapper) wrapper.classList.remove('active');
      var root = button.closest('.jeg-elementor-kit') || document;
      var opener = root.querySelector('.jkit-hamburger-menu');
      if (opener) opener.setAttribute('aria-expanded', 'false');
    });
  });
  document.querySelectorAll('.jkit-overlay').forEach(function (overlay) {
    overlay.addEventListener('click', function () {
      var root = overlay.closest('.jeg-elementor-kit') || document;
      var wrapper = root.querySelector('.jkit-menu-wrapper');
      var opener = root.querySelector('.jkit-hamburger-menu');
      if (wrapper) wrapper.classList.remove('active');
      if (opener) opener.setAttribute('aria-expanded', 'false');
    });
  });
  document.querySelectorAll('.menu-item-has-children > a').forEach(function (link) {
    link.addEventListener('click', function (event) {
      var toggle = event.target.closest('.dropdown-menu-toggle');
      if (toggle || link.getAttribute('href') === '#') {
        event.preventDefault();
        var item = link.closest('.menu-item-has-children');
        if (item) item.classList.toggle('open');
      }
    });
  });
});
</script>
"""


def main() -> None:
    html = HTML.read_text(encoding="utf-8-sig", errors="ignore")

    html = re.sub(r'\n?<style id="hca-static-fixes">[\s\S]*?</style>\n?', "\n", html)
    html = re.sub(r'\n?<script id="hca-static-fixes-js">[\s\S]*?</script>\n?', "\n", html)

    # Remove Cloudflare challenge/Rocket Loader artifacts captured from the old origin.
    html = re.sub(
        r'<script src="/cdn-cgi/scripts/7d0fa10a/cloudflare-static/rocket-loader\.min\.js"[^>]*></script>',
        "",
        html,
    )
    html = re.sub(
        r"<script>\(function\(\)\{function c\(\)\{[\s\S]*?challenge-platform[\s\S]*?</script>\s*</body>",
        "",
        html,
    )
    html = re.sub(r"<script>[\s\S]*?challenge-platform[\s\S]*?</script>", "", html)

    # Cloudflare Rocket Loader rewrote script types to hashes. Browsers ignore those on Pages.
    html = re.sub(r'type="[a-f0-9]+-text/javascript"', 'type="text/javascript"', html)
    html = re.sub(r"type='[a-f0-9]+-text/javascript'", "type='text/javascript'", html)
    html = re.sub(r'type="[a-f0-9]+-module"', 'type="module"', html)
    html = re.sub(r"type='[a-f0-9]+-module'", "type='module'", html)

    html = html.replace("https:\\/\\/healthcodeanalysis.com\\/wp-content\\/", "https:\\/\\/healthcodeanalysis.pages.dev\\/wp-content\\/")
    html = html.replace("https:\\/\\/healthcodeanalysis.com\\/wp-admin\\/admin-ajax.php", "https:\\/\\/healthcodeanalysis.pages.dev\\/")
    html = html.replace("https:\\/\\/healthcodeanalysis.com\\/wp-content\\/uploads", "https:\\/\\/healthcodeanalysis.pages.dev\\/wp-content\\/uploads")
    html = html.replace("https://healthcodeanalysis.com", "https://healthcodeanalysis.pages.dev")
    html = html.replace("http://127.0.0.1:8888/wp-login.php", "#")

    # Social login and MetForm submissions require PHP. Hide/disable them in the static frontend.
    html = re.sub(r'href="#\?loginSocial=google[^"]*"', 'href="#"', html)
    html = re.sub(r'href="[^"]*loginSocial=google[^"]*"', 'href="#"', html)
    html = html.replace("?hca_logout=true", "#")

    if "</head>" in html:
        html = html.replace("</head>", f"{FALLBACK_CSS}\n</head>", 1)
    body_match = re.search(r"<body[^>]*>", html, flags=re.IGNORECASE)
    if body_match:
        head_and_body_open = html[: body_match.end()]
        body_rest = html[body_match.end() :]
        body_rest = re.sub(
            r"<!DOCTYPE html>|</?html[^>]*>|</?head[^>]*>|<body[^>]*>|</body>",
            "",
            body_rest,
            flags=re.IGNORECASE,
        )
        html = head_and_body_open + body_rest + FALLBACK_JS + "\n</body>\n</html>\n"
    else:
        html += FALLBACK_JS + "\n</body>\n</html>\n"

    for css_name in [
        "post-1861.css",
        "post-1890.css",
        "post-1904.css",
        "post-1907.css",
        "post-2471.css",
        "post-2732.css",
        "post-2734.css",
    ]:
        css_path = PAGES / "wp-content/uploads/elementor/css" / css_name
        css_path.parent.mkdir(parents=True, exist_ok=True)
        if not css_path.exists():
            css_path.write_text("/* Elementor generated CSS unavailable in backup; inline styles are preserved in index.html. */\n", encoding="utf-8")

    (PAGES / "_redirects").write_text("/* /index.html 200\n", encoding="utf-8")
    HTML.write_text(html, encoding="utf-8")
    print("Repaired static export")


if __name__ == "__main__":
    main()
