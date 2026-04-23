const photoFiles = [
  // Wpisuj tutaj nazwy plików z katalogu /photos, np. "img_001.jpg"
  // "img_001.jpg",
  // "img_002.jpg",
  "t1.png","t2.png"
];

const gallery = document.getElementById('gallery');
const emptyState = document.getElementById('empty-state');
const readableName = (fileName) =>
  fileName
    .replace(/\.[^/.]+$/, '')
    .replace(/[_-]+/g, ' ')
    .trim();

if (photoFiles.length === 0) {
  emptyState.hidden = false;
} else {
  for (const fileName of photoFiles) {
    const card = document.createElement('figure');
    card.className = 'photo-card';

    const image = document.createElement('img');
    image.src = `photos/${fileName}`;
    image.alt = readableName(fileName) || 'Zdjęcie z galerii';
    image.loading = 'lazy';

    image.addEventListener('error', () => {
      card.remove();
      if (gallery.children.length === 0) {
        emptyState.hidden = false;
      }
    });

    const caption = document.createElement('figcaption');
    caption.textContent = fileName;

    card.append(image, caption);
    gallery.append(card);
  }
}
