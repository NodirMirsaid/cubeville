"""Builds app/www (the game bundled for the iOS/Android app) from ../game.html.

Everything the game needs ships inside the app: three.js, the Montserrat font,
supabase-js and config.js. No third-party requests (Apple Kids / Google Families).
Run: python3 make_www.py   (then: npx cap sync)
"""
import pathlib, re, shutil

APP = pathlib.Path(__file__).parent
ROOT = APP.parent
WWW = APP / 'www'
NM = APP / 'node_modules'

game = (ROOT / 'game.html').read_text(encoding='utf-8')

# 1) Google Fonts -> bundled Montserrat
game, n = re.subn(r'<link rel="preconnect"[^>]*>\s*', '', game)
game, m = re.subn(r'<link rel="stylesheet" href="https://fonts\.googleapis\.com[^>]*>', '<link rel="stylesheet" href="fonts/fonts.css">', game)
assert m == 1, 'google fonts link not found'

# 2) three.js from CDN -> bundled
CDN3 = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
assert game.count(CDN3) == 1, 'three.js CDN tag not found'
game = game.replace(CDN3, '<script src="config.js"></script><script src="supabase.js"></script><script src="three.min.js"></script>')
assert 'https://cdn' not in game and 'googleapis' not in game, 'a CDN reference is left'

head = ('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">'
        '<meta name="theme-color" content="#232527">'
        '<meta name="format-detection" content="telephone=no">'
        '<title>Cubeville</title>'
        '<style>html,body{margin:0;height:100%;background:#232527;overscroll-behavior:none;'
        '-webkit-user-select:none;user-select:none;-webkit-touch-callout:none;-webkit-tap-highlight-color:transparent}'
        ':root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}</style>'
        '</head><body>')

if WWW.exists():
    shutil.rmtree(WWW)
(WWW / 'fonts').mkdir(parents=True)
(WWW / 'index.html').write_text(head + game + '</body></html>', encoding='utf-8')

shutil.copy(NM / 'three/build/three.min.js', WWW / 'three.min.js')
shutil.copy(ROOT / 'supabase.js', WWW / 'supabase.js')
shutil.copy(ROOT / '591.supabase.js', WWW / '591.supabase.js')
shutil.copy(ROOT / 'config.js', WWW / 'config.js')

RANGES = {
    'latin': 'U+0000-00FF,U+0131,U+0152-0153,U+02BB-02BC,U+02C6,U+02DA,U+02DC,U+0304,U+0308,U+0329,U+2000-206F,U+20AC,U+2122,U+2191,U+2193,U+2212,U+2215,U+FEFF,U+FFFD',
    'cyrillic': 'U+0301,U+0400-045F,U+0490-0491,U+04B0-04B1,U+2116',
}
css = []
for sub, rng in RANGES.items():
    for w in (600, 700, 800, 900):
        f = f'montserrat-{sub}-{w}-normal.woff2'
        shutil.copy(NM / '@fontsource/montserrat/files' / f, WWW / 'fonts' / f)
        css.append(f"@font-face{{font-family:'Montserrat';font-style:normal;font-weight:{w};font-display:swap;"
                   f"src:url({f}) format('woff2');unicode-range:{rng}}}")
(WWW / 'fonts' / 'fonts.css').write_text('\n'.join(css) + '\n', encoding='utf-8')

size = sum(p.stat().st_size for p in WWW.rglob('*') if p.is_file())
print(f'www ready: {size/1024:.0f} KB')
