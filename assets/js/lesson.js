/**
 * Visualiseur de Leçon en Défilement Continu (Scroll Fluide)
 * Charte Graphique Nakôbio : Stepper visuel, repères d'étapes et encadré style carnet de croquis pour illustrations en attente.
 */

let courseData = null;

document.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const courseId = urlParams.get('course') || 'a1_cest_quoi_une_graine';
  
  loadLesson(courseId);
  setupPrintHandler();
});

async function loadLesson(courseId) {
  const container = document.getElementById('lesson-slides-container');
  try {
    const response = await fetch(`data/${courseId}.json`);
    if (!response.ok) {
      throw new Error(`Impossible de charger le cours "${courseId}". Fichier de données introuvable.`);
    }
    courseData = await response.json();
    renderLesson(courseData);
    setupScrollProgress(courseData.total_pages);
  } catch (err) {
    console.error(err);
    container.innerHTML = `
      <div style="text-align: center; padding: 4rem 1.5rem; background: #ffffff; border-radius: 20px; border: 1px solid var(--border-subtle); box-shadow: var(--shadow-card);">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🌱</div>
        <h2 style="color: var(--nakobio-green-deep); margin-bottom: 0.75rem; font-weight: 800;">Module en préparation</h2>
        <p style="color: var(--text-muted); max-width: 480px; margin: 0 auto 1.75rem; line-height: 1.6;">${err.message}</p>
        <a href="index.html" class="nav-back-link" style="display: inline-flex;">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
          <span>Retour au catalogue des formations</span>
        </a>
      </div>
    `;
  }
}

function renderLesson(data) {
  // Mise à jour de l'en-tête et du document
  document.title = `${data.title} — Formation Semences Paysannes Nakôbio`;
  document.getElementById('nav-course-title').textContent = data.title;
  document.getElementById('nav-category-tag').textContent = data.category || 'Semences Paysannes';

  // Hero d'introduction épuré et élégant
  const heroContainer = document.getElementById('lesson-hero');
  heroContainer.innerHTML = `
    <div class="module-hero-intro">
      <div class="hero-top-meta">
        <span class="hero-pill hero-pill-primary">🌱 ${data.category || 'Semences Paysannes'}</span>
        <span class="hero-pill">📖 ${data.total_pages} parties</span>
        <span class="hero-pill">☀️ Terroir tropical &amp; sahélien</span>
      </div>
      
      <h1 class="module-hero-title">${data.title}</h1>
      <p class="module-hero-summary">${data.summary || 'Guide pas à pas pour maîtriser la production et la sélection de semences paysannes saines.'}</p>

      <!-- Sommaire dépliable (fermé par défaut) -->
      <details class="lesson-quick-toc">
        <summary class="toc-summary-toggle">
          <span class="toc-summary-label">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
              <line x1="3" y1="6" x2="3.01" y2="6"></line>
              <line x1="3" y1="12" x2="3.01" y2="12"></line>
              <line x1="3" y1="18" x2="3.01" y2="18"></line>
            </svg>
            Sommaire des chapitres (${data.total_pages} parties)
          </span>
          <span class="toc-toggle-hint">Afficher / Masquer</span>
        </summary>
        <div class="toc-pills-list">
          ${data.pages.map(p => `
            <a href="#partie-${p.page_number}" class="toc-step-chip" title="Accéder à la partie ${p.page_number} : ${escapeHtml(p.title)}">
              <span class="toc-num">${p.page_number}</span>
              <span class="toc-title">${p.title}</span>
            </a>
          `).join('')}
        </div>
      </details>
    </div>
  `;

  // Rendu de chaque fiche thématique
  const slidesContainer = document.getElementById('lesson-slides-container');
  slidesContainer.innerHTML = '';

  data.pages.forEach((page, index) => {
    const slideEl = document.createElement('article');
    slideEl.className = 'slide-unit';
    slideEl.id = `partie-${page.page_number}`;

    const isFirstPages = index < 2;

    // Barre de repère claire et universelle (théorie comme pratique)
    const headerStepBar = `
      <div class="slide-step-header-bar">
        <div class="step-badge-circle">
          <span class="step-badge-num">${page.page_number}</span>
        </div>
        <div class="step-badge-meta">
          <span class="step-meta-label">PARTIE ${page.page_number} SUR ${data.total_pages}</span>
          <span class="step-meta-name">${escapeHtml(page.title)}</span>
        </div>
      </div>
    `;

    // Zone visuelle : image réelle ou écouteur onerror sécurisé
    const mediaWrapper = document.createElement('div');
    mediaWrapper.className = 'slide-visual-wrapper';

    const imgEl = document.createElement('img');
    imgEl.src = page.image;
    imgEl.alt = page.title;
    imgEl.loading = isFirstPages ? 'eager' : 'lazy';

    imgEl.addEventListener('error', () => {
      attachSketchBoard(mediaWrapper, page.illustration_description);
    });

    mediaWrapper.appendChild(imgEl);

    // Formatage du texte pédagogique
    const formattedText = formatPedagogicalText(page.text);

    const textEl = document.createElement('div');
    textEl.className = 'slide-body-text';
    textEl.innerHTML = `
      <h2 class="slide-step-title">${page.title}</h2>
      <div class="slide-pedagogical-content">
        ${formattedText}
      </div>
    `;

    slideEl.innerHTML = headerStepBar;
    slideEl.appendChild(mediaWrapper);
    slideEl.appendChild(textEl);
    slidesContainer.appendChild(slideEl);

    // Séparateur de transition épuré : passage direct à la partie suivante
    if (index < data.pages.length - 1) {
      const nextPage = data.pages[index + 1];
      const divider = document.createElement('div');
      divider.className = 'pedagogical-step-divider';
      divider.innerHTML = `
        <div class="divider-line"></div>
        <a href="#partie-${nextPage.page_number}" class="divider-milestone-link" title="Passer à la partie suivante">
          <span class="milestone-next-label">
            Partie suivante : <strong>${nextPage.page_number}. ${escapeHtml(nextPage.title)}</strong>
          </span>
          <span class="milestone-action-arrow" aria-hidden="true">➔</span>
        </a>
        <div class="divider-line"></div>
      `;
      slidesContainer.appendChild(divider);
    }
  });

  // Footer de fin de cours
  const footerContainer = document.getElementById('lesson-footer');
  footerContainer.innerHTML = `
    <div class="lesson-footer-completion">
      <div class="completion-icon">🌾</div>
      <h3 class="completion-title">Formation complétée avec succès !</h3>
      <p class="completion-desc">Vous avez parcouru l'ensemble des ${data.total_pages} parties de « ${data.title} ». Vous pouvez télécharger ce support au format PDF pour le terrain ou explorer un autre module.</p>
      <div class="completion-actions">
        <a href="index.html" class="nav-back-link">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
          <span>Retour au catalogue</span>
        </a>
        <button class="btn-print" onclick="window.print()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
          <span>Télécharger la version PDF</span>
        </button>
      </div>
    </div>
  `;
}

// Construction du cadre carnet de croquis pour illustration en attente
function attachSketchBoard(wrapper, desc) {
  const img = wrapper.querySelector('img');
  if (img) img.style.display = 'none';

  if (wrapper.querySelector('.sketch-placeholder-container')) return;

  const placeholderEl = document.createElement('div');
  placeholderEl.className = 'sketch-placeholder-container';
  placeholderEl.innerHTML = `
    <div class="sketch-board-frame">
      <div class="sketch-frame-top">
        <span class="sketch-type-badge">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 19l7-7 3 3-7 7-3-3z"></path>
            <path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"></path>
            <path d="M2 2l7.586 7.586"></path>
            <circle cx="11" cy="11" r="2"></circle>
          </svg>
          Croquis Pédagogique en Préparation
        </span>
      </div>

      <div class="sketch-desc-body">
        <div class="sketch-desc-title">Descriptif technique de l'illustration :</div>
        <blockquote class="sketch-desc-text">
          « ${desc ? desc.replace(/\n/g, '<br>') : 'Dessin technique de terrain illustrant les gestes clés et observations pratiques de cette étape.'} »
        </blockquote>
      </div>

      <div class="sketch-frame-bottom">
        <span class="sketch-author-note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="16" x2="12" y2="12"></line>
            <line x1="12" y1="8" x2="12.01" y2="8"></line>
          </svg>
          Illustration en cours de réalisation par l'équipe graphique
        </span>
        <span class="sketch-brand-watermark">NAKÔBIO ACADÉMIE</span>
      </div>
    </div>
  `;
  
  wrapper.appendChild(placeholderEl);
}

// Formatage du texte pédagogique
function formatPedagogicalText(rawText) {
  if (!rawText) return '<p><em>Contenu technique de l\'étape</em></p>';

  let html = rawText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  const lines = html.split('\n');
  let inList = false;
  let listType = 'ul';
  let formattedLines = [];

  for (let line of lines) {
    line = line.trim();
    if (!line) continue;

    if (line.startsWith('⚠️') || line.toLowerCase().startsWith('attention')) {
      if (inList) { formattedLines.push(`</${listType}>`); inList = false; }
      formattedLines.push(`<div class="slide-alert">${line}</div>`);
      continue;
    }

    const numMatch = line.match(/^(\d+)\.\s+(.*)/);
    if (numMatch) {
      if (!inList || listType !== 'ol') {
        if (inList) formattedLines.push(`</${listType}>`);
        formattedLines.push('<ol>');
        inList = true;
        listType = 'ol';
      }
      formattedLines.push(`<li>${numMatch[2]}</li>`);
      continue;
    }

    const bulletMatch = line.match(/^[-•]\s+(.*)/);
    if (bulletMatch) {
      if (!inList || listType !== 'ul') {
        if (inList) formattedLines.push(`</${listType}>`);
        formattedLines.push('<ul>');
        inList = true;
        listType = 'ul';
      }
      formattedLines.push(`<li>${bulletMatch[1]}</li>`);
      continue;
    }

    if (inList) {
      formattedLines.push(`</${listType}>`);
      inList = false;
    }
    formattedLines.push(`<p>${line}</p>`);
  }

  if (inList) {
    formattedLines.push(`</${listType}>`);
  }

  return formattedLines.join('\n');
}

// Jauge de lecture automatique selon le scroll et repères de jalons (3 à 5 steps)
function setupScrollProgress(totalPages) {
  const progressBar = document.getElementById('scroll-progress-bar');
  const progressContainer = document.querySelector('.scroll-progress-container');
  if (!progressBar || !progressContainer) return;

  // Création de 3 à 5 jalons bien espacés avec numéros sur la ligne
  if (totalPages && totalPages > 1) {
    progressContainer.querySelectorAll('.progress-tick').forEach(el => el.remove());
    const stepCount = totalPages <= 5 ? totalPages : (totalPages <= 8 ? 4 : 5);
    const milestones = [];
    for (let s = 0; s < stepCount; s++) {
      const pageIdx = Math.round((s / (stepCount - 1)) * (totalPages - 1));
      if (!milestones.some(m => m.idx === pageIdx)) {
        milestones.push({
          idx: pageIdx,
          pageNum: pageIdx + 1,
          posPercent: (s / (stepCount - 1)) * 100
        });
      }
    }

    milestones.forEach(m => {
      const tick = document.createElement('a');
      tick.className = `progress-tick ${m.idx === 0 ? 'active current' : ''}`;
      tick.href = `#partie-${m.pageNum}`;
      tick.title = `Partie ${m.pageNum}`;
      tick.style.left = `${m.posPercent}%`;
      tick.setAttribute('data-page-index', m.idx);
      tick.innerHTML = `<span class="step-tick-dot"></span>`;
      progressContainer.appendChild(tick);
    });
  }

  const activeStepNum = document.getElementById('active-step-num');
  const activeTotalSteps = document.getElementById('active-total-steps');
  if (activeTotalSteps && totalPages) {
    activeTotalSteps.textContent = totalPages;
  }

  function onScroll() {
    const totalHeight = document.documentElement.scrollHeight - window.innerHeight;
    if (totalHeight <= 0) return;
    const progress = (window.scrollY / totalHeight) * 100;
    progressBar.style.width = `${Math.min(100, Math.max(0, progress))}%`;

    // Détection de l'étape visible
    const steps = document.querySelectorAll('.slide-step-card');
    let currentIdx = 0;
    const trigger = window.innerHeight * 0.35;
    steps.forEach((step, idx) => {
      const rect = step.getBoundingClientRect();
      if (rect.top <= trigger) {
        currentIdx = idx;
      }
    });

    const newStep = currentIdx + 1;
    if (activeStepNum && activeStepNum.textContent !== String(newStep)) {
      activeStepNum.textContent = newStep;
      const readingBadge = document.getElementById('lesson-reading-progress');
      if (readingBadge) {
        readingBadge.classList.remove('step-changed');
        void readingBadge.offsetWidth;
        readingBadge.classList.add('step-changed');
      }
    }

    // Mise à jour des repères de jalons
    const ticks = Array.from(progressContainer.querySelectorAll('.progress-tick'));
    let foundCurrent = false;
    ticks.reverse().forEach((tick) => {
      const tickIdx = parseInt(tick.getAttribute('data-page-index') || '0', 10);
      if (tickIdx <= currentIdx) {
        tick.classList.add('active');
        if (!foundCurrent) {
          tick.classList.add('current');
          foundCurrent = true;
        } else {
          tick.classList.remove('current');
        }
      } else {
        tick.classList.remove('active', 'current');
      }
    });
    if (!foundCurrent && ticks[ticks.length - 1]) {
      ticks[ticks.length - 1].classList.add('active', 'current');
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();
}

function setupPrintHandler() {
  const btn = document.getElementById('btn-print-lesson');
  if (btn) {
    btn.addEventListener('click', () => {
      window.print();
    });
  }
}

function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}
