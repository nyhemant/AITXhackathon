"""Fill empty alt="" on content photos from names already on the page."""
import re, html as H
IMG = re.compile(r'<img\b[^>]*?>', re.S)
EMO = re.compile(r'[\U0001F000-\U0001FFFF\u2600-\u27BF\uFE0F\u200d]+')
def _clean(t):
    t = re.sub(r'<[^>]+>', '', t); t = H.unescape(t); t = EMO.sub('', t)
    return re.sub(r'\s+', ' ', t).strip(' ·—-')
NAME_PATS = [
    re.compile(r'<span class="[^"]*\b(?:try-card-name|[a-z-]*-name)\b[^"]*"[^>]*>(.*?)</span>', re.S),
    re.compile(r'<strong[^>]*>(.*?)</strong>', re.S),
    re.compile(r'<h[234][^>]*>(.*?)</h[234]>', re.S),
]
def _name_after(s, end):
    # look until the enclosing </a>, then the enclosing </article>/<li>/<figure>
    for stop in (r'</a>', r'</article>|</li>|</figure>'):
        m = re.compile(stop).search(s, end)
        if not m or m.start() - end > 1500: continue
        t = _first_name(s[end:m.start()])
        if t: return t
    return ''
def _first_name(seg):
    for p in NAME_PATS:
        n = p.search(seg)
        if n:
            t = _clean(n.group(1))
            if 2 <= len(t) <= 80: return t
    return ''
def card_names(root):
    import glob, os
    out = {}
    for f in glob.glob(os.path.join(root, 'field-pack/cards/*/index.html')):
        m = re.search(r'<h1[^>]*>(.*?)</h1>', open(f, encoding='utf-8').read(), re.S)
        if m: out[f.split("/")[-2]] = re.sub(r" Animal Card for Kids$", "", _clean(m.group(1)))
    return out
def fill(s, card_names=None):
    out = []; last = 0; n = 0
    for m in IMG.finditer(s):
        tag = m.group(0)
        if not re.search(r'\salt=""', tag): continue
        if re.search(r'\shidden\b|aria-hidden="true"|start-home-fallback', tag):
            if 'start-home-fallback' in tag and 'aria-hidden' not in tag:
                new = tag.replace('alt=""', 'alt="" aria-hidden="true"', 1)
                out.append(s[last:m.start()]); out.append(new); last = m.end()
            continue
        name = _name_after(s, m.end())
        if not name and card_names:
            a = s.rfind('<a ', 0, m.start()); ca = s.rfind('</a>', 0, m.start())
            if a > ca:
                h = re.search(r'href="/field-pack/cards/([a-z0-9-]+)/', s[a:m.start()])
                if h: name = card_names.get(h.group(1), '')
        if not name: continue
        new = tag.replace('alt=""', 'alt="%s"' % H.escape(name, quote=True), 1)
        out.append(s[last:m.start()]); out.append(new); last = m.end(); n += 1
    out.append(s[last:]); return ''.join(out), n


# 2026-11-04: contextual links to weakly linked cards, only on pages whose own
# content already names the animal / place (polar bear hunt line; Cuyahoga Valley related link).
_CUY_OLD = 'Cuyahoga Valley National Park</a> <small>Peninsula, OH</small>'
_CUY_NEW = ('Cuyahoga Valley National Park</a> <small>Peninsula, OH · '
            '<a href="/field-pack/cards/cuyahoga-towpath/">Towpath trail card</a></small>')
_POLAR = {
    'detroit-zoo': 'Arctic Ring of Life',
    'point-defiance-zoo': 'Polar bear',
}
def add_card_links(slug, s):
    if '/field-pack/cards/cuyahoga-towpath/' not in s and _CUY_OLD in s:
        s = s.replace(_CUY_OLD, _CUY_NEW, 1)
    if slug in _POLAR and '/field-pack/cards/polar-bear/' not in s and 'polar bear' in s.lower():
        p = ('<p class="seo-card-link">Spotting the polar bear? Open the '
             '<a href="/field-pack/cards/polar-bear/">polar bear card</a> for a photo, quiz and talk prompts.</p>\n')
        i = s.find('</article>')
        if i > 0: s = s[:i] + p + s[i:]
    return s
