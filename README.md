# Kancelaria KJK – strona z panelem edycji tekstów

Strona: https://kjk-kancelaria.netlify.app · panel edycji: https://kjk-kancelaria.netlify.app/admin/

Wersja 9 („publikacja”: granat i amarant, portret na pierwszym ekranie, ilustracja rozmowy Hanny Jurewicz w specjalizacjach) z panelem, w którym Katarzyna sama zmienia teksty.

## Jak to działa

1. Katarzyna loguje się do panelu `/admin/` (Decap CMS, logowanie przez DecapBridge – Google, Microsoft albo hasło).
2. Zapisana zmiana („Publish”) trafia do tego repozytorium jako zmiana w pliku `tresci/*.json`.
3. Netlify widzi zmianę w repozytorium i buduje stronę od nowa (`netlify.toml`: `python3 narzedzia/build.py public`).
4. Po 1–2 minutach nowa wersja jest online.

## Foldery

```
tresci/                 teksty edytowane w panelu (JSON)
  strona-glowna.json      cytat, zdanie pod cytatem, fakty „O mnie”, kroki współpracy, zdanie w pasie kontaktu
  o-mnie.json             wstęp, części tekstu, zakończenie
  strona-specjalizacje.json   wstęp nad listą specjalizacji
  specjalizacje/*.json    8 specjalizacji: nazwa, krótki opis, wstęp, listy, „Warto wiedzieć”
  zasady-wynagradzania.json, kontakt.json, polityka-prywatnosci.json
  ustawienia.json         telefon, e-mail, adres, media społecznościowe, filmy
  blog/*.json             artykuły (dodawane w panelu)
narzedzia/build.py      szablony stron: układ, menu, stopka, ikony, kolejność i adresy specjalizacji
narzedzia/panel_config.py   tworzy strona/admin/config.yml (pola panelu)
strona/                 pliki kopiowane bez zmian: css/, js/main.js, img/, fonts/, admin/, _headers
netlify.toml            polecenie budowania, wersja Pythona, przełącznik formularza
requirements.txt        moduł markdown (treść artykułów i polityki prywatności)
```

`js/config.js` (media społecznościowe i filmy) powstaje przy budowaniu z `tresci/ustawienia.json` – nie edytuj go ręcznie.

## Co zmienia Katarzyna, a co projektant

- **Panel (Katarzyna):** wszystkie teksty stron i specjalizacji, dane kontaktowe, adresy mediów, filmy, artykuły, pełna treść polityki prywatności, informacja o pierwszej rozmowie i formach rozliczenia. W polach: `*słowo*` = kursywa, `**słowo**` = pogrubienie; w polach z akapitami każdy wiersz to akapit. Puste pole = element znika ze strony (np. „Warto wiedzieć”, „Pierwsza rozmowa”). Wpisany kod HTML wyświetla się jako zwykły tekst.
- **Kod (projektant):** układ, kolory, zdjęcia, menu, stopka, nagłówki sekcji, liczba, kolejność i adresy specjalizacji, formularz.

Twarde spacje po jednoliterowych spójnikach i przed półpauzą dokłada `typo()` w `build.py`.

## Budowanie na komputerze

```
pip3 install -r requirements.txt
python3 narzedzia/build.py public
python3 -m http.server -d public 8000      # podgląd: http://localhost:8000
```

Przed pracą w kodzie pobierz zmiany Katarzyny (`git pull`), po pracy wyślij swoje (`git push`).

## Przełączniki

- **Formularz kontaktowy:** `KJK_FORM_PROVIDER` w `netlify.toml`. `""` – formularz widoczny, ale nieaktywny (informacja nad polami). `"netlify"` – Netlify Forms; w panelu Netlify: Forms → Enable form detection, powiadomienia e-mail na adres Katarzyny; opublikuj politykę prywatności. Potwierdzenie wysyłki pokazuje się tylko wtedy, gdy usługa przyjmie wiadomość.
- **Blokada wyszukiwarek:** `strona/_headers` (`X-Robots-Tag: noindex`) – strona nie jest indeksowana. Usuń ten plik, gdy strona ma być widoczna w Google (najlepiej razem z domeną i danymi kontaktowymi).
- **Podgląd redakcyjny:** dopisz `?podglad=1` do adresu – widać miejsca czekające na materiały; plansze: `/podglad.html`.

## Panel – konfiguracja

- `strona/admin/config.yml` – pola panelu; sekcję `backend` wypełnia fragment z DecapBridge (Add site → config). Zmieniając pola, edytuj `narzedzia/panel_config.py` (wpisz tam też `BACKEND` z DecapBridge) i uruchom `python3 narzedzia/panel_config.py`.
- DecapBridge: repozytorium `kyukadesign/Kasia-Jurewicz` (https://github.com/kyukadesign/Kasia-Jurewicz), token GitHub (fine-grained, tylko to repozytorium, Contents: Read and write), adres logowania `https://kjk-kancelaria.netlify.app/admin/index.html`. Zaproszenia: Manage collaborators.

## Historia

Wcześniejsze wersje strony (v1–v9) i narzędzia testowe są w `~/Downloads/kjk-strona` (git, tagi) i `~/Downloads/kjk-strona-materialy/narzedzia`. Ten folder powstał z wersji 9 – strona zbudowana z `tresci/` jest identyczna (bajt w bajt) z wersją 9 opublikowaną 26.09.2026.
