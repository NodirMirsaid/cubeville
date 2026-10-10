"""Builds the standalone Cubeville site (site/index.html) from the game page (index.html).
The artifact page has no <!doctype>/<head>; the site wraps it, adds supabase-js and config.js."""
import pathlib,re
root=pathlib.Path(__file__).parent
SITE='https://nodirmirsaid.github.io/cubeville/'
game=(root/'game.html').read_text(encoding='utf-8')
head=('<!doctype html><html lang="ru"><head><meta charset="utf-8">'
      '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">'
      '<meta name="theme-color" content="#232527">'
      '<title>Cubeville</title>'
      '<meta name="description" content="Безопасный мир для детей: 10 мини-игр, Городок, гардероб и общение только смайликами.">'
      '<meta property="og:title" content="Cubeville">'
      '<meta property="og:description" content="Игры, Городок и гардероб. Общение только смайликами и стикерами.">'
      '<meta property="og:type" content="website">'
      f'<meta property="og:url" content="{SITE}">'
      f'<meta property="og:image" content="{SITE}og.png">'
      '<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
      '<meta name="twitter:card" content="summary_large_image">'
      '<link rel="manifest" href="manifest.json">'
      '<link rel="icon" type="image/png" href="icon-192.png">'
      '<link rel="apple-touch-icon" href="apple-touch-icon.png">'
      '<meta name="apple-mobile-web-app-capable" content="yes">'
      '<meta name="mobile-web-app-capable" content="yes">'
      '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">'
      '<meta name="apple-mobile-web-app-title" content="Cubeville">'
      '<style>html,body{margin:0;height:100%}:root{padding:env(safe-area-inset-top,0px) 0 env(safe-area-inset-bottom,0px)}[hidden]{display:none!important}</style>'
      '</head><body>')
V='2'  # bump on every release so phones don't keep an old cached copy
libs=(f'<script src="config.js?v={V}"></script>'
      f'<script src="supabase.js?v={V}"></script>')  # supabase-js 2.45.4 UMD, self-hosted (CDN may be blocked)
i=game.index('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/')
out=head+game[:i]+libs+game[i:]+'</body></html>'
(root/'site').mkdir(exist_ok=True)
(root/'site'/'index.html').write_text(out,encoding='utf-8')
cfg=root/'site'/'config.js'
if not cfg.exists():
    cfg.write_text('// Fill in after creating the Supabase project (see SETUP.md). Leave empty to play offline.\nwindow.CUBEVILLE_CONFIG={url:"",anonKey:""};\n',encoding='utf-8')
import json
(root/'site'/'manifest.json').write_text(json.dumps({'name':'Cubeville','short_name':'Cubeville','start_url':'./','display':'fullscreen','orientation':'any','background_color':'#232527','theme_color':'#232527',
  'icons':[{'src':'icon-192.png','sizes':'192x192','type':'image/png'},{'src':'icon-512.png','sizes':'512x512','type':'image/png'}]},ensure_ascii=False,indent=1),encoding='utf-8')
print('site/index.html',len(out),'bytes')
