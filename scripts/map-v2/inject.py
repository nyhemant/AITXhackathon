import re,sys
SRC='/workspace/kz-map-mock/static/start/index.html'
OUT='/workspace/kz-map-tools/out/'
for d in 'ab':
    S='/workspace/kz-map-mock/static/start/'
    open(S+f'home-map-v2-{d}.css','w').write(open(S+'home-map-v2.css').read()+'\n'+open(S+f'map-v2-{d}-v1.css').read())
    h=open(SRC).read()
    places=open(OUT+f'fragment-{d}-places.html').read()

    world=open(OUT+f'fragment-{d}-world.html').read()
    i=h.index('<div id="home-places-map"'); j=h.index('<div id="home-pin-card"')
    h=h[:i]+places+'\n      '+h[j:]
    i=h.index('<div class="start-hero-pan" id="start-hero-pan">'); m=re.search(r'<p class="start-pan-hint"[^>]*>[^<]*</p>',h); j=m.end()
    h=h[:i]+world+h[j:]
    h=h.replace('<link rel="stylesheet" href="/start/hero-a-v1.css?v=1" />','<link rel="stylesheet" href="/start/hero-a-v1.css?v=1" />\n  <link rel="stylesheet" href="/start/home-map-v2-%s.css?v=1" />\n  <link rel="preload" href="/start/map-v2/%s-usa-v1.svg?v=1" as="fetch" crossorigin />'%(d,d))
    h=h.replace('<!-- Map pins are % of hero-world-map.jpg (1792×1008); left/top is the figurine center. Wrapper keeps that aspect and cover-crops; tall/mobile left-aligns so Americas stay in frame. -->','<!-- Map v2: animals sit on their habitat points as % of the world plate (a-world-v1.svg, 2000×932). Phones pan sideways; 641px and up shows the whole plate. -->')
    h=h.replace('<script src="/start/home-map-v1.js?v=5"></script>','<script src="/start/home-map-v2.js?v=2"></script>')
    assert 'home-map-v2.js' in h and 'map-v2-%s'%d in h
    open(f'/workspace/kz-map-mock/static/start/mock-{d}.html','w').write(h)
    print(d,len(h))
