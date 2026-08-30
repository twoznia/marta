# Przykładowy prompt do rozszerzenia Chrome (Maczfit → plan posiłków HTML)

Prompt do wklejenia w dodatku/agentcie w przeglądarce (np. na stronie panelu Maczfit),
który wygeneruje jeden plik HTML z planem posiłków dla wybranego zakresu dat.

---

wejdź w kalendarz od 2 do 21 września. po kliknięciu w datę po prawej stronie pojawi się 5 posiłków - śniadanie, 2 śniadanie, obiad, podwieczorek i kolacja. kliknij w każdy z nich w szczegóły posiłku. będzie tam zdjęcie, nazwa posiłku, krótki opis, kalorie, tłuszcze. białko i węglowodany potem skłądniki - skopiuj tę informację i utwórz mi plik html ze wszystkimi informacjami dla każdego dnia. wynik ma być w 1 pliku możliwy do otworzenia w przeglądarce.

---

Efekt takiego promptu to pliki w formacie `maczfit/maczfit-posilki-*.html`,
które parser `tools/parse-maczfit.js` scala do `maczfit/dania.json`.
