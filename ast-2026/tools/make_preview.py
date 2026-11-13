import json
s=open('/home/claude/danceauthority.github.io/ast-2026/index.html').read()
css=open('/home/claude/vendor/package/dist/leaflet.css').read()
js=open('/home/claude/vendor/package/dist/leaflet.js').read().replace('</script','<\\/script')
data=open('/home/claude/danceauthority.github.io/ast-2026/data.js').read().replace('</','<\\/')
tiles=json.dumps(json.load(open('/home/claude/build/tiles.json')),separators=(',',':'))
s=s.replace('<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="">','<style>'+css+'</style>')
s=s.replace('<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin=""></script>','<script>'+js+'</script>')
s=s.replace('<script src="data.js"></script>','<script>'+data+'</script>')
s=s.replace('<script src="config.js"></script>','<script>window.AST_FIREBASE=null;window.AST_PREVIEW=true;window.AST_TILES='+tiles+';</script>')
assert 'unpkg' not in s and 'src="data.js"' not in s
open('/home/claude/build/preview.html','w').write(s); print(round(len(s)/1e6,2),'MB')
