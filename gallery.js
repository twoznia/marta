const photos = [
  {
    fileName: 't1.png',
    caption: 'Tomek w Innsbrucku.'
  },
  {
    fileName: 't2.png',
    caption: 'tomek z koniem w tle. Learning Days.'
  }
];

const gallery = document.getElementById('gallery');
const emptyState = document.getElementById('empty-state');
const readableName = (fileName) =>
  fileName
    .replace(/\.[^/.]+$/, '')
    .replace(/[_-]+/g, ' ')
    .trim();

if (photos.length === 0) {
  emptyState.hidden = false;
} else {
  for (const { fileName, caption: photoCaption } of photos) {
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
    caption.textContent = photoCaption;

    card.append(image, caption);
    gallery.append(card);
  }
}
