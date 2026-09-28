# -*- coding: utf-8 -*-
"""Generator strony Kancelarii KJK – wersja 9 z panelem edycji treści (Decap CMS).

Teksty są w plikach tresci/*.json – zmienia je Katarzyna w panelu https://<adres-strony>/admin/
(logowanie: DecapBridge). Każda zmiana zapisana w panelu trafia do repozytorium, a Netlify buduje stronę od nowa:
    python3 narzedzia/build.py public        (polecenie z netlify.toml; wynik w folderze public/)
Układ, kolory, menu, ikony, kolejność i adresy specjalizacji zostają w tym pliku i w strona/css/style.css.

W polach tekstowych: *słowo* = kursywa, **słowo** = pogrubienie; w polach z akapitami – każdy wiersz to osobny akapit.
Twarde spacje po jednoliterowych spójnikach i przed półpauzą dokłada funkcja typo() – nie trzeba ich wpisywać.

Kierunek: jak dobrze złożona publikacja – wyrazisty portret, świadoma typografia, uporządkowane kolumny, czytelne odstępy.
Paleta: głęboki granat #1B2540 (tekst, przycisk, stopka), amarant #A8255B (tylko detale i stany), jasne tło #FAF8F5.
Jeden motyw: znaczniki kadru – cienkie narożniki w kolorze amarantu („szczegół w kadrze” – od zdania Katarzyny
„Problem najczęściej tkwi w szczególe”): przy portrecie, przy nagłówkach sekcji, przy ikonie wskazanej specjalizacji
i przy ramce „Warto wiedzieć”; w tym samym kadrze stoi ilustracja rozmowy (Hanna Jurewicz) w sekcji specjalizacji."""
import json, os, sys, datetime, re, shutil, html as H

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TRESCI = os.path.join(ROOT, 'tresci')        # teksty edytowane w panelu
STATIC = os.path.join(ROOT, 'strona')        # css, js, obrazy, fonty, panel /admin – kopiowane bez zmian
sys.path.insert(0, HERE)
from ikony import symbols as icon_symbols, ICONS
try:
    import markdown as MD                     # treść artykułów i polityki prywatności (requirements.txt)
except ImportError:
    MD = None

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'public')
shutil.copytree(STATIC, OUT, dirs_exist_ok=True)

def load(rel):
    return json.load(open(os.path.join(TRESCI, rel), encoding='utf-8'))

def fmt(s):
    """Tekst z panelu → HTML: znaki specjalne zabezpieczone, *kursywa*, **pogrubienie**."""
    s = H.escape((s or '').strip(), quote=True)
    s = re.sub(r'\*\*([^*\n]+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'\*([^*\n]+?)\*', r'<em>\1</em>', s)
    return s

def paras(s):
    """Pole z akapitami: każdy niepusty wiersz to osobny akapit."""
    return [fmt(x) for x in (s or '').splitlines() if x.strip()]

def md_html(text):
    """Markdown z panelu (artykuły, polityka prywatności) → HTML w stylu strony."""
    if not (text or '').strip():
        return ''
    if MD is None:
        raise SystemExit('Brak modułu markdown – zainstaluj: pip install -r requirements.txt')
    h = MD.markdown(text, extensions=['sane_lists'], output_format='html')
    h = re.sub(r'<h1(\s|>)', r'<h2\1', h).replace('</h1>', '</h2>')          # jeden H1 na stronie – w nagłówku
    h = re.sub(r'<h[456](\s|>)', r'<h3\1', h)
    h = re.sub(r'</h[456]>', '</h3>', h)
    return re.sub(r'<h([23])>', r'<h\1 class="block-h">', h)

USTAWIENIA = load('ustawienia.json')
STRONA_GLOWNA = load('strona-glowna.json')
LOGO = json.load(open(os.path.join(HERE, 'logo-kjk-nowe.json')))   # obrys logo (logo-kjk-zrodlo.jpg)
LOGO_VB = f'0 0 {LOGO["w"]} {LOGO["h"]}'

# Wysyłka formularza.
#   ''         – brak zatwierdzonej usługi: formularz widać, ale jest nieaktywny, a informacja o tym stoi NAD polami;
#   'netlify'  – Netlify Forms (w panelu Netlify: Forms → włączyć wykrywanie formularzy, ustawić powiadomienia e-mail);
#   adres URL  – POST do usługi (np. https://formspree.io/f/XXXX).
# Strona nigdy nie pokazuje potwierdzenia, jeśli usługa nie przyjęła wiadomości.
FORM_PROVIDER = os.environ.get('KJK_FORM_PROVIDER', '')

# Dane kontaktowe NOWEJ kancelarii – tylko potwierdzone przez Katarzynę (nie przenosić danych SZW Legal).
# Puste pole = na stronie publicznej informacja „zostaną podane”, w podglądzie redakcyjnym – miejsce na dane.
CONTACT = dict(phone=fmt(USTAWIENIA.get('telefon')), email=fmt(USTAWIENIA.get('email')), address=fmt(USTAWIENIA.get('adres')))

# ================================================================ treści
# Nazwy i kolejność – jak w notatce Katarzyny („Specjalizacje KJK”). Opisy „short” były publiczne w wersji 5.
# Rozwinięcia (when / help / prepare / note) to propozycje do akceptacji Katarzyny – w podglądzie redakcyjnym oznaczone.
# Kolejność, adresy, ikony i grupy – tutaj; teksty – w tresci/specjalizacje/<adres>.json.
SPEC_ORDER = ['rozwody', 'alimenty', 'spadki', 'opiniowanie-umow', 'windykacja', 'obsluga-firm', 'upadlosc-wierzyciele', 'komunikacja-elektroniczna']
def spec_from_file(slug):
    j = load(f'specjalizacje/{slug}.json')
    lst = lambda xs: [fmt(x) for x in (xs or []) if (x or '').strip()]
    return dict(slug=slug, name=fmt(j.get('nazwa')), short=fmt(j.get('krotki_opis')), lead=fmt(j.get('wstep')),
                when=lst(j.get('kiedy')), help=lst(j.get('pomoc')), prepare=lst(j.get('przygotuj')), note=fmt(j.get('warto_wiedziec')))
SPECS = [spec_from_file(x) for x in SPEC_ORDER]
SPEC = {s['slug']: s for s in SPECS}
def plain(s): return re.sub(r'<[^>]+>', '', s).replace('&nbsp;', ' ').replace('\u00a0', ' ')
# Dwie grupy – kolejność Katarzyny zachowana (pierwsze cztery i ostatnie cztery).
GROUPS = [('Rodzina, spadki i&nbsp;umowy', ['rozwody', 'alimenty', 'spadki', 'opiniowanie-umow']),
          ('Należności i&nbsp;firmy', ['windykacja', 'obsluga-firm', 'upadlosc-wierzyciele', 'komunikacja-elektroniczna'])]
def spec_url(slug): return f'specjalizacje/{slug}.html'

# Droga od pierwszego kontaktu – propozycja do akceptacji.
PATH = [(fmt(x.get('tytul')), fmt(x.get('opis'))) for x in STRONA_GLOWNA.get('wspolpraca_kroki', [])]

# Zdanie Katarzyny na pierwszym ekranie – jej brzmienie bez zmian (wersja 9, na prośbę zamawiającej).
# Otwierający cudzysłów wysunięty na margines, żeby tekst trzymał lewą krawędź kolumny.
QUOTE = '<span class="q-open">„</span>' + fmt(STRONA_GLOWNA.get('cytat')) + '”'

# Główne zdanie pierwszego ekranu – propozycje (wybrana: pierwsza).
H1_OPTIONS = [('„Problem najczęściej tkwi w&nbsp;<em>szczególe</em>, który trudno będzie ci dostrzec bez wsparcia profesjonalnego i&nbsp;zaangażowanego prawnika.”',
               'Wybrana w&nbsp;wersji 9 – na prośbę zamawiającej: słowa Katarzyny bez zmian, jako główne zdanie pierwszego ekranu. Nad nim nagłówek H1: imię, nazwisko i&nbsp;zawód; pod nim jedno zdanie o&nbsp;tym, komu i&nbsp;w&nbsp;czym pomagam.'),
              ('Pomoc prawna, w&nbsp;której liczy się <em>szczegół</em>.', 'Wersja 6. Wprowadza w&nbsp;pomoc prawną i&nbsp;w&nbsp;sześciu słowach niesie myśl Katarzyny („Problem najczęściej tkwi w&nbsp;szczególe”) – bez obietnicy wyniku i&nbsp;bez mówienia klientowi, że sam sobie nie poradzi.'),
              ('Każdą sprawę zaczynam od szczegółów.', 'Osobista, w&nbsp;pierwszej osobie, ale nie mówi, że chodzi o&nbsp;pomoc prawną – to musiałby dopowiedzieć tekst pod spodem.'),
              ('Sprawy rodzinne, spadkowe i&nbsp;firmowe – prowadzone starannie.', 'Najbardziej opisowa, ale dłuższa, a&nbsp;„starannie” to deklaracja, którą trudno odróżnić od innych kancelarii.')]

CATS = [dict(slug='rodzina', name='Rodzina'), dict(slug='spadki', name='Spadki'), dict(slug='umowy', name='Umowy'),
        dict(slug='naleznosci', name='Należności i upadłość'), dict(slug='firma', name='Firma'), dict(slug='komunikacja', name='Komunikacja elektroniczna')]
CAT = {c['slug']: c for c in CATS}
# Artykuły z panelu (tresci/blog/<adres>.json) – tylko teksty napisane lub zatwierdzone przez Katarzynę; szkice pomijane.
def iso_day(v):
    v = str(v or '')[:10]
    try:
        datetime.date.fromisoformat(v); return v
    except ValueError:
        return ''
def load_articles():
    out, d = [], os.path.join(TRESCI, 'blog')
    for fn in sorted(os.listdir(d)) if os.path.isdir(d) else []:
        if not fn.endswith('.json'):
            continue
        j = json.load(open(os.path.join(d, fn), encoding='utf-8'))
        slug = re.sub(r'[^a-z0-9-]+', '-', fn[:-5].lower()).strip('-')
        if j.get('szkic') or not slug or not (j.get('tytul') or '').strip() or not iso_day(j.get('data')):
            continue
        out.append(dict(slug=slug, cat=j.get('kategoria') if j.get('kategoria') in CAT else 'rodzina',
                        service=j.get('specjalizacja') if j.get('specjalizacja') in SPEC_ORDER else SPEC_ORDER[0],
                        title=fmt(j['tytul']), lead=fmt(j.get('wstep')), published=iso_day(j['data']),
                        updated=iso_day(j.get('aktualizacja')) or None, body=md_html(j.get('tresc'))))
    return out
ARTICLES = load_articles()
BLOG_LIVE = bool(ARTICLES)
TOPICS = [('rodzina', 'rozwody', 'Rozwód krok po kroku: jak wygląda postępowanie'), ('naleznosci', 'windykacja', 'Wezwanie do zapłaty: co powinno zawierać'),
          ('spadki', 'spadki', 'Przyjęcie czy odrzucenie spadku – ile jest czasu na decyzję'), ('umowy', 'opiniowanie-umow', 'Na co zwrócić uwagę przed podpisaniem umowy')]
MONTHS = ['stycznia', 'lutego', 'marca', 'kwietnia', 'maja', 'czerwca', 'lipca', 'sierpnia', 'września', 'października', 'listopada', 'grudnia']
def pl_date(iso):
    d = datetime.date.fromisoformat(iso); return f'{d.day} {MONTHS[d.month-1]} {d.year}'

SOCIAL = {
 'instagram': ('Instagram', '<rect x="3" y="3" width="18" height="18" rx="5.2" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="12" cy="12" r="4.1" fill="none" stroke="currentColor" stroke-width="1.8"/><circle cx="17.4" cy="6.6" r="1.2" fill="currentColor"/>'),
 'youtube': ('YouTube', '<path fill="currentColor" d="M21.6 7.2a2.5 2.5 0 0 0-1.8-1.8C18.2 5 12 5 12 5s-6.2 0-7.8.4a2.5 2.5 0 0 0-1.8 1.8C2 8.8 2 12 2 12s0 3.2.4 4.8a2.5 2.5 0 0 0 1.8 1.8C5.8 19 12 19 12 19s6.2 0 7.8-.4a2.5 2.5 0 0 0 1.8-1.8c.4-1.6.4-4.8.4-4.8s0-3.2-.4-4.8zM10 15V9l5.2 3z"/>'),
 'facebook': ('Facebook', '<path fill="currentColor" d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.8 1.4-3.8 3.9v2.3H8v3h2.5V21z"/>'),
 'linkedin': ('LinkedIn', '<path fill="currentColor" d="M5.3 8.8h3V19h-3zM6.8 4a1.7 1.7 0 1 1 0 3.5 1.7 1.7 0 0 1 0-3.5zM10.3 8.8h2.9v1.4c.4-.8 1.4-1.6 2.9-1.6 3.1 0 3.6 2 3.6 4.6V19h-3v-5.2c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V19h-2.7z"/>'),
}

# ================================================================ drobne elementy
def sprite(icons=False):
    s = '<svg class="sprite" aria-hidden="true" focusable="false"><defs>' + (icon_symbols() if icons else '')
    s += f'<symbol id="kjk" viewBox="{LOGO_VB}"><path fill="currentColor" d="{LOGO["d"]}"/></symbol>'
    for k, (_, v) in SOCIAL.items():
        s += f'<symbol id="so-{k}" viewBox="0 0 24 24">{v}</symbol>'
    line = 'fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"'
    s += f'<symbol id="chev" viewBox="0 0 16 16"><path d="M4 6l4 4 4-4" {line}/></symbol>'
    s += f'<symbol id="arrow" viewBox="0 0 24 24"><path d="M4 12h15.5M13.5 6l6 6-6 6" {line}/></symbol>'
    s += f'<symbol id="arrow-down" viewBox="0 0 24 24"><path d="M12 4v15.5M6 13.5l6 6 6-6" {line}/></symbol>'
    return s + '</defs></svg>'

def mark(cls='kjk-mark'):
    return f'<svg class="{cls}" viewBox="{LOGO_VB}" aria-hidden="true" focusable="false"><use href="#kjk"/></svg>'

def lockup(cls=''):
    return f'<span class="lockup {cls}">{mark("kjk-mark lockup-mark")}<span class="lockup-tag">Kancelaria Radcy Prawnego</span></span>'

def arrow(cls='ic-arrow', which='arrow'):
    return f'<svg class="{cls}" aria-hidden="true" focusable="false"><use href="#{which}"/></svg>'

def tel(phone): return re.sub(r'[^\d+]', '', phone)

TALK_SIZES = '(max-width: 1023px) min(640px, 92vw), 660px'   # kolumna obok nagłówka specjalizacji; węziej – pod nagłówkiem, najwyżej 640 px

def talk_pic(pg, loading='lazy', fetch=''):
    """Ilustracja rozmowy (autorka: Hanna Jurewicz – bez podpisu przy obrazie, informacja w stopce).
    Źródło: wektorowy PDF (kjk-strona-materialy/ilustracja-rozmowa-wektor.pdf), wyrenderowany i wycięty z tła – przezroczysty WebP 1600 px.
    Miejsce: sekcja „W czym mogę pomóc” na stronie głównej i nagłówek strony Specjalizacje – w kadrze z narożników amarantu."""
    alt = 'Ilustracja: rozmowa w&nbsp;kancelarii – dwie kobiety w&nbsp;fotelach przy małym stoliku z&nbsp;książkami i&nbsp;kwiatami; jedna trzyma dokumenty'
    fp = f' fetchpriority="{fetch}"' if fetch else ''
    ws = f'{pg.u("img/rozmowa-800.webp")} 800w, {pg.u("img/rozmowa-1200.webp")} 1200w, {pg.u("img/rozmowa.webp")} 1600w'
    return (f'<picture><source type="image/webp" srcset="{ws}" sizes="{TALK_SIZES}">'
            f'<img src="{pg.u("img/rozmowa.png")}" alt="{alt}" width="1600" height="841" loading="{loading}" decoding="async"{fp}></picture>')

def portrait(pg, variant='hero', lazy=False):
    alt = 'Katarzyna Jurewicz-Kupeć w&nbsp;fioletowej aksamitnej marynarce, oparta o&nbsp;drewniane krzesło, na zielonym tle'
    m = (f'<source media="(max-width: 719px)" type="image/webp" srcset="{pg.u("img/kjk-portret-m.webp")}" width="720" height="720">'
         f'<source media="(max-width: 719px)" srcset="{pg.u("img/kjk-portret-m.jpg")}" width="720" height="720">')
    lz = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    if variant == 'hero':
        return (f'<picture>{m}<source type="image/webp" srcset="{pg.u("img/kjk-portret.webp")}">'
                f'<img src="{pg.u("img/kjk-portret.jpg")}" alt="{alt}" width="800" height="1067"{lz} decoding="async"></picture>')
    return (f'<picture>{m}<source type="image/webp" srcset="{pg.u("img/kjk-portret-cala.webp")}">'
            f'<img src="{pg.u("img/kjk-portret-cala.jpg")}" alt="{alt}" width="800" height="1200" decoding="async"></picture>')

# ================================================================ rama strony
HEAD_JS = ("(function(){var d=document.documentElement;d.classList.add('js');try{var q=location.search,s=sessionStorage;"
           "if(/[?&]podglad=1/.test(q))s.setItem('kjk-podglad','1');"
           "if(/[?&]podglad=0/.test(q))s.removeItem('kjk-podglad');"
           "if(s.getItem('kjk-podglad')||d.hasAttribute('data-always-demo'))d.classList.add('demo')}catch(e){}})();")

class Page:
    def __init__(self, path):
        self.path = path; self.p = '../' * path.count('/')
    def u(self, target):
        return self.p + target

def head(pg, title, desc, robots=False, always_demo=False, og=False, body_cls='', extra=''):
    r = '\n  <meta name="robots" content="noindex">' if robots else ''
    ad = ' data-always-demo' if always_demo else ''
    ogt = (f'''
  <meta property="og:type" content="website">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{pg.u('img/og-kjk.jpg')}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:locale" content="pl_PL">
  <!-- Po wyborze domeny: link rel="canonical" i pełne adresy og:image / og:url -->''' if og else '')
    return f'''<!doctype html>
<html lang="pl"{ad}>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <meta name="theme-color" content="#FAF8F5">{r}{ogt}
  <link rel="icon" href="{pg.u('img/favicon.svg')}" type="image/svg+xml">
  <link rel="apple-touch-icon" href="{pg.u('img/apple-touch-icon.png')}">{extra}
  <link rel="preload" href="{pg.u('fonts/cormorant-pl.woff2')}" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="{pg.u('fonts/hanken-grotesk-pl.woff2')}" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="{pg.u('css/style.css')}">
  <script>{HEAD_JS}</script>
  <script src="{pg.u('js/config.js')}" defer></script>
  <script src="{pg.u('js/main.js')}" defer></script>
</head>
<body class="{body_cls}">
'''

def mega(pg):
    cols = ''.join(f'<div class="mega-col"><p class="mega-h">{label}</p><ul class="mega-list">'
                   + ''.join(f'<li><a href="{pg.u(spec_url(s))}">{SPEC[s]["name"]}</a></li>' for s in slugs) + '</ul></div>'
                   for label, slugs in GROUPS)
    return f'<div class="mega-cols">{cols}</div>'

def header(pg, current, icons=False):
    def cur(k): return ' aria-current="page"' if current == k else ''
    blog = '' if BLOG_LIVE else ' class="pending-nav"'
    yt = SOCIAL['youtube'][1]
    return f'''  {sprite(icons)}
  <a class="skip-link" href="#tresc">Przejdź do treści</a>
  <header class="site-header" data-header>
    <div class="bar">
      <a class="brand" href="{pg.u('index.html')}" aria-label="Kancelaria KJK – Katarzyna Jurewicz-Kupeć, Kancelaria Radcy Prawnego. Strona główna">
        {mark()}<span class="brand-tag"><span>Kancelaria</span><span>Radcy Prawnego</span></span>
      </a>
      <button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav"><span class="nav-toggle-label">Menu</span><span class="nav-toggle-icon" aria-hidden="true"><span></span><span></span></span></button>
      <nav class="nav" id="nav" aria-label="Menu główne">
        <ul class="nav-list">
          <li><a href="{pg.u('o-mnie.html')}"{cur('about')}>O mnie</a></li>
          <li class="nav-nojs"><a href="{pg.u('specjalizacje.html')}"{cur('spec')}>Specjalizacje</a></li>
          <li class="has-mega"{' data-current' if current == 'spec' else ''}>
            <button class="mega-toggle" type="button" aria-expanded="false" aria-controls="mega">Specjalizacje<svg class="chev" aria-hidden="true"><use href="#chev"/></svg></button>
            <div class="mega" id="mega" hidden>
              {mega(pg)}
              <a class="mega-all" href="{pg.u('specjalizacje.html')}">Wszystkie specjalizacje{arrow()}</a>
            </div>
          </li>
          <li><a href="{pg.u('zasady-wynagradzania.html')}"{cur('fees')}>Zasady wynagradzania</a></li>
          <li class="pending-nav"><a href="{pg.u('wspolpraca.html')}"{cur('coop')}>Współpraca</a></li>
          <li{blog}><a href="{pg.u('blog.html')}"{cur('blog')}>Blog</a></li>
          <li class="nav-yt" data-social="youtube" hidden><a aria-label="Kanał Katarzyny Jurewicz-Kupeć na YouTube (otwiera się w nowej karcie)" rel="noopener" target="_blank"><svg aria-hidden="true" viewBox="0 0 24 24">{yt}</svg></a></li>
          <li class="nav-cta"><a href="{pg.u('kontakt.html')}"{cur('contact')}>Kontakt</a></li>
        </ul>
      </nav>
    </div>
  </header>
'''

def social(where):
    items = ''.join(f'<li data-social="{k}" hidden><a aria-label="{n} – Katarzyna Jurewicz-Kupeć (otwiera się w nowej karcie)" rel="noopener" target="_blank"><svg aria-hidden="true"><use href="#so-{k}"/></svg><span class="so-name">{n}</span></a></li>' for k, (n, _) in SOCIAL.items())
    return (f'<ul class="social social-{where}" aria-label="Media społecznościowe">{items}</ul>'
            f'<p class="social-ph draft-note pending" data-note="Media społecznościowe">Instagram i&nbsp;YouTube pojawią się po wpisaniu adresów w&nbsp;panelu edycji (Dane kontaktowe i&nbsp;media).</p>')

def contact_list(pg, cls=''):
    c = CONTACT
    if any(c.values()):
        rows = ''
        if c['phone']: rows += f'<div><dt>Telefon</dt><dd><a href="tel:{tel(c["phone"])}">{c["phone"]}</a></dd></div>'
        if c['email']: rows += f'<div><dt>E-mail</dt><dd><a href="mailto:{c["email"]}">{c["email"]}</a></dd></div>'
        if c['address']: rows += f'<div><dt>Adres</dt><dd>{c["address"]}</dd></div>'
        return f'<dl class="contact-list {cls}">{rows}</dl>'
    return (f'<dl class="contact-list {cls} pending" data-note="Dane nowej kancelarii – do uzupełnienia (nie przenosić danych SZW Legal)">'
            '<div><dt>Telefon</dt><dd>[numer telefonu]</dd></div><div><dt>E-mail</dt><dd>[adres e-mail]</dd></div><div><dt>Adres</dt><dd>[adres kancelarii]</dd></div></dl>'
            f'<p class="contact-missing {cls} public-only">Telefon, e-mail i&nbsp;adres kancelarii zostaną podane przed publikacją strony.</p>')

def footer(pg, current=''):
    blog = '' if BLOG_LIVE else ' class="pending-nav"'
    specs = ''.join(f'<li><a href="{pg.u(spec_url(s["slug"]))}">{s["name"]}</a></li>' for s in SPECS)
    return f'''  <footer class="site-footer">
    <div class="wrap footer-top">
      <div class="footer-brand">
        <a class="footer-logo" href="{pg.u('index.html')}" aria-label="Kancelaria KJK – strona główna">{lockup('lockup-light')}</a>
        <p>Katarzyna Jurewicz-Kupeć, radca prawny<br>Okręgowa Izba Radców Prawnych we&nbsp;Wrocławiu, wpis WR-1682</p>
      </div>
      <nav class="footer-nav" aria-label="Stopka">
        <div><p class="footer-h">Kancelaria</p><ul>
          <li><a href="{pg.u('o-mnie.html')}">O mnie</a></li>
          <li><a href="{pg.u('specjalizacje.html')}">Specjalizacje</a></li>
          <li><a href="{pg.u('zasady-wynagradzania.html')}">Zasady wynagradzania</a></li>
          <li class="pending-nav"><a href="{pg.u('wspolpraca.html')}">Współpraca</a></li>
          <li{blog}><a href="{pg.u('blog.html')}">Blog</a></li>
          <li><a href="{pg.u('kontakt.html')}">Kontakt</a></li>
        </ul></div>
        <div><p class="footer-h">Specjalizacje</p><ul>{specs}</ul></div>
      </nav>
      <div class="footer-contact">
        <p class="footer-h">Kontakt</p>
        {contact_list(pg, 'on-navy')}
        {social('footer')}
      </div>
    </div>
    <div class="wrap footer-bottom">
      <p>© 2026 Kancelaria KJK</p>
      <p>Ilustracja: Hanna Jurewicz</p>
      <p><a href="{pg.u('polityka-prywatnosci.html')}">Polityka prywatności</a></p>
    </div>
  </footer>
</body>
</html>
'''

def typo(doc):
    parts = re.split(r'(<script\b.*?</script>|<style\b.*?</style>|<title>.*?</title>|<[^>]+>)', doc, flags=re.S)
    for i, t in enumerate(parts):
        if t.startswith('<') or not t.strip():
            continue
        t = re.sub(r'(^|[^\S\u00a0]|[(„])([aiouwzAIOUWZ]) (?=\S)', r'\1\2&nbsp;', t)
        t = re.sub(r'(^|[^\S\u00a0]|[(„])([aiouwzAIOUWZ]) (?=\S)', r'\1\2&nbsp;', t)   # drugi przebieg: „i w”, „a u”
        t = re.sub(r' – ', '&nbsp;– ', t)
        parts[i] = t
    return ''.join(parts)

def write(path, title, desc, current, body, icons=False, **kw):
    pg = Page(path)
    html_body = body(pg) if callable(body) else body
    doc = typo(head(pg, title, desc, **kw) + header(pg, current, icons) + '  <main id="tresc">\n' + html_body + '\n  </main>\n\n' + footer(pg, current))
    doc = doc.replace('\u00a0', '&nbsp;')   # twarde spacje wpisane w panelu
    full = os.path.join(OUT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w').write(doc)
    PAGES_WRITTEN.append(path)
PAGES_WRITTEN = []

def page_head(title, lead='', crumbs='', extra='', cls=''):
    return f'''
    <section class="page-head {cls}" aria-labelledby="ph">
      <div class="wrap page-head-in">
        {crumbs}
        <h1 id="ph">{title}</h1>
        {f'<p class="lead">{lead}</p>' if lead else ''}
        {extra}
      </div>
    </section>'''

# ================================================================ moduły wspólne
def spec_row(pg, s, with_id=False):
    return (f'''<li{f' id="{s["slug"]}"' if with_id else ''}><a class="spec-row" href="{pg.u(spec_url(s['slug']))}">'''
            f'''<span class="spec-ic"><svg aria-hidden="true" focusable="false"><use href="#ic-{s['slug']}"/></svg></span>'''
            f'''<span class="spec-text"><span class="spec-name">{s['name']}</span><span class="spec-short">{s['short']}</span></span>'''
            f'''{arrow('spec-arrow')}</a></li>''')

def spec_groups(pg, heading='h3', with_id=False):
    return '<div class="spec-groups">' + ''.join(
        f'<div class="spec-group"><{heading} class="group-h">{label}</{heading}><ul class="spec-list">'
        + ''.join(spec_row(pg, SPEC[x], with_id) for x in slugs) + f'</ul></div>' for label, slugs in GROUPS) + '</div>'

def path_section(pg, cls='section path'):
    steps = ''.join(f'<li><h3>{t}</h3><p>{d}</p></li>' for t, d in PATH)
    return f'''
    <section id="jak-zaczynamy" class="{cls}" aria-labelledby="path-h">
      <div class="wrap">
        <div class="section-head">
          <h2 id="path-h" class="h-mark">Jak zaczynamy współpracę</h2>
          <p class="section-note">{fmt(STRONA_GLOWNA.get('wspolpraca_opis'))} <a class="link" href="{pg.u('zasady-wynagradzania.html')}">Zasady wynagradzania</a></p>
        </div>
        <ol class="steps to-review" data-note="Opis drogi kontaktu – propozycja do akceptacji Katarzyny">{steps}</ol>
      </div>
    </section>'''

def contact_band(pg):
    return f'''
    <section class="section contact-band" aria-labelledby="kontakt-h">
      <div class="wrap split">
        <div class="split-head"><h2 id="kontakt-h" class="h-mark">Kontakt</h2></div>
        <div class="split-body">
          <p class="standfirst to-review" data-note="Opis – do akceptacji Katarzyny">{fmt(STRONA_GLOWNA.get('kontakt_zdanie'))}</p>
          {contact_list(pg)}
          <p><a class="btn btn-primary" href="{pg.u('kontakt.html')}">Przejdź do kontaktu</a></p>
        </div>
      </div>
    </section>'''

# ================================================================ STRONA GŁÓWNA
def home(pg):
    G = STRONA_GLOWNA
    facts = '\n'.join(f'            <div><dt>{fmt(x.get("tytul"))}</dt><dd>{fmt(x.get("opis"))}</dd></div>' for x in G.get('o_mnie_fakty', []))
    call = (f'<p class="hero-call">lub zadzwoń: <a href="tel:{tel(CONTACT["phone"])}">{CONTACT["phone"]}</a></p>' if CONTACT['phone'] else
            '<p class="hero-call pending" data-note="Telefon kancelarii – do uzupełnienia">lub zadzwoń: [numer telefonu]</p>')
    latest = sorted(ARTICLES, key=lambda a: a['published'], reverse=True)[:3]
    materials = (f'''
    <section class="section materials" aria-labelledby="mat-h">
      <div class="wrap split">
        <div class="split-head"><h2 id="mat-h" class="h-mark">Z&nbsp;bloga</h2><p><a class="link-arrow" href="{pg.u('blog.html')}">Wszystkie artykuły{arrow()}</a></p></div>
        <div class="split-body"><ul class="posts">{''.join(post_item(pg, a) for a in latest)}</ul></div>
      </div>
    </section>''' if latest else f'''
    <section class="section materials pending" data-note="Materiały eksperckie i opinie – pojawią się po publikacji pierwszych artykułów i otrzymaniu zgód autorów opinii" aria-labelledby="mat-h">
      <div class="wrap split">
        <div class="split-head"><h2 id="mat-h" class="h-mark">Materiały i&nbsp;opinie</h2></div>
        <div class="split-body">
          <p class="draft-note">Tu pojawią się najnowsze artykuły (po publikacji pierwszych tekstów) oraz opinie – wyłącznie dostarczone i&nbsp;zaakceptowane przez ich autorów. Bez pustych miejsc i&nbsp;ocen na próbę.</p>
        </div>
      </div>
    </section>''')
    return f'''
    <section class="hero" aria-labelledby="hero-h">
      <div class="wrap hero-grid">
        <div class="hero-copy">
          <h1 id="hero-h" class="hero-name h-mark"><span class="hero-name-n">Katarzyna Jurewicz-Kupeć,</span> <span class="hero-name-t">radca&nbsp;prawny</span></h1>
          <p class="hero-quote">{QUOTE}</p>
          <p class="hero-lead">{fmt(G.get('zdanie'))}</p>
          <div class="hero-actions">
            <a class="btn btn-primary" href="{pg.u('kontakt.html')}">Umów rozmowę</a>
            <a class="link-arrow" href="#specjalizacje">Specjalizacje{arrow('ic-arrow', 'arrow-down')}</a>
          </div>
          {call}
        </div>
        <figure class="hero-photo">
          <div class="framed">{portrait(pg)}</div>
          <figcaption>{fmt(G.get('podpis_zdjecia'))}</figcaption>
        </figure>
      </div>
    </section>

    <section id="specjalizacje" class="section specs" aria-labelledby="spec-h">
      <div class="wrap">
        <div class="talk-intro">
          <div class="talk-intro-text">
            <h2 id="spec-h" class="h-mark">W&nbsp;czym mogę pomóc</h2>
            <p class="section-note">{fmt(G.get('specjalizacje_opis'))}</p>
          </div>
          <figure class="talk-art"><div class="framed">{talk_pic(pg)}</div></figure>
        </div>
        {spec_groups(pg)}
      </div>
    </section>

    <section class="section about-short" aria-labelledby="about-h">
      <div class="wrap split">
        <div class="split-head">
          <h2 id="about-h" class="h-mark">O&nbsp;mnie</h2>
          <p><a class="link-arrow" href="{pg.u('o-mnie.html')}">Więcej o&nbsp;mnie{arrow()}</a></p>
        </div>
        <div class="split-body">
          <p class="standfirst">{fmt(G.get('o_mnie_zdanie'))}</p>
          <dl class="facts facts-4">
{facts}
          </dl>
        </div>
      </div>
    </section>
{path_section(pg)}
{materials}
{contact_band(pg)}'''

# ================================================================ O MNIE
def about(pg):
    A = load('o-mnie.json')
    secs = '\n'.join(f'            <section aria-labelledby="a{i}"><h2 id="a{i}" class="about-h">{fmt(x.get("tytul"))}</h2>\n'
                     + '\n'.join(f'              <p>{p}</p>' for p in paras(x.get('tresc'))) + '</section>'
                     for i, x in enumerate(A.get('sekcje', []), 1))
    close = f'\n            <p class="about-close">{fmt(A["zakonczenie"])}</p>' if (A.get('zakonczenie') or '').strip() else ''
    after = f'\n            <p class="about-after">{fmt(A["poza_kancelaria"])}</p>' if (A.get('poza_kancelaria') or '').strip() else ''
    return f'''
    <section class="page-head about-head" aria-labelledby="ph">
      <div class="wrap about-grid">
        <figure class="about-photo">
          <div class="framed">{portrait(pg, 'about')}</div>
          <figcaption>{fmt(A.get('podpis_zdjecia'))}</figcaption>
        </figure>
        <div class="about-text">
          <p class="hero-name h-mark"><span class="hero-name-n">Katarzyna Jurewicz-Kupeć,</span> <span class="hero-name-t">radca&nbsp;prawny</span></p>
          <h1 id="ph">O&nbsp;mnie</h1>
          <p class="standfirst about-lead">{fmt(A.get('wstep'))}</p>
          <div class="about-body to-review" data-note="Tekst Katarzyny po redakcji – do akceptacji (zmiany wypisane w podglądzie)">
{secs}{close}{after}
          </div>
          <div class="about-next">
            <a class="btn btn-primary" href="{pg.u('kontakt.html')}">Umów rozmowę</a>
            <a class="link-arrow" href="{pg.u('specjalizacje.html')}">Specjalizacje{arrow()}</a>
          </div>
        </div>
      </div>
    </section>
    <section class="section-s opinions pending" data-note="Miejsce na autentyczne opinie i rekomendacje – po otrzymaniu zgód autorów" aria-label="Opinie">
      <div class="wrap split"><div class="split-head"><h2 class="h-mark">Opinie</h2></div>
        <div class="split-body"><p class="draft-note">Opinie i&nbsp;rekomendacje pojawią się tu dopiero po ich dostarczeniu – z&nbsp;pisemną zgodą autorów.</p></div></div>
    </section>'''

# ================================================================ SPECJALIZACJE
def spec_overview(pg):
    return f'''
    <section class="page-head specs-head" aria-labelledby="ph">
      <div class="wrap talk-intro">
        <div class="page-head-in">
          <h1 id="ph">Specjalizacje</h1>
          <p class="lead">{fmt(load('strona-specjalizacje.json').get('wstep'))}</p>
        </div>
        <figure class="talk-art"><div class="framed">{talk_pic(pg, 'eager', 'high')}</div></figure>
      </div>
    </section>''' + f'''
    <section class="section-s specs specs-page" aria-label="Lista specjalizacji">
      <div class="wrap">{spec_groups(pg, 'h2', with_id=True)}</div>
    </section>
{path_section(pg)}'''

def spec_page(pg, s):
    others = ''.join(f'<li><a href="{pg.u(spec_url(o["slug"]))}">{o["name"]}{arrow()}</a></li>' for o in SPECS if o is not s)
    lst = lambda xs: ''.join(f'<li>{x}</li>' for x in xs)
    note = (f'''<div class="to-review" data-note="Informacja prawna – do sprawdzenia i akceptacji Katarzyny"><aside class="note-box" aria-label="Warto wiedzieć">
              <p class="note-h">Warto wiedzieć</p><p>{s['note']}</p></aside></div>''' if s.get('note') else '')
    crumbs = f'<nav class="crumbs" aria-label="Jesteś tutaj"><a href="{pg.u("specjalizacje.html")}">Specjalizacje</a><span aria-hidden="true">/</span><span aria-current="page">{s["name"]}</span></nav>'
    return f'''
    <section class="page-head spec-head" aria-labelledby="ph">
      <div class="wrap">
        {crumbs}
        <div class="spec-title">
          <span class="spec-ic spec-ic-l"><svg aria-hidden="true" focusable="false"><use href="#ic-{s['slug']}"/></svg></span>
          <h1 id="ph">{s['name']}</h1>
        </div>
        <p class="lead to-review" data-note="Opis – propozycja do akceptacji Katarzyny">{s['lead']}</p>
      </div>
    </section>
    <div class="section-s spec-body">
      <div class="wrap spec-layout">
        <div class="spec-main">
          <section class="spec-block to-review" data-note="Propozycja do akceptacji Katarzyny" aria-labelledby="kiedy-h">
            <h2 id="kiedy-h" class="block-h">Kiedy warto się zgłosić</h2>
            <ul class="dash-list">{lst(s['when'])}</ul>
          </section>
          <section class="spec-block to-review" data-note="Zakres pomocy – do akceptacji Katarzyny" aria-labelledby="pomoc-h">
            <h2 id="pomoc-h" class="block-h">Jak mogę pomóc</h2>
            <ul class="dash-list">{lst(s['help'])}</ul>
          </section>
          <section class="spec-block to-review" data-note="Propozycja do akceptacji Katarzyny" aria-labelledby="przygotuj-h">
            <h2 id="przygotuj-h" class="block-h">Co przygotować na rozmowę</h2>
            <ul class="check-list">{lst(s['prepare'])}</ul>
            <p class="block-note">Wystarczy to, co już masz – brakujące dokumenty ustalimy razem.</p>
          </section>
          {note}
        </div>
        <aside class="spec-side">
          <section class="next-box" aria-labelledby="next-h">
            <h2 id="next-h" class="next-h">Następny krok</h2>
            <p>Opisz krótko, czego dotyczy sprawa – odezwę się, żeby umówić rozmowę. Na niej uzgodnię z&nbsp;Tobą zakres pomocy i&nbsp;sposób rozliczenia.</p>
            <a class="btn btn-light" href="{pg.u('kontakt.html')}?temat={s['slug']}">Zapytaj o&nbsp;tę sprawę</a>
            <a class="link-light" href="{pg.u('zasady-wynagradzania.html')}">Zasady wynagradzania</a>
          </section>
        </aside>
      </div>
    </div>
    <nav class="section-s other-specs" aria-labelledby="other-h">
      <div class="wrap">
        <h2 id="other-h" class="group-h">Inne specjalizacje</h2>
        <ul>{others}</ul>
      </div>
    </nav>'''

# ================================================================ KONTAKT
def contact(pg):
    active = bool(FORM_PROVIDER)
    opts = ''.join(f'<option value="{s["slug"]}">{plain(s["name"])}</option>' for s in SPECS)
    endpoint = FORM_PROVIDER if FORM_PROVIDER.startswith('http') else ''
    provider = 'netlify' if FORM_PROVIDER == 'netlify' else ('endpoint' if endpoint else '')
    attrs = ''
    if provider == 'netlify':
        attrs = ' method="post" name="kontakt" data-netlify="true" netlify-honeypot="www"'
    elif provider == 'endpoint':
        attrs = f' method="post" action="{endpoint}"'
    nf_hidden = '<input type="hidden" name="form-name" value="kontakt">' if provider == 'netlify' else ''
    off = '' if active else '''
          <div class="notice" id="form-off">
            <p><strong>Formularz jeszcze nie działa.</strong> Trwa konfiguracja wysyłki wiadomości – do tego czasu pola są nieaktywne i&nbsp;nic nie jest przesyłane.</p>
          </div>'''
    K = load('kontakt.json')
    after = ''.join(f'<li><b>{fmt(x.get("tytul"))}</b><span>{fmt(x.get("opis"))}</span></li>' for x in K.get('po_kontakcie', []))
    first = fmt(K.get('pierwsza_rozmowa'))
    consult = (f'<p class="consult-cost"><b>Pierwsza rozmowa:</b> {first}</p>' if first else
               '<p class="consult-cost pending" data-note="Pierwsza rozmowa – do zatwierdzenia przez Katarzynę"><b>Pierwsza rozmowa:</b> [forma – telefon, spotkanie albo online; czas trwania; koszt]</p>')
    return page_head('Kontakt', fmt(K.get('wstep'))) + f'''
    <section class="section-s contact-page" aria-label="Dane kontaktowe i formularz">
      <div class="wrap contact-grid">
        <div class="contact-info">
          {contact_list(pg, 'contact-list-l')}
          <section class="after to-review" data-note="Opis – do akceptacji Katarzyny" aria-labelledby="after-h">
            <h2 id="after-h" class="block-h">Co dzieje się po kontakcie</h2>
            <ol class="after-list">{after}</ol>
          </section>
          {consult}
          <p class="safety">Jeśli grozi Ci niebezpieczeństwo, dzwoń pod <a href="tel:112">112</a>. Całodobowo działa Ogólnopolskie Pogotowie dla Osób Doznających Przemocy Domowej „Niebieska Linia”: <a href="tel:800120002">800&nbsp;120&nbsp;002</a>.</p>
          {social('contact')}
        </div>
        <div id="formularz" class="form-wrap">
          <h2 class="block-h">Prośba o&nbsp;kontakt</h2>
          <p class="form-intro">{fmt(K.get('formularz_wstep'))}</p>{off}
          <form id="contact-form" class="form{'' if active else ' is-off'}" novalidate data-provider="{provider}" data-endpoint="{endpoint}"{attrs}>
            {nf_hidden}
            <fieldset{'' if active else ' disabled aria-describedby="form-off"'}>
              <legend class="visually-hidden">Prośba o&nbsp;kontakt</legend>
              <div class="field">
                <label for="imie">Imię</label>
                <input id="imie" name="imie" type="text" autocomplete="given-name" required aria-describedby="imie-err">
                <p class="error" id="imie-err"></p>
              </div>
              <div class="field">
                <label for="kontakt-dane">Telefon albo e-mail</label>
                <input id="kontakt-dane" name="kontakt" type="text" autocomplete="email" inputmode="email" required aria-describedby="kontakt-hint kontakt-err">
                <p class="hint" id="kontakt-hint">Wystarczy jedna droga kontaktu.</p>
                <p class="error" id="kontakt-err"></p>
              </div>
              <div class="field">
                <label for="temat">Czego dotyczy sprawa?</label>
                <select id="temat" name="temat" required aria-describedby="temat-err"><option value="">Wybierz temat</option>{opts}<option value="inna">Inna sprawa</option></select>
                <p class="error" id="temat-err"></p>
              </div>
              <div class="hp" aria-hidden="true"><label for="www">Nie wypełniaj tego pola</label><input id="www" name="www" type="text" tabindex="-1" autocomplete="off"></div>
              <p class="form-note">Nie opisuj tu szczegółów sprawy i&nbsp;nie dołączaj dokumentów – porozmawiamy o&nbsp;nich bezpośrednio.</p>
              <button class="btn btn-primary btn-send" type="submit"><span class="btn-label">Poproś o&nbsp;kontakt</span></button>
              <p class="form-privacy to-review" data-note="Informacja o danych – do zatwierdzenia razem z polityką prywatności">Imię, dane kontaktowe i&nbsp;temat wykorzystam tylko po to, żeby odpowiedzieć na Twoją prośbę. Więcej w&nbsp;<a href="{pg.u('polityka-prywatnosci.html')}">polityce prywatności</a>.</p>
            </fieldset>
            <div class="form-msg" id="form-msg" role="alert" tabindex="-1" hidden></div>
          </form>
          <div class="form-done" id="form-done" role="status" tabindex="-1" hidden></div>
        </div>
      </div>
    </section>'''

# ================================================================ ZASADY WYNAGRADZANIA
def fees(pg):
    Z = load('zasady-wynagradzania.json')
    steps = '\n'.join(f'            <li><h3>{fmt(x.get("tytul"))}</h3><p>{fmt(x.get("opis"))}</p></li>' for x in Z.get('kroki', []))
    forms = [fmt(x) for x in Z.get('formy_rozliczenia', []) if (x or '').strip()]
    forms_html = (f'''<div>
            <p class="group-h">Formy rozliczenia</p>
            <ul class="dash-list">{''.join(f'<li>{x}</li>' for x in forms)}</ul>
          </div>''' if forms else '''<div class="pending" data-note="Formy rozliczenia i pierwsza rozmowa – do decyzji Katarzyny (bez kwot, dopóki ich nie poda)">
            <p class="group-h">Formy rozliczenia</p>
            <ul class="dash-list"><li>[kwota za całą sprawę]</li><li>[kwota za etap]</li><li>[stawka godzinowa]</li><li>[stała obsługa firmy – miesięcznie]</li><li>[pierwsza rozmowa: forma, czas i&nbsp;koszt]</li></ul>
          </div>''')
    costs = '\n'.join(f'            <div><dt>{fmt(x.get("nazwa"))}</dt><dd>{fmt(x.get("opis"))}</dd></div>' for x in Z.get('koszty', []))
    other = fmt(Z.get('inne_wydatki'))
    other_html = (f'<div><dt>Inne wydatki</dt><dd>{other}</dd></div>' if other else
                  '<div class="pending" data-note="Czy i jak rozliczane są wydatki – do decyzji Katarzyny"><dt>Inne wydatki</dt><dd>[np. tłumaczenia, dojazdy – czy i&nbsp;jak są rozliczane]</dd></div>')
    return page_head('Zasady wynagradzania', fmt(Z.get('wstep'))) + f'''
    <section class="section-s fees-page" aria-label="Jak ustalane jest wynagrodzenie">
      <div class="wrap split">
        <div class="split-head"><h2 class="h-mark">Jak to ustalamy</h2></div>
        <div class="split-body">
          <ol class="fee-steps to-review" data-note="Opis – propozycja do akceptacji Katarzyny">
{steps}
          </ol>
          {forms_html}
        </div>
      </div>
    </section>
    <section class="section-s fees-page" aria-labelledby="koszt-h">
      <div class="wrap split">
        <div class="split-head"><h2 id="koszt-h" class="h-mark">Z&nbsp;czego składa się koszt sprawy</h2></div>
        <div class="split-body">
          <dl class="cost-list">
{costs}
            {other_html}
          </dl>
          <p class="fees-cta"><a class="btn btn-primary" href="{pg.u('kontakt.html')}">Zapytaj o&nbsp;rozliczenie swojej sprawy</a></p>
        </div>
      </div>
    </section>'''

# ================================================================ WSPÓŁPRACA / BLOG / POLITYKA / 404
def coop(pg):
    return page_head('Współpraca', '', extra=f'<p class="lead public-only">Ta część strony jest w&nbsp;przygotowaniu.</p><p class="public-only"><a class="link-arrow" href="{pg.u("kontakt.html")}">Kontakt{arrow()}</a></p>') + f'''
    <section class="section-s pending" data-note="Konstrukcja modułu – bez danych. Tylko prawdziwi partnerzy, za ich zgodą.">
      <div class="wrap"><p class="draft-note">Każdy partner: rola, imię i&nbsp;nazwisko albo nazwa, 1–2 zdania o&nbsp;współpracy i&nbsp;zdjęcie – wyłącznie za zgodą obu stron.</p></div>
    </section>'''

def post_item(pg, a):
    return (f'<li class="post"><a href="{pg.u("blog/" + a["slug"] + ".html")}"><span class="post-meta">{CAT[a["cat"]]["name"]} · <time datetime="{a["published"]}">{pl_date(a["published"])}</time></span>'
            f'<span class="post-title">{a["title"]}</span><span class="post-lead">{a["lead"]}</span><span class="post-more">Czytaj artykuł{arrow()}</span></a></li>')

def draft_item(pg, t):
    cat, svc, title = t
    return (f'<li class="post post-draft"><div><span class="post-meta">{CAT[cat]["name"]} · szkic tematu</span><span class="post-title">{title}</span>'
            f'<span class="post-lead">Propozycja tematu – artykuł jeszcze nie istnieje.</span></div></li>')

def blog(pg):
    if BLOG_LIVE:
        listing = f'<section class="section-s"><div class="wrap"><ul class="posts posts-page" id="posts">{"".join(post_item(pg, a) for a in sorted(ARTICLES, key=lambda a: a["published"], reverse=True))}</ul></div></section>'
    else:
        listing = f'''<section class="section-s pending" data-note="Podgląd redakcyjny – propozycje tematów, nie artykuły. Szkice nie są publikowane.">
      <div class="wrap"><ul class="posts posts-page">{''.join(draft_item(pg, t) for t in TOPICS)}</ul>
        <p class="more-line"><a class="link-arrow" href="{pg.u('blog/wzor-artykulu.html')}">Szablon pojedynczego artykułu{arrow()}</a></p></div>
    </section>'''
    return page_head('Blog', '' if BLOG_LIVE else '', extra='' if BLOG_LIVE else f'<p class="lead public-only">Pierwsze artykuły są w&nbsp;przygotowaniu.</p><p class="public-only"><a class="link-arrow" href="{pg.u("specjalizacje.html")}">Specjalizacje{arrow()}</a></p>') + listing + f'''
    <section id="filmy" class="section-s" data-videos hidden aria-labelledby="filmy-h">
      <div class="wrap"><h2 id="filmy-h" class="h-mark">Filmy</h2><p class="section-note">Film ładuje się dopiero po kliknięciu „Odtwórz”.</p><ul class="films" id="v-list"></ul></div>
    </section>
    <section class="section-s pending" data-note="Układ sekcji filmów i mediów – bez materiałów (adresy i filmy – w panelu edycji)">
      <div class="wrap"><h2 class="h-mark">Filmy</h2><p class="draft-note">Filmy z&nbsp;YouTube pojawią się po dodaniu ich w&nbsp;panelu edycji (Dane kontaktowe i&nbsp;media): link, tytuł, krótki opis, napisy lub transkrypcja; odtwarzacz ładuje się dopiero po kliknięciu.</p>{social('follow')}</div>
    </section>'''

def article_html(pg, a, template=False):
    svc = SPEC[a['service']]
    pub = a['published'] if template else pl_date(a['published'])
    upd = f' · zaktualizowano: {a["updated"] if template else pl_date(a["updated"])}' if a.get('updated') else ''
    return f'''
    <article>
      <header class="page-head article-head" aria-labelledby="ph">
        <div class="wrap prose-wrap">
          <nav class="crumbs" aria-label="Jesteś tutaj"><a href="{pg.u('blog.html')}">Blog</a><span aria-hidden="true">/</span><span>{CAT[a['cat']]['name']}</span></nav>
          <h1 id="ph">{a['title']}</h1>
          <p class="lead">{a['lead']}</p>
          <p class="byline"><a class="byline-author" href="{pg.u('o-mnie.html')}">Katarzyna Jurewicz-Kupeć</a>, radca prawny · opublikowano: {pub}{upd}</p>
        </div>
      </header>
      <div class="section-s article-body">
        <div class="wrap prose-wrap prose">{a['body']}
          <p class="disclaimer to-review" data-note="Treść zastrzeżenia do akceptacji">Artykuł ma charakter informacyjny. Każda sprawa wymaga indywidualnej oceny.</p>
          <aside class="article-next" aria-label="Powiązana specjalizacja">
            <p class="group-h">Powiązana specjalizacja</p>
            <p><a class="service-link spec-link" href="{pg.u(spec_url(svc['slug']))}">{svc['name']}{arrow()}</a></p>
            <p class="article-author">Autorka: <a class="link" href="{pg.u('o-mnie.html')}">Katarzyna Jurewicz-Kupeć</a>, radca prawny</p>
            <p><a class="btn btn-primary" href="{pg.u('kontakt.html')}?temat={svc['slug']}">Zapytaj o&nbsp;swoją sprawę</a></p>
          </aside>
          {'<section aria-labelledby="rel-h"><h2 id="rel-h" class="block-h">Powiązane materiały</h2><ul class="related"><li>[Powiązany artykuł lub film]</li><li>[Powiązany artykuł lub film]</li></ul></section>' if template else ''}
        </div>
      </div>
    </article>'''

TEMPLATE = dict(slug='wzor-artykulu', cat='naleznosci', service='windykacja', title='[Tytuł artykułu]',
                lead='[Lead – 1–2 zdania: czego dotyczy artykuł i dla kogo jest.]', published='[data publikacji]', updated='[data aktualizacji – tylko przy rzeczywistej zmianie treści]',
                body='''<h2 class="block-h">[Śródtytuł]</h2><p>[Akapit – treść napisana i zaakceptowana przez Katarzynę.]</p><h2 class="block-h">[Śródtytuł]</h2><p>[Akapit.]</p>''')

def privacy(pg):
    form_state = ('<li>Formularz kontaktowy jest jeszcze nieaktywny i&nbsp;nie przesyła żadnych danych.</li>' if not FORM_PROVIDER else
                  '<li>Wiadomości z&nbsp;formularza kontaktowego przesyła usługa Netlify Forms; trafiają do kancelarii pocztą elektroniczną.</li>' if FORM_PROVIDER == 'netlify' else
                  '<li>Wiadomości z&nbsp;formularza kontaktowego przesyła zewnętrzna usługa formularzy; trafiają do kancelarii pocztą elektroniczną.</li>')
    body = md_html(load('polityka-prywatnosci.json').get('tresc'))
    if body:   # pełna treść wpisana w panelu – zastępuje projekt z miejscami do uzupełnienia
        return page_head('Polityka prywatności') + f'''
    <section class="section-s" aria-label="Treść polityki prywatności">
      <div class="wrap prose-wrap prose">{body}</div>
    </section>
    <section class="section-s" aria-labelledby="stan-h">
      <div class="wrap prose-wrap prose">
        <h2 id="stan-h" class="block-h">Jak działa ta strona</h2>
        <ul>
          <li>Strona nie używa plików cookies, analityki ani narzędzi śledzących.</li>
          <li>Kroje pisma i&nbsp;zdjęcia są na serwerze strony – przeglądając ją, nie łączysz się z&nbsp;innymi serwisami.</li>
          <li>Stronę udostępnia Netlify (hosting). Jak każdy serwer WWW, przetwarza techniczne dane połączenia, m.in. adres IP i&nbsp;informacje o&nbsp;przeglądarce – żeby wyświetlić stronę i&nbsp;chronić ją przed nadużyciami.</li>
          <li>Ikony Instagrama i&nbsp;YouTube to zwykłe linki. Filmy (gdy się pojawią) ładują się z&nbsp;youtube-nocookie.com dopiero po kliknięciu „Odtwórz”.</li>
          {form_state}
        </ul>
      </div>
    </section>'''
    return page_head('Polityka prywatności', 'Pełna treść zostanie opublikowana przed uruchomieniem formularza kontaktowego.') + f'''
    <section class="section-s" aria-labelledby="stan-h">
      <div class="wrap prose-wrap prose">
        <h2 id="stan-h" class="block-h">Jak działa ta strona</h2>
        <ul class="to-review" data-note="Stan faktyczny strony – do potwierdzenia przy publikacji">
          <li>Strona nie używa plików cookies, analityki ani narzędzi śledzących.</li>
          <li>Kroje pisma i&nbsp;zdjęcia są na serwerze strony – przeglądając ją, nie łączysz się z&nbsp;innymi serwisami.</li>
          <li>Stronę udostępnia Netlify (hosting). Jak każdy serwer WWW, przetwarza techniczne dane połączenia, m.in. adres IP i&nbsp;informacje o&nbsp;przeglądarce – żeby wyświetlić stronę i&nbsp;chronić ją przed nadużyciami.</li>
          <li>Ikony Instagrama i&nbsp;YouTube to zwykłe linki. Filmy (gdy się pojawią) ładują się z&nbsp;youtube-nocookie.com dopiero po kliknięciu „Odtwórz”.</li>
          {form_state}
        </ul>
      </div>
    </section>
    <section class="section-s pending" data-note="Projekt dokumentu – do uzupełnienia i zatwierdzenia przez Katarzynę. To nie jest gotowy dokument prawny." aria-labelledby="projekt-h">
      <div class="wrap prose-wrap prose">
        <h2 id="projekt-h" class="block-h">Projekt polityki – dane do uzupełnienia</h2>
        <ol>
          <li><b>Administrator danych:</b> [imię i&nbsp;nazwisko, nazwa kancelarii, adres, e-mail, telefon].</li>
          <li><b>Jakie dane:</b> z&nbsp;formularza – imię, telefon albo e-mail i&nbsp;ogólny temat sprawy; z&nbsp;korespondencji – dane, które przekażesz; techniczne dane połączenia (hosting).</li>
          <li><b>Cel i&nbsp;podstawa:</b> odpowiedź na zapytanie i&nbsp;działania przed zawarciem umowy (art. 6 ust. 1 lit. b RODO); prawnie uzasadniony interes – kontakt i&nbsp;bezpieczeństwo strony (art. 6 ust. 1 lit. f RODO) – [do potwierdzenia].</li>
          <li><b>Odbiorcy:</b> Netlify, Inc. – hosting i&nbsp;obsługa formularza; [dostawca poczty e-mail kancelarii].</li>
          <li><b>Przekazywanie poza EOG:</b> Netlify, Inc. (USA) – [podstawa przekazania do sprawdzenia i&nbsp;wpisania].</li>
          <li><b>Okres przechowywania:</b> [np. do zakończenia korespondencji; przy współpracy – zgodnie z&nbsp;przepisami].</li>
          <li><b>Prawa:</b> dostęp, sprostowanie, usunięcie, ograniczenie przetwarzania, sprzeciw, przenoszenie danych; skarga do Prezesa Urzędu Ochrony Danych Osobowych.</li>
          <li><b>Tajemnica zawodowa:</b> informacje przekazane w&nbsp;związku ze sprawą są objęte tajemnicą zawodową radcy prawnego.</li>
          <li><b>Dobrowolność:</b> podanie danych jest dobrowolne, ale bez nich nie mogę odpowiedzieć.</li>
        </ol>
      </div>
    </section>'''

def notfound(pg):
    return page_head('Nie ma takiej strony', 'Adres mógł się zmienić albo zawierać literówkę.',
                     extra=f'<p class="hero-actions"><a class="btn btn-primary" href="{pg.u("index.html")}">Strona główna</a><a class="link-arrow" href="{pg.u("specjalizacje.html")}">Specjalizacje{arrow()}</a></p>')

# ================================================================ PODGLĄD REDAKCYJNY
def lum(h):
    c = [int(h.lstrip('#')[i:i+2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]
def cr(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True); return (la + 0.05) / (lb + 0.05)
SWATCHES = [('Papier', '#FAF8F5', 'tło strony'), ('Pas sekcji', '#F2EEE8', 'kontakt, wyróżnienia'), ('Granat', '#1B2540', 'tekst, przycisk, stopka'),
            ('Amarant', '#A8255B', 'znaczniki, stany, drobne etykiety'), ('Szary granat', '#555B6E', 'tekst pomocniczy'), ('Róż na granacie', '#F2A3C1', 'etykiety w stopce')]
PAIRS = [('Tekst', '#1B2540', 'papier', '#FAF8F5'), ('Tekst pomocniczy', '#555B6E', 'papier', '#FAF8F5'), ('Tekst pomocniczy', '#555B6E', 'pas sekcji', '#F2EEE8'),
         ('Amarant', '#A8255B', 'papier', '#FAF8F5'), ('Biały', '#FFFFFF', 'granat', '#1B2540'), ('Biały', '#FFFFFF', 'amarant', '#A8255B'),
         ('Jasnoszary', '#C9CEDB', 'granat', '#1B2540'), ('Róż', '#F2A3C1', 'granat', '#1B2540')]
EDITS = [
    '„złożyłam pozytywnie egzamin sędziowski” → „zdałam egzamin sędziowski”.',
    '„Odskocznią od pracy na rzecz podmiotów gospodarczych jest dla mnie…” → „Od 2010 roku bezpłatnie udzielam pomocy prawnej osobom doznającym przemocy domowej, osobom w&nbsp;kryzysie i&nbsp;osobom bezdomnym – we współpracy z&nbsp;organizacją pozarządową, która je wspiera.” (bez nazwy organizacji, jak dotąd).',
    '„ofiary przemocy domowej” → „osoby doznające przemocy domowej” – określenie używane dziś m.in. w&nbsp;nazwie „Niebieskiej Linii”.',
    '„Doświadczenia powiązane z&nbsp;prawem rodzinnym ugruntowały mnie w&nbsp;przekonaniu, iż…” → „Doświadczenia z&nbsp;prawem rodzinnym przekonały mnie, że to najdelikatniejsza gałąź prawa – i&nbsp;zarazem taka, która wymaga od prawnika ogromnego zaangażowania.”',
    'Kolejność „O mnie”: rok 2007 i&nbsp;samorząd na początku, potem wykształcenie, doświadczenie i&nbsp;pomoc osobom w&nbsp;kryzysie – każdy fakt raz.',
    'Strona główna: zamiast pełnego biogramu – jedno przekonanie Katarzyny, rodzaje klientów i&nbsp;trzy fakty; pełny tekst na stronie „O mnie”.',
    'Pierwszy ekran (wersja 9): na prośbę zamawiającej wraca pełne zdanie Katarzyny „Problem najczęściej tkwi w&nbsp;szczególe…” – w&nbsp;jej brzmieniu; nagłówkiem H1 jest imię, nazwisko i&nbsp;zawód. (W&nbsp;wersji 6 zdanie zastępował krótszy nagłówek „Pomoc prawna, w&nbsp;której liczy się szczegół.”)',
    'Zasady wynagradzania: usunięte „Razem – znasz przed startem” (obietnica całkowitego kosztu, której nie potwierdziliśmy); zostaje opis, jak uzgadniamy zakres i&nbsp;sposób rozliczenia.',
]
MISSING = [
    'Pasje – śpiew i malarstwo: zdjęcia prac lub występów i kilka zdań Katarzyny. Na razie strona ma tylko zdanie „Poza kancelarią: śpiew i malarstwo.” – nic nie dopisujemy bez materiałów.',
    'Pierwsza rozmowa: forma (telefon, spotkanie, online), czas trwania i koszt – krótka informacja na stronie kontaktu i w zasadach wynagradzania.',
    'Informacja o danych pod formularzem (formularz nie ma już pola zgody – prosi tylko o imię, kontakt i temat) – do zatwierdzenia razem z polityką prywatności.',
    'Dane kontaktowe nowej kancelarii: telefon, e-mail, adres (nie przenosić danych SZW Legal) – Katarzyna może je wpisać sama w panelu edycji (Dane kontaktowe i media). Bez nich strona nie ma działającej drogi kontaktu.',
    'Formularz: decyzja o usłudze (przygotowane: Netlify Forms – jeden przełącznik w netlify.toml), adres e-mail do powiadomień, włączenie wykrywania formularzy w panelu Netlify. Do tego czasu formularz jest widoczny, ale nieaktywny.',
    'Polityka prywatności: administrator, okres przechowywania, dostawca poczty, podstawa przekazania danych do USA (Netlify) – projekt z miejscami do uzupełnienia jest na stronie.',
    'Akceptacja nagłówka pierwszego ekranu (trzy propozycje – wyżej na tej planszy).',
    'Akceptacja treści ośmiu podstron specjalizacji: kiedy się zgłosić, jak mogę pomóc, co przygotować, „Warto wiedzieć”.',
    'Akceptacja zredagowanego tekstu „O mnie” (zmiany: „zdałam egzamin sędziowski”, opis pomocy od 2010 roku zamiast „odskoczni”, krótsze zdania).',
    'Zasady wynagradzania: formy rozliczenia, forma i koszt pierwszej rozmowy, rozliczanie wydatków (bez kwot, dopóki ich nie poda).',
    'Opis drogi kontaktu (cztery kroki) i tekst „Co dzieje się po kontakcie”.',
    'Opinie i rekomendacje – tylko prawdziwe, z pisemną zgodą autorów. Partnerzy do „Współpracy” – za ich zgodą.',
    'Artykuły na blog (napisane lub zatwierdzone przez Katarzynę); filmy z napisami lub transkrypcją.',
    'Adresy profili Instagram i YouTube (panel edycji → Dane kontaktowe i media).',
    'Domena, adres kanoniczny, pełne adresy Open Graph.',
    'Zdjęcie portretowe w wyższej rozdzielczości (obecne 800×1200 px) oraz zgoda autora zdjęcia na publikację i ewentualny podpis.',
    'Logo w wersji wektorowej od autora (na stronie – wierny obrys z pliku JPG).',
    'Ilustracja rozmowy (autorka: Hanna Jurewicz – informacja w stopce): potwierdzenie zgody autorki na publikację. Plik wektorowy (PDF) już jest – na stronie ostra wersja 1600 px.',
]
def board(pg):
    pairs = ''.join(f'<tr><td><span class="pair" style="color:{fh};background:{bh}">Aa</span></td><td>{fn} na: {bn}</td><td>{str(round(cr(fh, bh), 2)).replace(".", ",")}:1</td></tr>' for fn, fh, bn, bh in PAIRS)
    sw = ''.join(f'<li><span class="swatch" style="background:{h}"></span><b>{n}</b><span>{h} · {u}</span></li>' for n, h, u in SWATCHES)
    h1s = ''.join(f'<li{" class=chosen" if i == 0 else ""}><p class="h1-option">{t}</p><p>{why}</p></li>' for i, (t, why) in enumerate(H1_OPTIONS))
    return page_head('Plansze i&nbsp;brakujące materiały', 'Moduły w&nbsp;przerywanej ramce na stronach widać tylko w&nbsp;tym trybie (dopisz ?podglad=1, wyłącz: ?podglad=0).',
                     crumbs='<p class="group-h">Podgląd redakcyjny · nie publikować</p>') + f'''
    <section class="section-s"><div class="wrap board">
      <div class="board-row"><h2 class="block-h">Panel edycji</h2><div class="prose"><p>Teksty stron, specjalizacji, dane kontaktowe, media, filmy i&nbsp;artykuły Katarzyna zmienia sama w&nbsp;panelu <a href="{pg.u('admin/index.html')}">/admin/</a> (Decap CMS, logowanie DecapBridge). Zmiana trafia do repozytorium, a&nbsp;Netlify buduje stronę od nowa w&nbsp;1–2 minuty. Układ, kolory, zdjęcia i&nbsp;menu zostają w&nbsp;kodzie.</p></div></div>
      <div class="board-row"><h2 class="block-h">Wersja 9</h2><div class="prose"><ul>
        <li>Powrót do wersji 6 („publikacja”) na prośbę zamawiającej: portret na pierwszym ekranie, granat i&nbsp;amarant na jasnym tle, znaczniki kadru.</li>
        <li>Ilustracja rozmowy Hanny Jurewicz (dwie kobiety w&nbsp;fotelach) stoi w&nbsp;specjalizacjach: obok nagłówka „W&nbsp;czym mogę pomóc” na stronie głównej i&nbsp;w&nbsp;nagłówku strony Specjalizacje – w&nbsp;tym samym kadrze z&nbsp;narożników amarantu co portret. Wersja ostra, z&nbsp;pliku wektorowego, na przezroczystym tle. Bez podpisu przy obrazie; autorka wymieniona w&nbsp;stopce.</li>
        <li>Z&nbsp;briefu wersji 8 zostają treści i&nbsp;działanie: nowy opis przy specjalizacjach, cztery potwierdzone fakty w&nbsp;„O&nbsp;mnie”, formularz z&nbsp;trzema polami (imię, jedna droga kontaktu, temat) i&nbsp;przyciskiem „Poproś o&nbsp;kontakt”, stan wysyłania, błędy przy polach, potwierdzenie tylko po przyjęciu wiadomości, miejsce na informację o&nbsp;pierwszej rozmowie, bez pustych kafelków i&nbsp;próbnych opinii.</li></ul></div></div>
      <div class="board-row"><h2 class="block-h">Kierunek: publikacja</h2><div class="prose"><p>Strona złożona jak dobra publikacja: wyrazisty portret, świadoma typografia, uporządkowane kolumny i&nbsp;dużo powietrza. Kolor ma proporcje portretu – jasne tło, głęboki granat jak cień aksamitnej marynarki, amarant jak detal. Zieleń tła zostaje tylko na zdjęciu.</p>
        <ul><li>Jeden motyw: znaczniki kadru – cienkie narożniki w&nbsp;kolorze amarantu. Pochodzą ze zdania Katarzyny „Problem najczęściej tkwi w&nbsp;szczególe”: wyznaczają szczegół. Stoją przy portrecie, przy ilustracji rozmowy, przy nagłówkach sekcji, przy ikonie wskazanej specjalizacji i&nbsp;przy ramce „Warto wiedzieć”.</li>
        <li>Zniknęły ozdobniki, które ze sobą konkurowały: spinacz, przechylone zdjęcie, linie zeszytu, odręczne obrysy i&nbsp;podkreślenia, kropki spisu treści.</li>
        <li>Ruch tylko funkcjonalny: rozwijanie menu, stan wskazania, komunikaty formularza. Przy „ogranicz ruch” – bez animacji.</li></ul></div></div>
      <div class="board-row"><h2 class="block-h">Nagłówek pierwszego ekranu</h2><div><ol class="h1-options">{h1s}</ol></div></div>
      <div class="board-row"><h2 class="block-h">Redakcja tekstów</h2><div class="prose"><p>Fakty bez zmian; zmienione tylko sformułowania – do akceptacji Katarzyny:</p><ul>{''.join(f'<li>{x}</li>' for x in EDITS)}</ul></div></div>
      <div class="board-row"><h2 class="block-h">Kolor</h2><div><ul class="swatches">{sw}</ul><table class="contrast"><tbody>{pairs}</tbody></table></div></div>
      <div class="board-row"><h2 class="block-h">Typografia</h2><div class="prose"><p class="specimen-serif">Cormorant Garamond – tylko krótkie nagłówki i&nbsp;nazwy.</p><p>Hanken Grotesk – tekst, menu, formularz, etykiety. Skład według polskich zasad: spójniki jednoliterowe i&nbsp;półpauzy nie zostają na końcu wiersza, cudzysłowy „ ”. Kroje na licencji SIL OFL, odchudzone do polskiego alfabetu.</p></div></div>
      <div class="board-row"><h2 class="block-h">Ikony</h2><div><p class="board-note">Przedmioty, które ludzie przynoszą na rozmowę. Jedna siatka (32&nbsp;px), jedna grubość kreski (1,5&nbsp;px) w&nbsp;każdym rozmiarze. W&nbsp;umowie jeden zapis wzięty jest w&nbsp;znaczniki – szczegół w&nbsp;kadrze.</p><ul class="icon-board">{''.join(f'<li><span class="spec-ic"><svg aria-hidden="true"><use href="#ic-{x["slug"]}"/></svg></span>{x["name"]}</li>' for x in SPECS)}</ul></div></div>
      <div class="board-row"><h2 class="block-h">Znak</h2><div class="logos"><span class="logo-tile">{lockup()}</span><span class="logo-tile dark">{lockup('lockup-light')}</span>
        <span class="logo-tile sizes">{mark('kjk-mark s64')}{mark('kjk-mark s40')}{mark('kjk-mark s28')}{mark('kjk-mark s20')}</span></div></div>
      <div class="board-row"><h2 class="block-h">Brakuje</h2><ol class="missing">{''.join(f'<li>{m}</li>' for m in MISSING)}</ol></div>
      <div class="board-row"><h2 class="block-h">Podgląd modułów</h2><ul class="module-links">
        <li><a class="link" href="{pg.u('index.html')}?podglad=1">Strona główna</a></li><li><a class="link" href="{pg.u('o-mnie.html')}?podglad=1">O mnie</a></li>
        <li><a class="link" href="{pg.u(spec_url('spadki'))}?podglad=1">Podstrona specjalizacji</a></li><li><a class="link" href="{pg.u('kontakt.html')}?podglad=1">Kontakt</a></li>
        <li><a class="link" href="{pg.u('zasady-wynagradzania.html')}?podglad=1">Zasady wynagradzania</a></li><li><a class="link" href="{pg.u('blog.html')}?podglad=1">Blog i&nbsp;filmy</a></li>
        <li><a class="link" href="{pg.u('blog/wzor-artykulu.html')}">Szablon artykułu</a></li><li><a class="link" href="{pg.u('wspolpraca.html')}?podglad=1">Współpraca</a></li>
        <li><a class="link" href="{pg.u('polityka-prywatnosci.html')}?podglad=1">Polityka prywatności</a></li></ul></div>
    </div></section>'''

LD = {
    "@context": "https://schema.org", "@type": "LegalService",
    "name": "Kancelaria KJK – Katarzyna Jurewicz-Kupeć, Kancelaria Radcy Prawnego",
    "description": "Pomoc prawna dla osób prywatnych i firm.",
    "knowsAbout": [plain(x['name']) for x in SPECS],
    "founder": {"@type": "Person", "name": "Katarzyna Jurewicz-Kupeć", "jobTitle": "radca prawny",
                "memberOf": {"@type": "Organization", "name": "Okręgowa Izba Radców Prawnych we Wrocławiu"},
                "alumniOf": {"@type": "CollegeOrUniversity", "name": "Uniwersytet Wrocławski"},
                "award": "Pamiątkowy medal „Zasłużony dla Wymiaru Sprawiedliwości” (2011)"}}
if CONTACT['phone']: LD['telephone'] = CONTACT['phone']
if CONTACT['email']: LD['email'] = CONTACT['email']
if CONTACT['address']: LD['address'] = CONTACT['address']
HOME_HEAD = f'''
  <link rel="preload" href="img/kjk-portret.webp" as="image" type="image/webp" media="(min-width: 720px)" fetchpriority="high">
  <link rel="preload" href="img/kjk-portret-m.webp" as="image" type="image/webp" media="(max-width: 719px)" fetchpriority="high">
  <link rel="preload" href="fonts/cormorant-italic-pl.woff2" as="font" type="font/woff2" crossorigin>
  <script type="application/ld+json">{json.dumps(LD, ensure_ascii=False)}</script>'''

# ================================================================ zapis
write('index.html', 'Kancelaria KJK – Katarzyna Jurewicz-Kupeć, radca prawny',
      'Katarzyna Jurewicz-Kupeć, radca prawny. Pomoc prawna dla osób prywatnych i firm: rozwody, alimenty, spadki, umowy, windykacja, obsługa firm.', 'home', home, og=True, body_cls='home', extra=HOME_HEAD, icons=True)
write('o-mnie.html', 'O mnie – Katarzyna Jurewicz-Kupeć, radca prawny', 'Katarzyna Jurewicz-Kupeć, radca prawny: wykształcenie, aplikacja sądowa, własna praktyka od 2007 roku, bezpłatna pomoc prawna od 2010 roku.', 'about', about, og=True)
write('specjalizacje.html', 'Specjalizacje – Kancelaria KJK', 'Rozwody, alimenty, spadki, opiniowanie umów, windykacja, obsługa firm, reprezentacja wierzycieli w upadłości, prawo komunikacji elektronicznej.', 'spec', spec_overview, icons=True)
for s in SPECS:
    write(spec_url(s['slug']), f'{plain(s["name"])} – Kancelaria KJK', plain(s['lead']), 'spec', lambda pg, s=s: spec_page(pg, s), icons=True)
write('kontakt.html', 'Kontakt – Kancelaria KJK', 'Umów rozmowę z Katarzyną Jurewicz-Kupeć, radcą prawnym.', 'contact', contact)
write('zasady-wynagradzania.html', 'Zasady wynagradzania – Kancelaria KJK', 'Jak ustalane jest wynagrodzenie i z czego składa się koszt sprawy.', 'fees', fees)
write('wspolpraca.html', 'Współpraca – Kancelaria KJK', 'Osoby i organizacje współpracujące z Kancelarią KJK.', 'coop', coop, robots=True)
write('blog.html', 'Blog – Kancelaria KJK', 'Artykuły i filmy Katarzyny Jurewicz-Kupeć, radcy prawnego.', 'blog', blog, robots=not BLOG_LIVE)
for a in ARTICLES:
    write(f'blog/{a["slug"]}.html', f'{plain(a["title"])} – Blog Kancelarii KJK', plain(a['lead']), 'blog', lambda pg, a=a: article_html(pg, a))
write('blog/wzor-artykulu.html', 'Szablon artykułu – podgląd redakcyjny', 'Szablon pojedynczego artykułu.', 'blog',
      lambda pg: '<div class="tpl-bar pending" data-note="Szablon artykułu – podgląd redakcyjny, nie publikować"></div>' + article_html(pg, TEMPLATE, template=True), robots=True, always_demo=True)
write('polityka-prywatnosci.html', 'Polityka prywatności – Kancelaria KJK', 'Polityka prywatności strony Kancelarii KJK.', 'priv', privacy, robots=True)
write('404.html', 'Nie znaleziono strony – Kancelaria KJK', 'Nie znaleziono strony.', '', notfound, robots=True)
write('podglad.html', 'Podgląd redakcyjny – Kancelaria KJK', 'Plansze i brakujące materiały.', 'demo', board, robots=True, always_demo=True, icons=True)

open(os.path.join(OUT, 'img/favicon.svg'), 'w').write(
  f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120"><rect width="120" height="120" rx="16" fill="#1B2540"/>'
  f'<svg x="14" y="26" width="92" height="68" viewBox="{LOGO_VB}"><path fill="#FFFFFF" d="{LOGO["d"]}"/></svg></svg>')

# Media społecznościowe i filmy z panelu → js/config.js (czyta go js/main.js)
def youtube_id(v):
    v = (v or '').strip()
    m = re.search(r'(?:v=|youtu\.be/|/shorts/|/embed/|/live/)([A-Za-z0-9_-]{11})', v)
    return m.group(1) if m else (v if re.fullmatch(r'[A-Za-z0-9_-]{11}', v) else '')
CONFIG = {'social': {k: (USTAWIENIA.get(k) or '').strip() for k in ('instagram', 'youtube', 'facebook', 'linkedin')},
          'videos': [{'youtubeId': youtube_id(v.get('film')), 'title': (v.get('tytul') or '').strip(), 'description': (v.get('opis') or '').strip(),
                      'captions': bool(v.get('napisy')), 'transcript': (v.get('transkrypcja') or '').strip()}
                     for v in USTAWIENIA.get('filmy') or [] if youtube_id(v.get('film'))]}
open(os.path.join(OUT, 'js/config.js'), 'w', encoding='utf-8').write(
    '/* Plik tworzony przy budowaniu strony z tresci/ustawienia.json – zmieniaj w panelu edycji (Dane kontaktowe i media). */\n'
    'window.KJK_CONFIG = ' + json.dumps(CONFIG, ensure_ascii=False, indent=2) + ';\n')
print('ok · stron:', len(PAGES_WRITTEN), '· artykułów:', len(ARTICLES))
