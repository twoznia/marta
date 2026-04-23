# marta

Prosta galeria zdjęć pod GitHub Pages (`github.io`).

## Struktura repozytorium

- `index.html` – strona galerii
- `style.css` – styl strony
- `gallery.js` – lista zdjęć do wyświetlenia
- `photos/` – tutaj wrzucasz swoje zdjęcia

## Jak dodać zdjęcia

1. Skopiuj zdjęcia do katalogu `photos/` (np. `photos/001.jpg`, `photos/002.jpg`).
2. Otwórz `gallery.js` i uzupełnij tablicę `photoFiles`, np.:

```js
const photoFiles = [
  "001.jpg",
  "002.jpg",
  "003.jpg"
];
```

3. Zacommituj zmiany do repozytorium.

## Jak opublikować na GitHub Pages (`github.io`)

1. Wejdź w repozytorium na GitHub.
2. `Settings` → `Pages`.
3. W sekcji **Build and deployment** ustaw:
   - **Source**: `Deploy from a branch`
   - **Branch**: `main` (lub gałąź, z której publikujesz), folder `/ (root)`
4. Zapisz ustawienia.
5. Po chwili strona będzie dostępna pod adresem:
   - `https://twoznia.github.io/marta/`

## Kolejne kroki (praktycznie)

1. Dodaj kilkadziesiąt zdjęć do `photos/`.
2. Dopisz wszystkie nazwy plików w `gallery.js`.
3. Wypchnij zmiany do GitHub.
4. Otwórz opublikowany link i sprawdź galerię.
