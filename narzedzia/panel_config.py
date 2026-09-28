# -*- coding: utf-8 -*-
"""Tworzy strona/admin/config.yml (Decap CMS) i strona/admin/index.html. Pola po polsku, z podpowiedziami dla Katarzyny.
Uruchom po zmianie pól:  python3 narzedzia/panel_config.py   (sekcję backend z DecapBridge wpisz w BACKEND poniżej)."""
import json, os

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # katalog repozytorium
SITE = 'https://kjk-kancelaria.netlify.app'
MD_BUTTONS = ['bold', 'italic', 'link', 'heading-two', 'heading-three', 'bulleted-list', 'numbered-list', 'quote']
KURSYWA = 'Słowo w gwiazdkach (*słowo*) będzie kursywą, w podwójnych (**słowo**) – pogrubione.'

def f(label, name, widget='string', **kw):
    d = {'label': label, 'name': name, 'widget': widget}
    d.update(kw)
    return d

def lista_obiektow(label, name, pola, summary='{{fields.tytul}}', **kw):
    return f(label, name, 'list', summary=summary, fields=pola, **kw)

def lista_punktow(label, name, **kw):
    return f(label, name, 'list', field=f('Punkt', 'punkt', 'text'), **kw)

TYTUL_OPIS = [f('Tytuł', 'tytul'), f('Opis', 'opis', 'text')]
SPECS = [('rozwody', 'Rozwody'), ('alimenty', 'Alimenty'), ('spadki', 'Spadki'), ('opiniowanie-umow', 'Opiniowanie umów'),
         ('windykacja', 'Windykacja'), ('obsluga-firm', 'Obsługa podmiotów gospodarczych'),
         ('upadlosc-wierzyciele', 'Reprezentacja wierzycieli w postępowaniach upadłościowych'),
         ('komunikacja-elektroniczna', 'Prawo komunikacji elektronicznej')]
CATS = [('rodzina', 'Rodzina'), ('spadki', 'Spadki'), ('umowy', 'Umowy'), ('naleznosci', 'Należności i upadłość'),
        ('firma', 'Firma'), ('komunikacja', 'Komunikacja elektroniczna')]
SPEC_FIELDS = [
    f('Nazwa', 'nazwa', hint='Nazwa w menu, na liście specjalizacji, w stopce i w nagłówku tej strony.'),
    f('Krótki opis', 'krotki_opis', 'text', hint='Jedno zdanie pod nazwą na liście specjalizacji.'),
    f('Wstęp', 'wstep', 'text', hint='Pod nagłówkiem strony tej specjalizacji.'),
    lista_punktow('Kiedy warto się zgłosić', 'kiedy', label_singular='punkt'),
    lista_punktow('Jak mogę pomóc', 'pomoc', label_singular='punkt'),
    lista_punktow('Co przygotować na rozmowę', 'przygotuj', label_singular='punkt'),
    f('Warto wiedzieć (ramka)', 'warto_wiedziec', 'text', required=False, hint='Puste – ramka nie pokazuje się na stronie.'),
]
DATE = dict(format='YYYY-MM-DD', date_format='DD.MM.YYYY', time_format=False, picker_utc=True)

config = {
    'locale': 'pl',
    'site_url': SITE,
    'display_url': SITE,
    'logo_url': '/img/apple-touch-icon.png',
    'media_folder': 'strona/img/wgrane',
    'public_folder': '/img/wgrane',
    'slug': {'encoding': 'ascii', 'clean_accents': True, 'sanitize_replacement': '-'},
    'collections': [
        {'name': 'strony', 'label': 'Strony', 'label_singular': 'strona',
         'description': 'Teksty stron. Po kliknięciu „Publish” zmiana jest na stronie po 1–2 minutach. ' + KURSYWA,
         'editor': {'preview': False},
         'files': [
             {'name': 'strona-glowna', 'label': 'Strona główna', 'file': 'tresci/strona-glowna.json', 'preview_path': '', 'fields': [
                 f('Cytat na pierwszym ekranie', 'cytat', 'text', hint='Bez cudzysłowu – strona dodaje go sama. ' + KURSYWA),
                 f('Zdanie pod cytatem', 'zdanie', 'text', hint='Komu i w czym pomagam.'),
                 f('Podpis pod zdjęciem', 'podpis_zdjecia'),
                 f('„W czym mogę pomóc” – opis', 'specjalizacje_opis', 'text'),
                 f('„O mnie” – zdanie', 'o_mnie_zdanie', 'text'),
                 lista_obiektow('„O mnie” – fakty', 'o_mnie_fakty', TYTUL_OPIS, label_singular='fakt', min=1, max=6,
                                hint='Najlepiej 4 – układają się w dwie kolumny.'),
                 f('„Jak zaczynamy współpracę” – opis', 'wspolpraca_opis', 'text', hint='Link „Zasady wynagradzania” strona dodaje sama.'),
                 lista_obiektow('„Jak zaczynamy współpracę” – kroki', 'wspolpraca_kroki', TYTUL_OPIS, label_singular='krok', min=1, max=6,
                                hint='Najlepiej 4. Te same kroki są też na stronie Specjalizacje.'),
                 f('„Kontakt” – zdanie na dole strony', 'kontakt_zdanie', 'text'),
             ]},
             {'name': 'o-mnie', 'label': 'O mnie', 'file': 'tresci/o-mnie.json', 'preview_path': 'o-mnie.html', 'fields': [
                 f('Wstęp (duża czcionka)', 'wstep', 'text'),
                 f('Podpis pod zdjęciem', 'podpis_zdjecia'),
                 lista_obiektow('Części tekstu', 'sekcje', [f('Tytuł części', 'tytul'), f('Treść', 'tresc', 'text', hint='Każdy wiersz to osobny akapit.')],
                                label_singular='część'),
                 f('Zdanie na zakończenie', 'zakonczenie', 'text', required=False),
                 f('Poza kancelarią', 'poza_kancelaria', required=False),
             ]},
             {'name': 'strona-specjalizacje', 'label': 'Specjalizacje – wstęp nad listą', 'file': 'tresci/strona-specjalizacje.json',
              'preview_path': 'specjalizacje.html', 'fields': [f('Wstęp', 'wstep', 'text')]},
             {'name': 'zasady-wynagradzania', 'label': 'Zasady wynagradzania', 'file': 'tresci/zasady-wynagradzania.json',
              'preview_path': 'zasady-wynagradzania.html', 'fields': [
                 f('Wstęp', 'wstep', 'text'),
                 lista_obiektow('„Jak to ustalamy” – kroki', 'kroki', TYTUL_OPIS, label_singular='krok'),
                 f('Formy rozliczenia', 'formy_rozliczenia', 'list', required=False, label_singular='forma',
                   field=f('Forma rozliczenia', 'forma'), hint='Puste – lista nie pokazuje się na stronie.'),
                 lista_obiektow('„Z czego składa się koszt sprawy”', 'koszty', [f('Nazwa', 'nazwa'), f('Opis', 'opis', 'text')],
                                summary='{{fields.nazwa}}', label_singular='pozycja'),
                 f('Inne wydatki (np. tłumaczenia, dojazdy)', 'inne_wydatki', 'text', required=False,
                   hint='Puste – pozycja nie pokazuje się na stronie.'),
             ]},
             {'name': 'kontakt', 'label': 'Kontakt', 'file': 'tresci/kontakt.json', 'preview_path': 'kontakt.html', 'fields': [
                 f('Wstęp', 'wstep', 'text'),
                 lista_obiektow('„Co dzieje się po kontakcie”', 'po_kontakcie', TYTUL_OPIS, label_singular='krok'),
                 f('Pierwsza rozmowa', 'pierwsza_rozmowa', 'text', required=False,
                   hint='Np. forma (telefon, spotkanie, online), czas trwania, koszt. Puste – informacja nie pokazuje się na stronie.'),
                 f('Zdanie nad formularzem', 'formularz_wstep'),
             ]},
             {'name': 'polityka-prywatnosci', 'label': 'Polityka prywatności', 'file': 'tresci/polityka-prywatnosci.json',
              'preview_path': 'polityka-prywatnosci.html', 'fields': [
                 f('Treść polityki prywatności', 'tresc', 'markdown', required=False, buttons=MD_BUTTONS, editor_components=[], modes=['rich_text'],
                   hint='Puste – na stronie zostaje informacja, że pełna treść zostanie opublikowana. Część „Jak działa ta strona” strona dodaje sama.'),
             ]},
             {'name': 'ustawienia', 'label': 'Dane kontaktowe i media', 'file': 'tresci/ustawienia.json', 'preview_path': 'kontakt.html', 'fields': [
                 f('Telefon', 'telefon', required=False, hint='Np. +48 600 700 800 – na stronie będzie klikalny. Pokaże się na pierwszym ekranie, w kontakcie i w stopce.'),
                 f('E-mail', 'email', required=False),
                 f('Adres kancelarii', 'adres', required=False),
                 f('Instagram – pełny adres profilu', 'instagram', required=False, hint='Zaczyna się od https://. Puste – ikona się nie pokazuje.'),
                 f('YouTube – pełny adres kanału', 'youtube', required=False, hint='Zaczyna się od https://. Puste – ikona się nie pokazuje.'),
                 f('Facebook – pełny adres', 'facebook', required=False),
                 f('LinkedIn – pełny adres', 'linkedin', required=False),
                 lista_obiektow('Filmy (strona Blog)', 'filmy', [
                     f('Link do filmu na YouTube', 'film', hint='Skopiuj adres filmu z przeglądarki, np. https://www.youtube.com/watch?v=…'),
                     f('Tytuł', 'tytul'),
                     f('Krótki opis', 'opis', 'text', required=False),
                     f('Film ma napisy', 'napisy', 'boolean', default=False, required=False),
                     f('Transkrypcja', 'transkrypcja', 'text', required=False, hint='Akapity oddziel pustym wierszem.'),
                 ], required=False, label_singular='film'),
             ]},
         ]},
        {'name': 'specjalizacje', 'label': 'Specjalizacje', 'label_singular': 'specjalizacja',
         'description': 'Osiem specjalizacji. Kolejność, adresy stron i ikony zmienia projektant. ' + KURSYWA,
         'editor': {'preview': False},
         'files': [{'name': slug, 'label': label, 'file': f'tresci/specjalizacje/{slug}.json',
                    'preview_path': f'specjalizacje/{slug}.html', 'fields': SPEC_FIELDS} for slug, label in SPECS]},
        {'name': 'blog', 'label': 'Blog – artykuły', 'label_singular': 'artykuł',
         'description': 'Artykuły są na stronie Blog, a trzy najnowsze także na stronie głównej. Pierwszy opublikowany artykuł włącza „Blog” w menu. '
                        'Zaznacz „Szkic”, żeby zapisać tekst bez pokazywania go na stronie.',
         'folder': 'tresci/blog', 'create': True, 'extension': 'json', 'format': 'json', 'slug': '{{slug}}',
         'identifier_field': 'tytul', 'summary': '{{tytul}}', 'sortable_fields': ['data', 'tytul'],
         'preview_path': 'blog/{{slug}}.html',
         'fields': [
             f('Tytuł', 'tytul'),
             f('Data publikacji', 'data', 'datetime', **DATE),
             f('Kategoria', 'kategoria', 'select', options=[{'label': l, 'value': v} for v, l in CATS]),
             f('Powiązana specjalizacja', 'specjalizacja', 'select', options=[{'label': l, 'value': v} for v, l in SPECS],
               hint='Pod artykułem pojawi się link do tej specjalizacji i przycisk „Zapytaj o swoją sprawę”.'),
             f('Wstęp', 'wstep', 'text', hint='1–2 zdania: czego dotyczy artykuł i dla kogo jest. Pokazuje się też na liście artykułów.'),
             f('Treść', 'tresc', 'markdown', buttons=MD_BUTTONS, editor_components=[], modes=['rich_text'],
               hint='Śródtytuły: przycisk „Heading 2”. Tekst ma charakter informacyjny – zastrzeżenie strona dodaje sama.'),
             f('Data aktualizacji', 'aktualizacja', 'datetime', required=False, hint='Tylko gdy treść naprawdę się zmieniła.', **DATE),
             f('Szkic – nie pokazuj jeszcze na stronie', 'szkic', 'boolean', default=False, required=False),
         ]},
    ],
}

def y(v, ind=0):
    """Mały zapis YAML: napisy w cudzysłowie (składnia JSON jest poprawnym YAML), klucze bez cudzysłowu."""
    sp = '  ' * ind
    if isinstance(v, dict):
        if not v:
            return ' {}'
        out = ''
        for k, x in v.items():
            if isinstance(x, (dict, list)) and x:
                out += f'\n{sp}{k}:' + y(x, ind + 1)
            else:
                out += f'\n{sp}{k}:' + y(x, ind + 1)
        return out
    if isinstance(v, list):
        if not v:
            return ' []'
        out = ''
        for x in v:
            if isinstance(x, dict) and x:
                body = y(x, ind + 1).lstrip('\n')
                out += f'\n{sp}- ' + body[len('  ' * (ind + 1)):]
            else:
                out += f'\n{sp}-' + y(x, ind + 1)
        return out
    if isinstance(v, bool):
        return ' true' if v else ' false'
    if isinstance(v, (int, float)):
        return f' {v}'
    return ' ' + json.dumps(v, ensure_ascii=False)

BACKEND = '''backend:
  # ZASTĄP ten fragment kodem, który pokaże DecapBridge po dodaniu strony (Add site). Zostaw resztę pliku bez zmian.
  name: git-gateway
  repo: NAZWA-KONTA/kjk-kancelaria
  branch: main
  identity_url: https://auth.decapbridge.com/sites/ID-STRONY
  gateway_url: https://gateway.decapbridge.com
'''
text = ('# Panel edycji treści strony Kancelarii KJK: https://kjk-kancelaria.netlify.app/admin/\n'
        '# Decap CMS (https://decapcms.org) + logowanie DecapBridge (https://decapbridge.com).\n'
        '# Pola odpowiadają plikom tresci/*.json; strona buduje się z nich po każdej zmianie (narzedzia/build.py).\n'
        '# Plik tworzy skrypt panel_config.py – przy zmianie pól łatwiej go wygenerować ponownie niż poprawiać ręcznie.\n\n'
        + BACKEND + y(config).lstrip('\n') + '\n')
os.makedirs(os.path.join(R, 'strona/admin'), exist_ok=True)
open(os.path.join(R, 'strona/admin/config.yml'), 'w', encoding='utf-8').write(text)

open(os.path.join(R, 'strona/admin/index.html'), 'w', encoding='utf-8').write('''<!doctype html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex">
  <title>Panel edycji – Kancelaria KJK</title>
  <link rel="icon" href="/img/favicon.svg" type="image/svg+xml">
</head>
<body>
  <!-- Decap CMS: ustawienia i pola w config.yml obok tego pliku -->
  <script src="https://unpkg.com/decap-cms@^3.0.0/dist/decap-cms.js"></script>
</body>
</html>
''')
print('ok', len(text), 'znaków')
