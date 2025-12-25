// Common functions for the PT Alternative project

// Variable for the slider
var divisor;
var colunaEsquerda;
var colunaDireita;
let isDragging = false;
let startX;
let initialLeftWidth;
let initialRightWidth;

// Variables for the comboTrack
var combobox;
var datalist;
const MAX_ITEMS = 25;


// Get the anchor from the URL
function getAnchor(url) {
  try {
    const urlObj = new URL(url);
    return urlObj.hash.substring(1); // Remove o # inicial
  } catch (error) {
    return null;
  }
}

// Verify if we have an anchor in the current URL
function hasAnchor() {
  const currentUrl = window.location.href;
  const hasHash = currentUrl.indexOf('#') !== -1;
  return hasHash;
}

// Find an anchor by name
function findAnchorByName(anchorName) {
  const anchors = document.querySelectorAll(`a[name="${anchorName}"]`);
  return anchors; // Returns a NodeList (can have zero, one, or multiple elements)
}

// Work with the first initial data loaded
function LoadStartPage() {
  var page_name = getCookie("PAGE");
  if (page_name) {
    open_page(page_name)
  }
}

// Open a page from top menu
function open_page(page_name) {
  window.location.href = page_name + ".html";
  setCookie("PAGE", page_name, 180)
}


function generate_url(paper, section, paragraph) {
  const protocol = window.location.protocol;
  const currentDomain = window.location.hostname;
  const currentPage = window.location.pathname;

  if (!Number.isInteger(paper) || !Number.isInteger(section) || !Number.isInteger(paragraph)) {
    const fullUrl = `${protocol}//${currentDomain}/${currentPage}`;
    return fullUrl;
  }

  setCookie("paper", paper, 180)
  setCookie("section", section, 180)
  setCookie("paragraph", paragraph, 180)
  hash = `p${paper.toString().padStart(3, '0')}_${section.toString().padStart(3, '0')}_${paragraph.toString().padStart(3, '0')}`;
  const fullUrl = `${protocol}//${currentDomain}/${currentPage}#${hash}`;
  return fullUrl;
}

// Open the local edit modal
function generateUrlAndOpen(codeString) {
  const parts = codeString.split(/[:.-]/);

  if (parts.length < 3) return;

  const paper = parts[0];
  const section = parts[1];
  const paragraph = parts[2];

  // Find the Portuguese Text in DOM
  // We use the English ID (pPPP_SSS_PPP) to find the row
  const id_str = `p${paper.padStart(3, '0')}_${section.padStart(3, '0')}_${paragraph.padStart(3, '0')}`;
  const div_en = document.getElementById(id_str);

  let currentText = "";

  if (div_en) {
    const tr = div_en.closest('tr');
    const cells = tr.querySelectorAll('td');
    if (cells.length > 1) {
      const div_pt = cells[1].querySelector('div');
      // Clone to avoid modifying DOM while reading
      const clone = div_pt.cloneNode(true);
      const anchor = clone.querySelector('a');
      if (anchor) anchor.remove();
      currentText = clone.textContent.trim();
    }
  } else {
    console.warn("Could not find paragraph element for " + id_str);
    // Try to find by generic class or just let empty?
    // If the user clicked the link, the element SHOULD be there.
  }

  // Set Modal Values
  document.getElementById('editPaper').value = paper;
  document.getElementById('editSection').value = section;
  document.getElementById('editParagraph').value = paragraph;
  document.getElementById('editText').value = currentText;

  // Show Modal
  const modalEl = document.getElementById('editModal');
  const modal = new bootstrap.Modal(modalEl);
  modal.show();
}

async function saveParagraph() {
  const paper = document.getElementById('editPaper').value;
  const section = document.getElementById('editSection').value;
  const paragraph = document.getElementById('editParagraph').value;
  const text = document.getElementById('editText').value;

  try {
    const response = await fetch('/save_paragraph', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        paper: parseInt(paper),
        section: parseInt(section),
        paragraph: parseInt(paragraph),
        text: text
      })
    });

    if (response.ok) {
      // Update DOM immediately
      const id_str = `p${paper.padStart(3, '0')}_${section.padStart(3, '0')}_${paragraph.padStart(3, '0')}`;
      const div_en = document.getElementById(id_str);
      if (div_en) {
        const tr = div_en.closest('tr');
        const cells = tr.querySelectorAll('td');
        if (cells.length > 1) {
          const div_pt = cells[1].querySelector('div');
          const anchor = div_pt.querySelector('a');
          div_pt.innerHTML = "";
          if (anchor) div_pt.appendChild(anchor);
          div_pt.append(" " + text);
        }
      }

      // Hide modal
      const modalEl = document.getElementById('editModal');
      const modal = bootstrap.Modal.getInstance(modalEl);
      modal.hide();
    } else {
      const err = await response.json();
      alert("Erro ao salvar: " + (err.error || "Desconhecido"));
    }
  } catch (e) {
    alert("Erro de conexão: " + e);
  }
}

async function performSearch() {
  // Try to find input in the modal first
  let query = "";
  const modalInput = document.getElementById('modalSearchInput');
  if (modalInput) {
    query = modalInput.value;
  } else {
    // Fallback to navbar input if it still exists (legacy)
    const navInput = document.getElementById('searchInput');
    if (navInput) query = navInput.value;
  }

  if (!query) return;

  // Show loading state
  const list = document.getElementById('searchResultsList');
  if (list) list.innerHTML = '<div class="text-center p-3">Pesquisando...</div>';

  // Ensure modal is open
  showSearchModal();

  try {
    const response = await fetch(`/search?q=${encodeURIComponent(query)}`);
    const results = await response.json();

    if (list) {
      list.innerHTML = "";

      if (results.length === 0) {
        list.innerHTML = '<div class="p-3">Nenhum resultado encontrado.</div>';
        return;
      }

      results.forEach(item => {
        const a = document.createElement('a');
        a.className = "list-group-item list-group-item-action";
        a.href = "javascript:void(0)";
        a.onclick = () => {
          // Hide modal
          const modalEl = document.getElementById('searchResultsModal');
          const modal = bootstrap.Modal.getInstance(modalEl);
          if (modal) modal.hide();

          // Call global load function
          if (typeof loadDocByPaperSectionParagraph === 'function') {
            loadDocByPaperSectionParagraph(item.paper, item.section, item.paragraph);
          } else {
            console.error("loadDocByPaperSectionParagraph not found");
          }
        };

        a.innerHTML = `
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">${item.paper}:${item.section}.${item.paragraph}</h5>
                    </div>
                    <p class="mb-1">${item.text_pt || '(Sem texto PT)'}</p>
                    <small class="text-muted">${(item.text_en || '').substring(0, 100)}...</small>
                `;
        list.appendChild(a);
      });
    }

  } catch (e) {
    if (list) list.innerHTML = `<div class="text-danger p-3">Erro na pesquisa: ${e}</div>`;
  }
}

function showSearchModal() {
  const modalEl = document.getElementById('searchResultsModal');
  if (modalEl) {
    let modal = bootstrap.Modal.getInstance(modalEl);
    if (!modal) modal = new bootstrap.Modal(modalEl);
    modal.show();

    // Focus input after show
    setTimeout(() => {
      const input = document.getElementById('modalSearchInput');
      if (input) input.focus();
    }, 500);
  } else {
    console.error("searchResultsModal not found");
  }
}

function showSettingsModal() {
  alert("Configurações - Em breve");
}

// Bind Enter key on search input (modal)
document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('modalSearchInput');
  if (input) {
    input.addEventListener('keyup', (e) => {
      if (e.key === 'Enter') performSearch();
    });
  }
});


function setCookie(cname, cvalue, exdays) {
  var d = new Date();
  d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
  var expires = "expires=" + d.toUTCString();
  document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

function getCookie(cname) {
  var name = cname + "=";
  var decodedCookie = decodeURIComponent(document.cookie);
  var ca = decodedCookie.split(';');
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

// Get a dictionary from a query string
function getQueryStringParams(queryString) {
  // Use window.location.search if no queryString is provided
  queryString = queryString || window.location.search;

  // Remove the leading "?" if present
  if (queryString.startsWith("?")) {
    queryString = queryString.substring(1);
  }

  const params = {};

  if (!queryString) {
    return params; // Return empty object if no query string
  }

  const pairs = queryString.split("&");

  for (const pair of pairs) {
    const [name, value] = pair.split("=");

    if (name) { // Check if name exists after splitting
      try {
        // Decode URI components to handle special characters
        params[decodeURIComponent(name)] = value ? decodeURIComponent(value) : "";
      } catch (error) {
        console.error("Error decoding URI component:", error);
        params[name] = value || ""; // Fallback to raw value if decoding fails
      }
    }
  }
  return params;
}


function findImmediateParentDiv(element) {
  if (!element) {
    return null; // Handle null or undefined input
  }

  let parent = element.parentNode;

  while (parent) {
    if (parent.tagName.toLowerCase() === 'div') {
      return parent; // Found the immediate parent div
    }
    parent = parent.parentNode; // Go up the DOM tree
  }

  return null; // No parent div found
}


// Initialize the slider
// Must run after the load event
function initSlider() {
  divisor = document.getElementById('divisor');
  colunaEsquerda = document.getElementById('leftColumn');
  colunaDireita = document.getElementById('rightColumn');

  divisor.addEventListener('mousedown', (e) => {
    isDragging = true;
    startX = e.clientX;
    initialLeftWidth = colunaEsquerda.offsetWidth;
    initialRightWidth = colunaDireita.offsetWidth;
  });

  window.addEventListener('mousemove', (e) => {
    if (!isDragging) return;
    const deltaX = e.clientX - startX;
    const newLeftWidth = initialLeftWidth + deltaX;
    const newRightWidth = initialRightWidth - deltaX;
    const totalWidth = colunaEsquerda.offsetWidth + colunaDireita.offsetWidth + divisor.offsetWidth;
    const newLeftPercentage = (newLeftWidth / totalWidth) * 100;

    if (newLeftPercentage >= 5 && newLeftPercentage <= 95) {
      colunaEsquerda.style.width = `${newLeftPercentage}%`;
      colunaDireita.style.width = `${100 - newLeftPercentage - (divisor.offsetWidth / totalWidth * 100)}%`;
      divisor.setAttribute("aria-valuenow", newLeftPercentage);
    }
  });

  window.addEventListener('mouseup', () => {
    isDragging = false;
  });
}


// Add an item to the combo track
function addTocEntry(paper, section, paragraph) {
  newEntry = `${paper}:${section}-${paragraph}`;
  addNewEntryOption(newEntry)
}


function referenceFromString(href) {
  const entry = { paper: 0, section: 0, paragraph: 1 };
  try {
    const sep = /[;:.\-_ ]/;
    const parts = href.split(sep).filter(part => part.trim() !== '');

    switch (parts.length) {
      case 0:
        break;
      case 1:
        entry.paper = parseInt(parts[0], 10);
        entry.section = 0;
        entry.paragraph = 1;
        break;
      case 2:
        entry.paper = parseInt(parts[0], 10);
        entry.section = parseInt(parts[1], 10);
        entry.paragraph = 1;
        break;
      default:
        entry.paper = parseInt(parts[0], 10);
        entry.section = parseInt(parts[1], 10);
        entry.paragraph = parseInt(parts[2], 10);
        break;
    }
  } catch (error) {
    console.error("An error occurred while parsing href:", error);
    // In case of exception, the entry is returned with what it already has
  }
  return entry;
}
