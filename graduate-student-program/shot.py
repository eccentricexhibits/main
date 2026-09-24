import sys, pathlib
from playwright.sync_api import sync_playwright
d = pathlib.Path(__file__).parent
with sync_playwright() as p:
    b = p.chromium.launch(executable_path='/opt/pw-browsers/chromium-1194/chrome-linux/chrome')
    pg = b.new_page(viewport={'width':1200,'height':627}, device_scale_factor=float(sys.argv[3]) if len(sys.argv)>3 else 1)
    pg.goto((d/f'graphic_{sys.argv[1]}.html').as_uri()); pg.wait_for_timeout(400)
    pg.screenshot(path=str(d/sys.argv[2]))
    b.close()
