# 보물상자 깨기 게임 안내 페이지 생성기.
# data.json = 게임 코드(treasure-box/src)에서 lune로 뽑은 값 (tests/_dump.luau).
# photos.json = 모델 검토 페이지의 표준 사진 목록. 실행: python build.py
import json, math, html

D = json.load(open('data.json', encoding='utf-8'))
P = json.load(open('photos.json', encoding='utf-8'))
META = json.load(open('meta.json', encoding='utf-8'))

G = D['grades']
GN = [g['name'] for g in G]
NAMES = D['items']['names']
SLOTN = D['items']['slotNames']


def esc(s):
    return html.escape(str(s))


def pct(x, digits=None):
    v = x * 100
    if digits is None:
        if v == 0:
            return '0%'
        if v >= 10:
            digits = 0 if abs(v - round(v)) < 1e-9 else 1
        elif v >= 1:
            digits = 0 if abs(v - round(v)) < 1e-9 else (1 if abs(v * 10 - round(v * 10)) < 1e-9 else 2)
        else:
            digits = 2 if abs(v * 100 - round(v * 100)) < 1e-9 else 3
    s = f'{v:.{digits}f}'
    if '.' in s:
        s = s.rstrip('0').rstrip('.')
    return s + '%'


def num(x):
    if isinstance(x, float) and abs(x - round(x)) > 1e-9:
        return f'{x:,.2f}'.rstrip('0').rstrip('.')
    return f'{int(round(x)):,}'


def chip(g):  # g = 1..8
    return f'<span class="g g{g}">{GN[g-1]}</span>'


def photo(key, alt, cls='ph'):
    src = P.get(key)
    if not src:
        return f'<div class="{cls} none">사진 없음</div>'
    return f'<img class="{cls}" src="{src}" alt="{esc(alt)}" loading="lazy">'


def table(head, rows, cls=''):
    h = ''.join(f'<th>{c}</th>' for c in head)
    b = ''.join('<tr>' + ''.join(f'<td>{c}</td>' for c in r) + '</tr>' for r in rows)
    return f'<div class="tw {cls}"><table><thead><tr>{h}</tr></thead><tbody>{b}</tbody></table></div>'


def fig(src, cap, wide=True):
    return f'<figure class="{"wide" if wide else ""}"><img src="{src}" alt="{esc(cap)}" loading="lazy"><figcaption>{cap}</figcaption></figure>'


sections = []


def section(id_, title, body, lead=''):
    sections.append((id_, title))
    lead_html = f'<p class="lead">{lead}</p>' if lead else ''
    return f'<section id="{id_}"><h2>{title}</h2>{lead_html}{body}</section>'


# ---------- hero: the grade staircase ----------
hits = D['field']['hits']
steps = ''
for i, g in enumerate(G, start=1):
    h = 18 + 82 * (math.log10(hits[i-1]) - math.log10(hits[0])) / (math.log10(hits[-1]) - math.log10(hits[0]))
    steps += (f'<div class="step g{i}" style="--h:{h:.1f}%"><span class="sn">{g["name"]}</span>'
              f'<span class="sh">{num(hits[i-1])}타</span></div>')
hero = f'''<header class="hero">
<div class="hero-text">
<h1>보물상자 깨기</h1>
<p>광장에 흩어진 보물상자를 두드려 깨고, 나온 장비로 더 빨리 치고, 더 높은 등급 상자로 올라가는 로블록스 클리커입니다. 아래 수치는 모두 게임 코드에서 그대로 뽑았습니다.</p>
<p class="src">코드 기준: {esc(META["commit"])} · {esc(META["date"])}</p>
</div>
<div class="stairs" aria-label="등급별 상자 타수">{steps}</div>
<p class="stairs-cap">D부터 SSS까지 여덟 등급. 계단 높이는 그 등급 상자를 깨는 데 필요한 타수(로그 눈금)입니다.</p>
</header>'''

body = []

# ---------- 1. flow ----------
flow = '''<ol class="flow">
<li><b>상자 치기</b> — 광장 구역에 놓인 상자를 클릭(폰은 공격 버튼)으로 칩니다. 한 대 = 상자 1칸, 데미지 배수는 없습니다.</li>
<li><b>장비 얻기</b> — 상자가 깨지면 그 등급 근처의 장비 조각 하나와 코인이 나옵니다.</li>
<li><b>입고 강화하기</b> — 7부위를 입어 공격 속도·행운·판매 보너스를 올리고, 코인으로 +10까지 강화합니다.</li>
<li><b>다음 구역으로</b> — 입은 장비의 평균 등급이 오르면 유적·신전·천궁 문이 열리고, 더 높은 등급 상자가 나옵니다.</li>
<li><b>세트와 팻</b> — 같은 세트 7부위를 모으면 그 세트의 팻이 생기고, 다 입으면 세트 오라와 공격 속도 보너스가 붙습니다.</li>
</ol>'''
body.append(section('flow', '한눈에 보기', flow + fig(P['맵/전체 전경/overview'], '광장 전경 — 가운데 광장에서 네 구역으로 갈라집니다')))

# ---------- 2. grades ----------
rows = []
for i, g in enumerate(G, start=1):
    rows.append([chip(i), f'×{g["mult"]}', num(hits[i-1]), num(D['field']['coins'][i-1]),
                 pct(D['field']['weights'][i-1] / 100), pct(D['field']['setShares'][i-1]), pct(D['field']['climb'][i-1])])
grades = table(['등급', '능력치 배수', '상자 타수', '상자 코인', '상자 출현 비중*', '세트 조각 몫', '한 단계 위로 오를 몫'], rows, 'num')
grades += '<p class="note">* 출현 비중은 전체 기준값입니다. 실제로는 구역마다 그 구역의 등급 범위만 잘라 다시 100%로 나눕니다(아래 「필드」). 「세트 조각 몫」은 나온 조각이 신수 세트일 확률, 「오를 몫」은 행운·황금으로 한 등급 위가 나올 때 실제로 적용되는 비율입니다.</p>'
body.append(section('grades', '등급', grades, '모든 장비·상자·팻이 같은 여덟 등급을 씁니다. 색은 게임 화면의 테두리 색 그대로입니다.'))

# ---------- 3. slots ----------
STAT = {
    'handSpeed': ('손 공격 속도', 'speed'), 'petSpeed': ('팻 공격 속도', 'speed'), 'luck': ('행운', 'pct'),
    'sellBonus': ('판매 보너스', 'pct'), 'golden': ('황금 조각', 'pct'), 'bonusPart': ('추가 조각', 'pct'),
    'speed': ('이동 속도', 'walk')}
EXPL = {
    'handSpeed': '손으로 치는 간격이 1/(1+값)로 줄어듭니다.',
    'petSpeed': '팻이 치는 간격이 1/(1+값)로 줄어듭니다.',
    'luck': '조각 등급이 한 단계 아래로 나올 몫을 한 단계 위로 옮깁니다.',
    'sellBonus': '상자 코인과 조각 판매 값이 이만큼 늘어납니다.',
    'golden': '이 확률로 조각이 한 등급 위로 나옵니다(오를 몫 적용).',
    'bonusPart': '이 확률로 조각이 하나 더 나옵니다.',
    'speed': '걷기 속도(기본 16)에 더해집니다. 최대 28.',
}


def fmt(kind, v):
    if kind == 'speed':
        return f'+{num(v*100)}%'
    if kind == 'walk':
        return f'+{num(v)}'
    return pct(v)


caps = D['caps']
rows = []
for s in D['slots']:
    name, kind = STAT[s['stat']]
    cap = caps.get(s['stat'])
    rows.append([f'<b>{s["name"]}</b>', name] + [fmt(kind, s['v0'][g]) for g in (0, 3, 5, 7)]
                + [fmt(kind, s['v10'][7]), pct(cap) if cap else '—', EXPL[s['stat']]])
slots = table(['부위', '능력치', 'D +0', 'A +0', 'S +0', 'SSS +0', 'SSS +10', '상한', '하는 일'],
              rows, 'num first-wide')
slots += f'<p class="note">계산: 팔·갑옷 = 등급별 속도표 × (1 + 0.08 × 강화), 나머지 = 기본값 × 등급 배수 × (1 + 0.08 × 강화). 7부위 상한은 합계 기준이며 팻 스킬 효과는 상한 뒤에 더해집니다.</p>'
rows = []
for i, s in enumerate(D['suit'], start=1):
    rows.append([chip(i)] + [f'{v:.3f}초 · 초당 {1/v:.1f}회' for v in (s['p0'], s['p10'], s['set0'], s['set10'])])
slots += '<h3>같은 등급으로 7부위를 다 입었을 때 손 공격 간격</h3>'
slots += table(['등급', '일반 +0', '일반 +10', '세트 +0', '세트 +10'], rows, 'num')
slots += '<p class="note">기본 간격 0.5초. 세트는 같은 세트 7부위를 입었을 때로, 간격이 「가장 낮은 부위 등급 × 2%」 더 줄어듭니다. 팔 하나만 손 속도에 들어갑니다.</p>'
body.append(section('slots', '장비 부위와 능력치', slots, '부위는 7개: 투구·어깨·갑옷·팔·하의·무릎·부츠. 부위마다 맡은 능력치가 하나씩 있습니다.'))

# ---------- 4. enhance ----------
E = D['enhance']
rows = [[f'+{i}→+{i+1}', pct(r), pct(min(1, r + E['scroll']))] for i, r in enumerate(E['rates'])]
enh = '<div class="two">' + table(['단계', '성공 확률', '주문서 사용'], rows, 'num') + '<div>'
enh += f'<p>실패해도 장비는 깨지거나 내려가지 않고, 다음 시도 확률이 <b>+{pct(E["pity"])}p</b> 오릅니다(성공하면 초기화). 강화 주문서는 한 번에 <b>+{pct(E["scroll"])}p</b>. 강화 한 단계마다 그 장비 능력치 +8%.</p>'
enh += '<p>강화한 장비를 팔면 들인 코인의 <b>절반</b>을 돌려받습니다. 세트 오라도 강화에 따라 커집니다(아래 「세트 효과」).</p></div></div>'
rows = []
for i, c in enumerate(E['cost'], start=1):
    c = [c[str(k)] for k in range(1, 11)] if isinstance(c, dict) else c[:10]
    rows.append([chip(i)] + [num(v) for v in c] + [f'<b>{num(sum(c))}</b>'])
enh += '<h3>단계별 비용 (코인)</h3>'
enh += table(['등급'] + [f'+{k}' for k in range(1, 11)] + ['+10까지 합계'], rows, 'num small')
enh += '<p class="note">비용 = 20 × 1.6^(등급−1) × 1.5^(현재 강화), 반올림.</p>'
enh += fig('img/fx/glow_plus.webp', '강화 단계별 장비 빛 (+1 · +5 · +10)')
body.append(section('enhance', '강화', enh, f'최대 +{E["max"]}. 코인으로 하고, 실패해도 잃는 건 코인뿐입니다.'))

# ---------- 5. sets ----------
SA = D['setAura']
MOTIF = {'dragon': '용 리본', 'claw': '할퀸 자국', 'fire': '불꽃 날개', 'water': '물결', 'judgement': '심판의 빛',
         'winter': '눈·별·사탕지팡이·머리 위 큰 별', 'newyear': '붉은 빛줄기·금화·복주머니·해돋이'}
SETPHOTO = {'set1': '세트/청룡', 'set2': '세트/백호', 'set3': '세트/주작', 'set4': '세트/현무', 'set5': '세트/해태',
            'season_newyear': '세트/새해 붉은 숫양 장수', 'season_childrens': '세트/어린이날 색동 장수',
            'season_chuseok': '세트/추석 달 장수', 'season_halloween': '세트/할로윈 고스트 장수',
            'season_christmas': '세트/겨울 장수'}
PETPHOTO = {'set1': '펫/청룡 팻', 'set2': '펫/백호 팻', 'set3': '펫/주작 팻', 'set4': '펫/현무 팻', 'set5': '펫/해태 팻',
            'season_newyear': '펫/새해 붉은 새끼양', 'season_childrens': '펫/어린이날 까치', 'season_chuseok': '펫/추석 달토끼',
            'season_halloween': '펫/할로윈 잭오랜턴', 'season_christmas': '펫/겨울 빨간코 순록'}
SK = {s['id']: s for s in D['pets']['skills']}
SEASONWIN = {s['key']: s for s in D['products']['seasons']}


def rgbcss(c):
    return f'rgb({c[0]},{c[1]},{c[2]})'


def card(id_, kind_label, extra=''):
    s = SK[id_]
    sa = SA.get(id_)
    sw = f'<span class="sw" style="background:{rgbcss(sa["color"])}"></span>' if sa else ''
    aura = f'{sw}{MOTIF[sa["motif"]]}' if sa else '<span class="dim">세트 오라 아직 없음(등급 오라만)</span>'
    pk = PETPHOTO[id_]
    return f'''<article class="card">
<div class="pics">{photo(SETPHOTO[id_] + "/front", NAMES[id_] + " 세트")}{photo(pk + "/front", NAMES[id_] + " 팻", "ph pet")}</div>
<h3>{esc(NAMES[id_])} <small>{kind_label}</small></h3>
<dl>
<dt>세트 오라</dt><dd>{aura}</dd>
<dt>팻 스킬</dt><dd><b>{esc(s["skill"]["name"])}</b> — {esc(s["desc"][0])}</dd>
{extra}
</dl></article>'''


sets = '<h3>신수 세트 5종</h3><p>필드 상자에서 낮은 확률로 나오는 고유 세트입니다(등급별 「세트 조각 몫」). 7부위를 모두 한 번씩 얻으면 그 신수 팻이 생깁니다. 신수 상자(상점)에서도 나옵니다.</p><div class="cards">'
for sid in D['items']['sets']:
    sets += card(sid, '신수')
sets += '</div>'
sets += '<h3>시즌 세트 5종</h3><p>시즌 기간에만 필드 상자에서 조각이 나옵니다(S등급, 상자 등급 × 0.2%). 시즌 세트 상품(1,499 로벅스)은 그 시즌 세트 7부위를 S등급으로 줍니다. 7부위를 모으면 시즌 팻이 생깁니다.</p><div class="cards">'
for sid in D['items']['seasons']:
    key = sid.replace('season_', '')
    w = SEASONWIN.get(key, {})
    when = f'{w["from"]} ~ {w["to"]}' if w.get('from') else '<span class="dim">기간 미정</span>'
    sets += card(sid, '시즌', f'<dt>기간</dt><dd>{when}</dd>')
sets += '</div>'
NORMPHOTO = {'wood': '나무', 'leather': '가죽', 'bronze': '청동', 'chain': '사슬', 'plate': '판금', 'bone': '뼈'}
sets += '<h3>일반 테마 6종</h3><p>일반 장비는 여섯 테마가 고르게 나옵니다. 능력치는 테마와 상관없이 등급·강화로만 정해지고, 테마는 모양과 도감 칸·호칭에 쓰입니다. 색은 네 가지(나올 비중 70 · 18 · 9 · 3).</p><div class="mini">'
for n in D['items']['normals']:
    sets += f'<figure>{photo("일반템/" + NORMPHOTO[n] + "/front", NAMES[n])}<figcaption>{esc(NAMES[n])}</figcaption></figure>'
sets += '</div>'
body.append(section('sets', '세트', sets, '세트는 신수 5 · 시즌 5, 그 밖의 장비는 일반 테마 6종입니다.'))

# ---------- 6. set effects (aura) ----------
A = D['aura']
FEAT = [('rings', '바닥 고리'), ('wisps', '피어오르는 빛'), ('flames', '불꽃'), ('orbs', '궤도 구슬'),
        ('pillar', '빛기둥'), ('rune', '마법진'), ('tendrils', '빛 줄기'), ('swirl', '몸을 감는 나선'),
        ('arcs', '번개'), ('blades', '등 뒤 수정 칼날'), ('signature', '세트 고유 효과 단계')]
rows = []
for i, a in enumerate(A, start=1):
    r = [chip(i)]
    for k, _ in FEAT:
        v = a[k]
        r.append('●' if v is True else ('' if v in (False, 0) else str(v)))
    r.append(f'{a["ground"]:g}')
    rows.append(r)
fx = '''<ul class="ticks">
<li><b>공격 속도</b>: 같은 세트(신수·시즌) 7부위를 입으면 손 공격 간격이 「가장 낮은 부위 등급 × 2%」 줄어듭니다. SSS면 16%.</li>
<li><b>세트 오라</b>: 등급마다 요소가 하나씩 늘어납니다. 신수와 겨울·새해 세트는 오라 색 전체가 세트 색으로 바뀌고, 고유 효과(아래 표 마지막 열)가 C·A·S·SSS에서 한 단계씩 커집니다.</li>
<li><b>강화와 오라</b>: +10이 표의 모습입니다. +0은 「등급 절반」의 요소만 켜지고(SSS → A 수준), 더 작고 흐립니다. 색과 이름표는 실제 등급 그대로.</li>
<li><b>세트 팻</b>: 7부위를 모으면(입지 않아도) 생깁니다. 다 입으면 팻도 입은 세트 색을 따라갑니다.</li>
</ul>'''
fx += table(['등급'] + [n for _, n in FEAT] + ['바닥 빛 지름'], rows, 'num small center')
fx += fig('img/fx/aura_plus.webp', 'SSS 청룡: 강화 +0 · +3 · +6 · +10 오라')
fx += fig('img/fx/circles.webp', '신수 세트 바닥 문양 — 청룡 · 백호 · 주작 · 현무 · 해태')
fx += '<div class="trio">' + fig('img/fx/tier1.webp', '낮은 등급 오라', False) + fig('img/fx/tier4.webp', '중간 등급 오라', False) + fig('img/fx/tier6.webp', '높은 등급 오라', False) + '</div>'
body.append(section('setfx', '세트 효과와 오라', fx))

# ---------- 7. pets ----------
PD = D['pets']
pets = f'''<ul class="ticks">
<li><b>팻 칸</b>: 무료 {PD["freeSlots"]}칸, 구독으로 2칸·3칸이 열립니다. 칸이 닫히면 그 칸의 팻은 쉬고 스킬도 안 나갑니다.</li>
<li><b>치는 속도</b>: 팻은 1초에 한 번 치고, 입은 갑옷의 팻 공격 속도만큼 빨라집니다. 단 손보다 빨라지지는 않게 손 속도의 90%가 상한입니다.</li>
<li><b>스킬</b>: 신수·시즌 팻만 있습니다. 모든 스킬은 「같은 시간에 더 많이 치게」 할 뿐, 한 대의 데미지는 늘리지 않습니다. 같은 종류 스킬은 동시에 하나만 켜집니다.</li>
</ul>'''
KIND = {'combo': '연타', 'clone': '분신', 'frenzy': '손 폭주', 'petRush': '팻 폭주', 'burst': '한 번에 내리꽂기'}
rows = []
for s in PD['skills']:
    sk = s['skill']
    if s['id'].startswith('set'):
        ch = ' · '.join(f'{GN[g]} {pct(s["chance"][g])}' for g in (0, 3, 5, 7))
    else:
        ch = f'고정 {pct(s["chance"][0])}'
    rows.append([f'<b>{esc(s["design"])}</b>', esc(sk['name']), KIND[sk['kind']], esc(s['desc'][0]), ch])
pets += '<h3>신수·시즌 팻 스킬</h3>' + table(['팻', '스킬', '종류', '발동 (D 기준)', '발동 확률 (D · A · S · SSS)'], rows, 'first-wide')
pets += '<p class="note">신수 팻은 각성 등급의 배수(아래)가 발동 확률에 곱해집니다. 상한은 연타 60%, 나머지 30%. 시즌 팻은 각성이 없어 고정입니다.</p>'
pets += '<p class="note">효과: 연타 = 그 클릭에 추가 타. 분신 = 지속시간 동안 분신이 손 속도로 같이 칩니다. 손 폭주 = 손 공격 속도 배수. 팻 폭주 = 팻 공격 속도 배수. 내리꽂기 = 「손으로 N초 칠 만큼」의 타수가 한 번에 들어갑니다.</p>'
CH = D['field']['characterHeight']
rows = [[chip(i), f'×{m}', f'{PD["heightRatio"][i-1]:g}배 <span class="dim">({CH * PD["heightRatio"][i-1]:.1f}스터드)</span>'] for i, m in enumerate(PD['awakenMult'], start=1)]
pets += '<div class="two"><div><h3>신수 팻 각성</h3>' + table(['각성', '스킬 확률 배수', '키 (캐릭터 = 1배)'], rows, 'num')
pets += '</div><div><p>신수 팻은 처음 생길 때 <b>D</b>에서 시작합니다. 한 단계 올리려면 지금보다 한 등급 이상 높은 그 세트 조각을 <b>7부위 모두 다시</b> 얻어야 합니다(자동 판매된 조각도 셉니다). 한 번에 한 단계씩.</p>'
pets += fig('img/fx/pets_lineup.webp', '신수 팻 다섯', False) + '</div></div>'
pets += '<p class="new">11-11 조정: 팻 키를 모두 두 배로 키웠습니다(전엔 D가 캐릭터의 절반, SSS가 2배).</p>' + fig('img/fx/pets_big.webp', '두 배로 커진 팻')
rows = []
for b in PD['boxPets']:
    rows.append([photo('펫/' + b['name'] + '/front', b['name'], 'ph tiny'), f'<b>{esc(b["name"])}</b>', str(b['weight'])])
soul = ' → '.join(f'{GN[i]}→{GN[i+1]} {c}개' for i, c in enumerate(PD['soulCost']))
pc = D['field']['petChance']
pets += '<h3>상자 팻 8종</h3>'
pets += f'<p>필드 상자를 깰 때 <b>상자 등급 × 0.2%</b> 확률로 나옵니다(D {pct(pc[0])} ~ SSS {pct(pc[7])}). 아직 상자 팻이 하나도 없으면 <b>{D["field"]["firstPetBoost"]}배</b>(첫 팻 맛보기). 같은 팻이 또 나오면 그 팻의 영혼 1개가 되고, 영혼으로 등급을 올립니다: {soul}. 상자 팻 등급은 키와 빛만 바꾸고 스킬은 없습니다. 키는 신수 팻과 같은 표를 따릅니다(D = 캐릭터의 {PD["heightRatio"][0]:g}배 → SSS = 캐릭터의 {PD["heightRatio"][7]:g}배).</p>'
pets += table(['', '이름', '팻 상자 비중'], rows, 'pets')
pets += '<p class="note">팻 상자(상점 149 로벅스)는 상자 팻 8종만 나오고, 이미 가진 팻은 빠집니다. 8종을 다 가졌으면 대신 강화 주문서 15장.</p>'
pets += '<p class="new">팻 자리: 따라다닐 때는 오른쪽 뒤 · 왼쪽 뒤 · 바로 뒤, 상자를 칠 때는 캐릭터 반대쪽(상자 양옆과 뒤)에 섭니다. 팻마다 실제 몸 크기를 재서 캐릭터 · 다른 팻 · 상자와 겹치지 않게 떨어지고, 각성으로 커지면 그만큼 더 떨어집니다.</p>'
RD = PD['ride']
MV = {'glide': '활공', 'swim': '물 위 달리기'}
rows = []
for i, m in enumerate(RD['mult'], start=1):
    rows.append([chip(i), f'×{m:g}', f'{min(RD["baseWalk"] * m, RD["max"]):g}', f'{min(RD["maxWalk"] * m, RD["max"]):g}', f'{min(min(RD["baseWalk"] * m, RD["max"]) * RD["glideBoost"], RD["max"]):g}'])
ride = '<h3>팻 타기</h3>'
ride += f'''<ul class="ticks">
<li><b>타는 법</b>: 1번 칸에 팻이 있으면 <b>🐾 타기</b> 버튼(PC는 R 키)이 보입니다. 타기를 켜 두면 상자를 치는 동안만 저절로 내렸다가, 다 치면 다시 탑니다.</li>
<li><b>버튼 자리</b>: 폰에서는 공격 버튼 바로 위에 같은 크기로 붙습니다(위에 자리가 없으면 공격 버튼 왼쪽). 점프·공격·메뉴 버튼과 겹치지 않습니다. PC는 화면 오른쪽 가운데.</li>
<li><b>빠르기</b>: 걷는 속도 × 팻 등급 배수, 최대 {RD["max"]:g}. 시즌 팻은 등급이 없어 {GN[RD["seasonGrade"]-1]} 팻처럼 탑니다.</li>
<li><b>탈 때 크기</b>: 작은 팻도 타는 동안은 최소 캐릭터 키의 {pct(RD["minRatio"])}까지 커집니다. 큰 팻은 제 크기 그대로.</li>
</ul>'''
ride += '<div class="two">' + table(['팻 등급', '배수', '걷기 16일 때', '걷기 최대 28일 때', '활공 (걷기 16)'], rows, 'num')
moves = ' · '.join(f'<b>{esc(x["name"])}</b>' for x in RD['moves'] if x['move'] == 'glide')
swims = ' · '.join(f'<b>{esc(x["name"])}</b>' for x in RD['moves'] if x['move'] == 'swim')
ride += f'''<ul class="ticks">
<li><b>활공</b> ({moves}): 높은 곳에서 떨어지면 1초에 {RD["glideFall"]:g}스터드씩만 천천히 내려가고, 앞으로는 타는 속도의 {RD["glideBoost"]:g}배로 날아갑니다(최대 {RD["max"]:g}).</li>
<li><b>물 위 달리기</b> ({swims}): 강과 협곡 개울 위를 가라앉지 않고 달립니다. 물보라가 튑니다. 물에 빠진 채로 타면 물 위로 떠오릅니다.</li>
<li>둘 다 길을 막는 것은 아닙니다. 강에는 다리가, 고개마다 길이 있습니다. 더 빨리, 더 자유롭게 다니는 길일 뿐입니다.</li>
</ul></div>'''
ride += '<div class="two">' + fig('img/fx/ride_glide.webp', '주작을 타고 활공', False) + fig('img/fx/ride_swim.webp', '현무를 타고 물 위 달리기', False) + '</div>'
pets += ride
body.append(section('pets', '팻', pets))

# ---------- 8. field ----------
F = D['field']
rows = []
for z in F['zones']:
    lo = f'평균 {GN[z["minGrade"]-1]} 이상' if z['minGrade'] else '처음부터'
    hi = f' · {GN[z["maxGrade"]-1]} 미만' if z.get('maxGrade') else ''
    enter = lo + hi
    boxes = '<br>'.join(f'{chip(b["grade"])} {esc(b["name"])} <span class="dim">{pct(b["share"], 1 if b["share"]>=0.1 else 2)}</span>' for b in z['boxes'])
    rows.append([f'<b>{esc(z["name"])}</b>', enter, boxes, esc(z['boss']), photo('상자/Z' + str(F['zones'].index(z)+1) + '/front', z['name'] + ' 상자', 'ph box')])
field = table(['구역', '들어가는 조건', '나오는 상자 (구역 안 비중)', '보스 상자', '상자 모습'], rows, 'zones')
field += '<p class="note">평균 = 7부위 등급(D=1 … SSS=8)의 평균, 빈 부위는 0. 아래 구역에는 상한이 있어서 장비가 좋아지면 위 구역으로 올라가야 합니다(같은 자리에서 낮은 상자만 쓸어 담지 못하게). 광장(가운데)에 있으면 열린 구역 중 가장 높은 곳으로 셉니다.</p>'
field += '<h3>상자에서 나오는 것</h3>'
rows = []
for i in range(8):
    rows.append([chip(i+1), num(F['coins'][i]), pct(F['scrollChance'][i]), pct(F['petChance'][i]), pct(F['seasonChance'][i])])
field += '<div class="two">' + table(['상자', '코인', '주문서', '상자 팻', '시즌 조각'], rows, 'num')
field += f'''<ul class="ticks">
<li><b>장비 조각 1개</b>: 상자와 같은 등급 60%, 한 단계 아래 30%, 한 단계 위 10%. 행운은 「아래 30%」를 위로 옮기고, 위로 가는 몫에는 등급별 「오를 몫」이 곱해집니다.</li>
<li><b>황금</b>: 확률로 조각이 한 등급 더 위(오를 몫 적용).</li>
<li><b>추가 조각</b>: 확률로 조각이 하나 더.</li>
<li><b>코인</b> = 10 × 2^(등급−1) × (1 + 판매 보너스 + 친구 보너스), 반올림.</li>
<li><b>상자 수</b>: 구역마다 최소 {F["zoneMin"]}개, 그 구역 사람 1명당 +{F["perPlayer"]}개, 최대 {F["zoneMax"]}개. 깨면 {F["respawn"]}초 뒤 새로 놓입니다.</li>
<li><b>타격 거리</b>: 상자 가장자리에서 {F["strike"]}스터드 안이면 그 자리에서 치고, 더 멀면 상자 앞까지 걸어가서 칩니다(서버는 지연을 감안해 {F["reach"]}스터드까지 받아 줌). 거리를 늘리는 능력치는 없습니다.</li>
<li><b>상자 크기</b>: 등급이 오를수록 커집니다 — {' · '.join(f'{GN[i]} {w:g}' for i, w in enumerate(F['boxSizes']))}스터드(D의 8배까지).</li>
<li><b>찜</b>: 먼저 친 사람이 그 상자를 가집니다. {F["claimIdle"]}초 동안 안 치면 풀립니다.</li>
</ul></div>'''
field += '<h3>보스 상자</h3>'
bh = ' · '.join(f'{z["name"]} {num(F["bossHits"][i])}' for i, z in enumerate(F['zones']))
field += f'<p>각 구역에 <b>{F["bossEvery"]//60}분마다</b> 나타나 <b>{F["bossTime"]//60}분</b> 안에 깨야 합니다. 필요 타수 = 기준 × (그 구역 사람 수 + 0.5). 기준: {bh}. 깨지면 친 몫이 {pct(F["bossShare"])} 이상인 모두가 보상 1번, 상위 {F["bossTop"]}명은 2번. 보상 한 번 = 그 구역 상자 두 개를 굴려 좋은 쪽.</p>'
field += f'<p class="new">보스 상자는 폭 <b>{F["bossSize"]}스터드</b>(SSS 상자의 {F["bossSize"]/F["boxSizes"][7]:.1f}배)이고, 그 자리에 <b>하늘까지 {F["pillarHeight"]}스터드 빛기둥</b>(구역 보스 등급 색)이 서서 맵 어디서든 보입니다. 보스가 내려앉는 자리에 있던 빈 상자는 치워지고 다른 곳에 다시 놓입니다.</p>'
field += '<div class="trio">' + fig('img/fx/break1.webp', '상자가 깨질 때 0.15초 — 뚜껑이 열림', False) + fig('img/fx/break2.webp', '0.45초 — 조각이 쏟아지고 빛기둥', False) + fig('img/fx/break4.webp', '1.15초 — 조각이 몸으로 빨려 들어감', False) + '</div>'
field += '<div class="trio">' + fig('img/fx/move1.webp', '타격 동작: 정권', False) + fig('img/fx/move3.webp', '앞차기', False) + fig('img/fx/move4.webp', '세트 착용 돌려차기', False) + '</div>'
field += fig(P['상자/전체/front'], '구역별 상자 전체 — 등급이 오를수록 크고 화려해집니다')
field += '<p class="new">11-11: 들판에 나무·바위·통나무를 촘촘히 세우고(숲은 더 빽빽하게), 바닥에 고사리·풀·버섯·나뭇가지를 깔았습니다. 길과 마을, 상자 자리는 비워 둡니다. 천궁(설산)은 눈 소나무만.</p>' + fig('img/fx/field_forest.webp', '초원 숲 — 나무와 바닥 풀')
body.append(section('field', '필드: 구역·상자·보스', field, f'광장 한 서버 최대 {F["maxPlayers"]}명. 가운데 광장에서 네 구역으로 갈라집니다.'))

# ---------- 9. rewards ----------
rw = '<h3>매일 출석</h3>'
rows = [[f'{i}일째', f'{d["boxes"]}상자' if d['boxes'] else '—', f'{d["scrolls"]}장' if d['scrolls'] else '—'] for i, d in enumerate(D['daily'], start=1)]
rw += '<div class="two">' + table(['연속 출석', '코인', '강화 주문서'], rows, 'num') + '<p>한국 시간 하루 첫 접속에 받습니다. 하루 빠지면 1일째부터, 7일째 다음은 다시 1일째(연속 일수는 계속 셉니다). 「n상자」 = 내가 갈 수 있는 가장 높은 구역의 가장 낮은 상자 n개 값의 코인이라, 단계가 올라도 값어치가 유지됩니다.</p></div>'
M = D['missions']
rw += '<h3>일일 미션</h3>'
rows = [[esc(m['text'] % m['goal'])] for m in M['pool']]
tr = ' · '.join(f'{i}번째 날: <b>{ {"auto": "자동 공격", "petSlot2": "팻 칸 2"}[t["kind"]] } {t["hours"]//24}일 체험</b>' for i, t in enumerate(D['trials'], start=1))
rw += '<div class="two">' + table(['미션 후보 (하루 3개)'], rows) + f'<div><p>매일 여섯 중 세 개(모두 같은 세 개). 하나 끝낼 때마다 {M["boxes"]}상자 값의 코인, 세 개를 다 끝내면 주문서 +{M["allScrolls"]}.</p><p class="new"><b>구독 맛보기</b> — 세 개를 다 끝낸 날 차례로: {tr}. 계정당 한 번씩이고, 체험 중에는 구독과 똑같이 작동합니다(오프라인 정산은 실제 구독만).</p></div></div>'
rw += '<h3>도감 수집 보상</h3>'
rows = [[f'{num(m["cells"])}칸', f'{m["boxes"]}상자', f'{m["scrolls"]}장'] for m in D['codex']]
rw += '<div class="two">' + table(['도감', '코인', '주문서'], rows, 'num') + '<p>도감 칸 = 테마 × 부위 × 등급. 전체 651칸. 시즌 세트는 S등급 칸만 셉니다. 팔거나 자동 판매해도 한번 채운 칸은 사라지지 않습니다.</p></div>'
rw += '<h3>호칭</h3><p>캐릭터 머리 위에 「호칭의 이름」으로 붙습니다. 직접 골라 쓰고, ★표시는 얻는 순간 서버 전체에 알려집니다.</p>'
rows = [[f'{"★ " if t.get("brag") else ""}<b>{esc(t["name"])}</b>', esc(t['hint'])] for t in D['titles']]
rw += table(['호칭', '얻는 법'], rows, 'cols2')
fr = D['friends']
rw += f'<h3>친구 보너스</h3><p>같은 서버의 로블록스 친구 1명마다 상자 코인 +{pct(fr["per"])}, 최대 {fr["max"]}명(+{pct(fr["per"]*fr["max"])}).</p>'
body.append(section('rewards', '출석·미션·도감·호칭', rw))

# ---------- 10. shop ----------
PR = D['products']['prices']
GO = D['gacha']['odds']


def odds(key):
    return ' · '.join(f'{chip(g)} {pct(w/100)}' for g, w in GO[key])


rows = [
    ['자동 공격', f'{PR["auto"]} / 월', f'차지한 상자를 손 공격보다 {D["stats"]["baseInterval"] / D["stats"]["baseAuto"]:.1f}배 빠르게 자동으로 칩니다. 꺼져 있어도(접속 안 해도) 최대 12시간까지 정산.'],
    ['팻 칸 2', f'{PR["petSlot2"]} / 월', '팻을 2마리 데리고 다닙니다.'],
    ['팻 칸 3', f'{PR["petSlot3"]} / 월', '3마리.'],
]
shop = '<h3>구독</h3>' + table(['구독', '로벅스', '하는 일'], rows, 'first-wide')
rows = [
    ['장비 스타터팩', num(PR['starterA']), f'일반 테마 하나를 골라 7부위 A등급 + 주문서 {D["products"]["starterScrolls"]}장 (한 번만)'],
    ['주문서 5장', num(PR['scroll5']), ''], ['주문서 15장', num(PR['scroll15']), ''],
    ['시즌 세트', num(PR['season']), '그 시즌 세트 7부위 S등급 (시즌 중에만)'],
]
shop += '<h3>상품</h3>' + table(['상품', '로벅스', '내용'], rows, 'first-wide')
rows = [
    ['일반 A 상자', num(PR['boxA']), '처음부터', odds('boxA')],
    ['일반 S 상자', num(PR['boxS']), '유적 입장 조건을 한 번 넘긴 뒤', odds('boxS')],
    ['신수 상자', f'{num(PR["beast1"])} · 10+1 {num(PR["beast11"])}', '신전 입장 조건을 한 번 넘긴 뒤', odds('beast') + f'<br><span class="dim">천장: {D["gacha"]["pity"]}번 연속 A 미만이면 다음은 A 이상</span>'],
    ['팻 상자', num(PR['petBox']), '처음부터', '상자 팻 8종 (위 비중, 가진 팻 제외)'],
]
shop += '<h3>뽑기 상자</h3>' + table(['상자', '로벅스', '열리는 때', '등급 확률'], rows, 'first-wide')
shop += '<p class="note">일반 상자는 일반 테마 6종, 신수 상자는 신수 세트 5종에서 부위·테마가 고르게 나옵니다. 로블록스 정책상 유료 뽑기가 막힌 지역에서는 뽑기·주문서 상품이 보이지 않습니다.</p>'
shop += '<div class="mini">' + ''.join(f'<figure>{photo("상자/" + n + "/front", n)}<figcaption>{n}</figcaption></figure>' for n in ('상점 일반 A', '상점 일반 S', '상점 신수', '상점 팻')) + '</div>'
body.append(section('shop', '상점', shop, '게임은 무료이고, 구독·상품은 속도와 편의를 삽니다. 가격 단위는 로벅스.'))

# ---------- 11. balance ----------
B = META['balance']
rows = []
for k, label in (('boxpet', '첫 상자 팻'), ('A', '첫 A 장비'), ('S', '첫 S'), ('SS', '첫 SS'), ('SSS', '첫 SSS'), ('pet', '첫 신수 팻'), ('setS', '신수 세트 S 7부위'), ('setSSS', '신수 세트 SSS 7부위')):
    f, p = B['free'][k], B['paid'][k]
    def hm(h):
        m = round(h * 60)
        return f'{m}분' if m < 60 else (f'{m//60}시간 {m%60}분' if m % 60 else f'{m//60}시간')
    rows.append([label, hm(f), hm(p), f'{p/f:.2f}배'])
bal = table(['도달 목표', '무료 (팻 1칸)', '구독 (자동 공격 + 팻 3칸)', '구독 / 무료'], rows, 'num first-wide')
bal += f'<p class="note">시뮬레이션: 실제 보상 코드를 그대로 돌린 접속 시간 기준 중앙값({B["seeds"]}회). 오프라인 정산은 빼고 셈. 기준선 — 무료: 첫 A 3~8분, 첫 S 2.8~3.8시간, 신수 팻 8.7~11.8시간, SSS 21.8~29.6시간. 구독: 무료의 0.4~0.6배(약 절반).</p>'
bal += '<p class="new">11-11 조정: 구독 도달시간은 그대로 두고 무료를 약 2배 느리게 했습니다(상자 타수 ×1.55). 자동 공격은 손보다 1.4배 빠르게 바뀌었습니다(전엔 손의 절반 속도).</p>'
body.append(section('balance', '밸런스 시험 결과', bal, f'{esc(META["date"])} 출시 전 재시험. 전체 시험 {META["specs"]}개 통과.'))

# ---------- page ----------
toc = ''.join(f'<li><a href="#{i}">{t}</a></li>' for i, t in sections)
page = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>보물상자 깨기 안내</title>
<meta name="description" content="보물상자 깨기 — 등급, 장비, 세트, 팻, 필드, 상점 수치 안내">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
</head>
<body>
{hero}
<div class="layout">
<nav class="toc" aria-label="목차"><details open><summary>목차</summary><ol>{toc}</ol></details></nav>
<main>{''.join(body)}
<footer><p>수치는 게임 코드에서 자동으로 뽑아 만든 페이지입니다(data.json). 사진: 모델 검토 페이지 표준 사진과 Studio 화면.</p></footer>
</main>
</div>
</body>
</html>
'''
open('index.html', 'w', encoding='utf-8', newline='\n').write(page)
print('ok', len(page))
