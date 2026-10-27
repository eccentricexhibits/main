#!/usr/bin/env python3
"""Build one offline HTML file with the desktop and mobile event mockups."""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
TEMPLATE = ROOT / 'tools' / 'mockup'


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return f'data:{mime};base64,' + base64.b64encode(path.read_bytes()).decode('ascii')


def inline_css(css: str) -> str:
    def replace(match: re.Match) -> str:
        ref = match.group(1).strip().strip('\"\'')
        if ref.startswith(('data:', '#')):
            return match.group(0)
        if ref.startswith('fonts/'):
            # Fonts belong to the owner's original handoff; keep external and do not redistribute.
            return 'url("Source/dist/' + ref + '")'
        path = DIST / ref
        if not path.is_file():
            raise FileNotFoundError(path)
        return 'url("' + data_uri(path) + '")'
    return re.sub(r'url\(([^)]+)\)', replace, css)


def once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f'Expected one matching application fragment: {old[:70]}')
    return text.replace(old, new)


def build() -> str:
    styles = inline_css('\n'.join((DIST / name).read_text() for name in
                                  ['styles.css', 'gradient-panels.css', 'mobile.css', 'editorial-event-identity.css']))
    app = (DIST / 'app.js').read_text()
    app = once(app, 'src="${E(src)}"', 'src="${E(window.REMARKABLE_ASSETS[src] || src)}"')
    app = once(app, 'if(updateURL){const url=new URL(location.href);',
               "if(updateURL && location.protocol !== 'about:'){const url=new URL(location.href);")
    app = once(app, 'new URLSearchParams(location.search)',
               'new URLSearchParams(window.REMARKABLE_PREVIEW_ROUTE.search)')
    app = once(app, 'const hashMatch=location.hash.match(',
               'const hashMatch=window.REMARKABLE_PREVIEW_ROUTE.hash.match(')
    app = once(app, 'document.getElementById(location.hash.slice(1))',
               'document.getElementById(window.REMARKABLE_PREVIEW_ROUTE.hash.slice(1))')
    pages = {}
    for page in ['index', 'agenda', 'speakers', 'faq']:
        html = (DIST / f'{page}.html').read_text()
        html = re.sub(r'<link\b[^>]*>', '', html)
        html = re.sub(r'<script\b[^>]*\bsrc=[^>]*>\s*</script>', '', html)
        pages[page] = html
    assets = {path.relative_to(DIST).as_posix(): data_uri(path)
              for path in sorted((DIST / 'assets').rglob('*')) if path.is_file()}
    payload = {'format': 'remarkable-mockup-v1', 'styles': styles, 'app': app,
               'copy': json.loads((DIST / 'content' / 'copy.json').read_text()),
               'pages': pages, 'assets': assets}
    encoded = json.dumps(payload, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    viewer = (TEMPLATE / 'viewer.html').read_text()
    css = inline_css((TEMPLATE / 'viewer.css').read_text())
    script = (TEMPLATE / 'viewer.js').read_text().replace('</script', '<\\/script')
    viewer = viewer.replace('<!-- MOCKUP_STYLES -->', '<style>' + css + '</style>')
    viewer = viewer.replace('<!-- MOCKUP_DATA -->', '<script id="mockup-data" type="application/json">' + encoded + '</script>')
    return viewer.replace('<!-- MOCKUP_SCRIPT -->', '<script>' + script + '</script>')


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=DIST / 'mockup.html')
    args = parser.parse_args()
    result = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(result)
    print(f'{args.output.resolve()} ({args.output.stat().st_size:,} bytes)')


if __name__ == '__main__':
    main()
