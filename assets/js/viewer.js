let currentModule = null;
let currentPageIndex = 0;

// Charger les données du cours
async function loadCourse(dataFile = 'data/b14_carotte.json') {
  try {
    const response = await fetch(dataFile);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    currentModule = await response.json();
    initApp();
  } catch (err) {
    console.error("Erreur de chargement du cours :", err);
    document.getElementById('slide-viewport').innerHTML = `
      <div style="padding: 2rem; text-align: center; color: #dc2626;">
        <h3>Impossible de charger le module de formation</h3>
        <p>${err.message}</p>
      </div>
    `;
  }
}

function initApp() {
  document.getElementById('module-title').textContent = currentModule.title;
  document.getElementById('total-pages').textContent = currentModule.total_pages;

  renderCurrentSlide();
  renderPrintPages();
  setupEventListeners();
}

function renderCurrentSlide() {
  if (!currentModule || !currentModule.pages.length) return;

  const page = currentModule.pages[currentPageIndex];
  const viewport = document.getElementById('slide-viewport');

  // Mettre à jour l'indicateur
  document.getElementById('current-page-num').textContent = page.page_number;
  const progressPercent = ((currentPageIndex + 1) / currentModule.total_pages) * 100;
  document.getElementById('progress-bar').style.width = `${progressPercent}%`;

  // Mettre à jour les boutons Précédent / Suivant
  document.getElementById('btn-prev').disabled = currentPageIndex === 0;
  document.getElementById('btn-next').disabled = currentPageIndex === currentModule.pages.length - 1;

  viewport.innerHTML = `
    <article class="slide-card slide-layout-landscape">
      <div class="slide-media">
        <img src="${page.image}" alt="${page.title}" id="slide-img" onerror="this.onerror=null; this.src='assets/images/placeholder-seed.svg'">
      </div>
      <div class="slide-content">
        <div class="slide-header">
          <span class="slide-step">Étape ${page.page_number} / ${currentModule.total_pages}</span>
        </div>
        <h2 class="slide-title">${page.title}</h2>
        <div class="slide-text">${formatMarkdownText(page.text)}</div>
      </div>
    </article>
  `;
}

// Préparer l'ensemble des pages pour l'impression / export PDF complet
function renderPrintPages() {
  let printContainer = document.getElementById('print-container');
  if (!printContainer) {
    printContainer = document.createElement('div');
    printContainer.id = 'print-container';
    printContainer.className = 'print-only';
    document.body.appendChild(printContainer);
  }

  printContainer.innerHTML = currentModule.pages.map(page => `
    <div class="print-page">
      <div class="print-page-media">
        <img src="${page.image}" alt="${page.title}" onerror="this.src='assets/images/b14_carotte/page_01.jpg'">
      </div>
      <div class="print-page-content">
        <div class="print-step">Module ${currentModule.title} — Page ${page.page_number}/${currentModule.total_pages}</div>
        <h2 class="print-title">${page.title}</h2>
        <div class="print-text">${formatMarkdownText(page.text)}</div>
      </div>
    </div>
  `).join('');
}

function formatMarkdownText(rawText) {
  if (!rawText) return "";
  let formatted = rawText
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n- (.*)/g, '<br>• $1')
    .replace(/\n(\d+)\. (.*)/g, '<br><strong>$1.</strong> $2')
    .replace(/\n\n/g, '<br><br>');

  return formatted;
}

function nextPage() {
  if (currentPageIndex < currentModule.pages.length - 1) {
    currentPageIndex++;
    renderCurrentSlide();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function prevPage() {
  if (currentPageIndex > 0) {
    currentPageIndex--;
    renderCurrentSlide();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }
}

function toggleLayoutMode() {
  const card = document.querySelector('.slide-card');
  if (card) {
    card.classList.toggle('slide-layout-landscape');
  }
}

function exportPdf() {
  window.print();
}

function setupEventListeners() {
  document.getElementById('btn-next').addEventListener('click', nextPage);
  document.getElementById('btn-prev').addEventListener('click', prevPage);
  document.getElementById('btn-pdf').addEventListener('click', exportPdf);

  const toggleBtn = document.getElementById('btn-toggle-layout');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', toggleLayoutMode);
  }

  // Clavier
  window.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowRight' || e.key === ' ') {
      nextPage();
    } else if (e.key === 'ArrowLeft') {
      prevPage();
    }
  });

  // Tactile (swipe)
  let touchStartX = 0;
  window.addEventListener('touchstart', (e) => {
    touchStartX = e.changedTouches[0].screenX;
  }, false);

  window.addEventListener('touchend', (e) => {
    let touchEndX = e.changedTouches[0].screenX;
    if (touchStartX - touchEndX > 50) {
      nextPage();
    }
    if (touchEndX - touchStartX > 50) {
      prevPage();
    }
  }, false);
}

document.addEventListener('DOMContentLoaded', () => {
  loadCourse();
});
