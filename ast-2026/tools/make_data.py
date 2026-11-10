import json, re, collections, sys

full = json.load(open('/home/claude/raw/full.json'))
ht = json.load(open('/home/claude/raw/hosts_tiles.json'))
hostmap = {u: h for u, h in ht['hosts']}

L = {l['n']: l for l in full['L']}

LOCRE = re.compile(r'\d{1,3}\. [^.]*?, (?:TX|Texas) ?\d{5}(?:, USA)? Get Directions')

def clean_host(h):
    h = re.split(r' Navigat(?:e|ion) ', h or '')[0].strip()
    if h.startswith('Open '):
        return ''
    # de-dup "X X"
    half = len(h) // 2
    if len(h) > 6 and h[:half].strip() == h[half:].strip():
        h = h[:half].strip()
    return h

def nav_of(seg):
    m = re.search(r'Navigat(?:e|ion) (.*?)(?= Open |$)', seg)
    return m.group(1).strip() if m else ''

def hours_of(seg):
    m = re.search(r'Open (.*)$', seg)
    if not m:
        return ''
    s = m.group(1)
    s = re.split(r' ?What TO expect| ?Featured (?:Hosts|Artists)| ?Back to Explore', s, flags=re.I)[0]
    return s.strip()

def days_of(s):
    if not s:
        return 15  # default to all tour days when not stated
    if 'All Tour Dates' in s:
        return 15
    d = 0
    if re.search(r'\b14', s): d |= 1
    if re.search(r'\b15|14[–-]15', s): d |= 2
    if re.search(r'\b21', s): d |= 4
    if re.search(r'\b22|21[–-]22', s): d |= 8
    return d or 15

def short_hours(s):
    if not s or s.startswith('All Tour Dates'):
        return ''
    s = s.replace(' | ', ' ').replace(':00', '')
    s = re.sub(r'(Saturday|Sunday), Nov\. (\d+)(?:st|nd|rd|th)', lambda m: m.group(1)[:3] + ' ' + m.group(2), s)
    s = re.sub(r'\s+', ' ', s).strip()
    # drop broken "11am -" with no end
    s = re.sub(r'(\d(?:am|pm)) -(?=\s*(?:Sat|Sun|$))', r'\1', s)
    return s[:80]

def split_mediums(m):
    if not m:
        return []
    parts = re.split(r'(?<=[a-z])(?=[A-Z0-9])', m)
    return [p.strip() for p in parts if p.strip()]

TYPE = {'Artist': 'A', 'Art Group': 'G', 'Host': 'H', '': 'H'}

def activities(c):
    m = re.search(r'Activities (.*?)(?= Groups or| Overall| Accessibility| Content|$)', c)
    if not m:
        return []
    return [a for a in re.split(r'(?<=[a-z])(?=[A-Z])', m.group(1)) if a]

FT = json.load(open('/home/claude/raw/fulltext.json'))
HOSTCAT = r'(Retail Business|Commercial Business|Studio Complex|Individual Studio|Gallery|Community Center|Residential|Event Venue|City or County(?: Building)?|Maker Space|Office|Public/Outdoor Space|Dining/Bar|Pop-Up|School|Library|Museum|Church|Place of Worship|Nonprofit|Other)'
def bio_of(o):
    ft = FT.get(o['u'])
    if not ft: return '', '', ''
    h = ft['head'].replace('Skip to content','',1).strip()
    m = re.search(r'Featured (Host & Partner|Artist|Art Group|Host|Group) ', h)
    rest = h[m.end():] if m else h
    nm = o['n'].strip()
    if rest.startswith(nm): rest = rest[len(nm):].strip()
    cat = ''
    if o['t'] in ('Host', ''):
        mm = re.match(HOSTCAT + r'\b\s*', rest)
        if mm: cat = mm.group(1); rest = rest[mm.end():]
    else:
        med = (o['m'] or '').strip()
        if med and rest.startswith(med): rest = rest[len(med):].strip()
        else:
            for part in sorted(split_mediums(med), key=len, reverse=True):
                if rest.startswith(part + ' '): rest = rest[len(part):].strip(); break
    exp = re.sub(r'\s*Back to Explore.*$', '', ft['exp']).strip()
    return rest.strip(), exp, cat
people = []
loc_info = collections.defaultdict(lambda: {'hosts': [], 'nav': [], 'acts': set(), 'fam': 0, 'days': 0, 'hrs': collections.Counter()})

for o in full['out']:
    if not o['l']:
        continue
    url = o['u']
    h = o['h'] or ''
    segs = LOCRE.split(h)
    locs = []
    seen = set()
    for i, (n, addr) in enumerate(o['l']):
        if n in seen:
            continue
        seen.add(n)
        seg = segs[i] if i < len(segs) else ''
        host = ''
        if i == 0:
            host = clean_host(hostmap.get(url, ''))
        else:
            m = re.match(r'\s*Host (.*?)(?= Open | Navigat|$)', seg)
            if m:
                host = m.group(1).strip()
        hrs = hours_of(seg)
        locs.append({'n': n, 'host': host, 'nav': nav_of(seg)[:140], 'hrs': hrs, 'days': days_of(hrs)})
        if n in L and 'a' not in L[n]:
            L[n]['a'] = addr
    t = TYPE.get(o['t'], 'H')
    c = o['c'] or ''
    fam = 1 if 'Family-friendly' in c else 0
    acts = activities(c)
    if '/location/' in url:
        continue
    rec = {
        'name': o['n'].strip(),
        't': t,
        'm': split_mediums(o['m']) if t != 'H' else [],
        'u': url.replace('https://atxstudiotour.com/', '').strip('/'),
        'e': '', 'b': '', 'cat': '', 'img': (FT.get(url) or {}).get('img',''),
        'locs': locs,
        'fam': fam,
    }
    b, ex, cat = bio_of(o)
    rec['b'] = b; rec['e'] = ex or re.sub(r'\s*Content.*$', '', (o['e'] or '')).replace('Back to Explore', '').strip(); rec['cat'] = cat
    people.append(rec)
    for lc in locs:
        li = loc_info[lc['n']]
        if t == 'H':
            li['hosts'].append(rec['name'])
        elif lc['host']:
            li['hosts'].append(lc['host'])
        if lc['nav']:
            li['nav'].append(lc['nav'])
        li['acts'].update(acts if t == 'H' else [])
        li['fam'] |= fam
        li['days'] |= lc['days']
        li['hrs'][short_hours(lc['hrs'])] += 1

# Build location records
MED = []
def mid(m):
    if m not in MED:
        MED.append(m)
    return MED.index(m)

locs_out = []
for n, l in sorted(L.items()):
    if 'lat' not in l:
        continue
    li = loc_info.get(n)
    if not li:
        continue
    hc = collections.Counter(h for h in li['hosts'] if h and not re.match(r'^[\d. ]+$', h))
    venue = hc.most_common(1)[0][0] if hc else ''
    others = [h for h, _ in hc.most_common() if h != venue][:3]
    hrs_common = li['hrs'].most_common(1)[0][0] if li['hrs'] else ''
    locs_out.append({
        'n': n, 'lat': l['lat'], 'lng': l['lng'], 'a': (l.get('a') or '').replace(', Austin, TX', ''),
        'v': venue, 'v2': others, 'd': li['days'] or 15, 'h': hrs_common,
        'f': li['fam'], 'x': sorted(li['acts']),
        'nav': (li['nav'][0] if li['nav'] else '')[:140],
    })

ppl_out = []
for p in people:
    ppl_out.append([
        p['name'], p['t'], [mid(m) for m in p['m']],
        [[lc['n'], lc['days'], short_hours(lc['hrs'])] for lc in p['locs']],
        p['e'], p['u'], p['b'], p['img'].replace('https://atxstudiotour.com/wp-content/uploads/',''), p['cat'],
    ])

data = {'M': MED, 'L': locs_out, 'P': ppl_out}
s = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
open('/home/claude/build/data.json', 'w').write(s)
print('bytes', len(s.encode()), 'locs', len(locs_out), 'people', len(ppl_out))
print('mediums', MED)
for l in locs_out[:6]:
    print(l)
print(collections.Counter(len(l['v']) > 0 for l in locs_out))
