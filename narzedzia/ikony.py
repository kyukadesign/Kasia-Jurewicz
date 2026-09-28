# -*- coding: utf-8 -*-
"""Ikony specjalizacji KJK – wersja 6: precyzyjne ikony liniowe, jedna siatka i jedna grubość kreski.
Przedmioty, które ludzie przynoszą na rozmowę: obrączki, rysunek dziecka, klucz, umowa z zaznaczonym zapisem,
wezwanie do zapłaty, pieczątka, lista wierzytelności, telefon. Bez młotków i wag.
viewBox 0 0 32 32; kreska ustawiana w CSS (stroke-width), niezależna od rozmiaru (vector-effect).
Uruchom:  python3 ikony.py arkusz.html  (arkusz do oceny)."""

def _el(tag, **a):
    attrs = ' '.join(f'{k.replace("_", "-")}="{v}"' for k, v in a.items())
    return f'<{tag} {attrs} vector-effect="non-scaling-stroke"/>'

def P(d): return _el('path', d=d)
def C(cx, cy, r): return _el('circle', cx=cx, cy=cy, r=r)
def R(x, y, w, h, rx=0): return _el('rect', x=x, y=y, width=w, height=h, rx=rx)

ICONS = {
    # obrączki, które się rozeszły
    'rozwody': C(10, 19.5, 6) + C(10, 19.5, 4.2) + C(22, 12.5, 6) + C(22, 12.5, 4.2),
    # rysunek dziecka: kartka, domek, słońce
    'alimenty': R(5, 4, 22, 24, 1.5) + P('M9.5 23.5v-5.5l5-4.2 5 4.2v5.5z') + P('M13 23.5v-3h3v3') + C(21.5, 9.5, 1.9),
    # stary klucz
    'spadki': C(9.5, 16, 5.5) + C(9.5, 16, 1.7) + P('M15 16h14M24.5 16v4M28 16v3'),
    # umowa, w której jeden zapis wzięty jest w znaczniki – szczegół w kadrze
    'opiniowanie-umow': P('M8 3.5h11l6 6v19H8z') + P('M19 3.5v6h6') + P('M11.5 12.5h8M11.5 25h6') + P('M12.5 18.75h7.5') +
                        P('M10.5 17.5v-2h2M22 20v2h-2'),
    # wezwanie do zapłaty: koperta i moneta
    'windykacja': R(3.5, 12.5, 18, 13, 1) + P('M3.5 13.5l9 6.5 9-6.5') + C(24.5, 9, 4.5) + C(24.5, 9, 2.3),
    # pieczątka firmowa i jej odcisk
    'obsluga-firm': C(16, 6.5, 3) + P('M14.4 9.2l-.9 5.3M17.6 9.2l.9 5.3') + R(8, 14.5, 16, 4.5, 1) + P('M6.5 19h19') +
                    P('M7 25h18M7 28h11'),
    # lista wierzytelności na podkładce
    'upadlosc-wierzyciele': R(7, 5.5, 18, 23.5, 1.5) + R(12, 3.5, 8, 4, 1) + P('M10.5 13.5l1.5 1.5 3-3M17.5 13.5h4.5') +
                            P('M10.5 20l1.5 1.5 3-3M17.5 20h4.5M17.5 25.5h4.5M11 25.5h3.5'),
    # telefon i zasięg
    'komunikacja-elektroniczna': R(7.5, 3.5, 12, 25, 2) + P('M12 7h3') + C(13.5, 24.5, 1) + P('M22.5 10.5a5 5 0 0 1 0 7M25.5 7.5a9.5 9.5 0 0 1 0 13'),
}

def symbols():
    return ''.join(f'<symbol id="ic-{k}" viewBox="0 0 32 32">{v}</symbol>' for k, v in ICONS.items())

if __name__ == '__main__':
    import sys
    sizes = (24, 32, 48, 96)
    def cell(k, s): return f'<svg style="width:{s}px;height:{s}px" viewBox="0 0 32 32"><use href="#ic-{k}"/></svg>'
    rows = ''.join('<div class="row">' + ''.join(cell(k, s) for s in sizes) + f'<span>{k}</span></div>' for k in ICONS)
    html = f'''<!doctype html><meta charset="utf-8"><style>
    body{{margin:0;padding:24px;background:#FAF8F5;font:13px sans-serif;color:#555B6E}}
    .row{{display:flex;align-items:end;gap:22px;margin-bottom:14px}}
    svg{{fill:none;stroke:#1B2540;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}}
    </style><svg width="0" height="0" style="position:absolute"><defs>{symbols()}</defs></svg>{rows}'''
    open(sys.argv[1], 'w').write(html)
    print('ok')
