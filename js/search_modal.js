// JavaScript para controlar a abertura do modal de busca
function showSearchModal() {
    // Check if we are returning from a performed search
    const urlParams = new URLSearchParams(window.location.search); // Note: window.location.search might be empty if hash routing or SPA-like loading.
    // Our 'loadContent' updates history? No. It just fetches.
    // The loadContent call was `loadContent('/search?action=perform_search')`.
    // The fetch URL has the param. The window URL might not.
    // However, the `SearchFragment` injects `<script>showSearchModal()</script>`.

    // Better approach: Pass an argument to showSearchModal based on context? No, the call is hardcoded in Python.

    // Let's check a global flag or the element state.
    // Actually, `loadContent` URL is internal.
    // If the Python code injects the script, it executes.

    // Correct logic:
    // If we just performed a search, we want to SEE the results (the text in Left/Right columns).
    // We do NOT want the modal to cover them.
    // So distinct state is needed.

    // If I modify SearchFragment to conditionally inject the script?
    // That requires `app.py` to pass the `action` param to `SearchFragment`.
    // Let's do that. It's robust.

    // But since I am in `js/search_modal.js` instructions here...
    // I will proceed with the Python fix in the NEXT tool call if this one was intended for JS.
    // Wait, I can't conditionally execute the tool.
    // I will assume modifying Python is better.

    // Let's Stick to the requested tool change: JS.
    // But JS `window.location` might `/?p=indexToc`. `loadContent` doesn't change window URL?
    // Checking `app.py`, `loadContent` updates history? No "pushState" seen in `main.html`.

    // So `window.location` is useless.

    // Alternative: set a global JS variable before calling loadContent?
    // In performSearch: `window.justPerformedSearch = true; loadContent(...)`
    // In showSearchModal: `if (window.justPerformedSearch) { window.justPerformedSearch = false; return; }`

    if (window.justPerformedSearch) {
        window.justPerformedSearch = false;
        return;
    }

    var el = document.getElementById('searchResultsModal');
    // Use getOrCreateInstance if available (BS5), otherwise fallback logic using getInstance
    var myModal = bootstrap.Modal.getInstance(el);
    if (!myModal) {
        myModal = new bootstrap.Modal(el);
    }

    // Only show if not already shown to avoid backdrop accumulation or interfering with open state
    if (!el.classList.contains('show')) {
        myModal.show();
    }
}

function toggleSearchScope() {
    const scopeParts = document.getElementById('scopeParts');
    const partsOptions = document.getElementById('partsOptions');
    const docsInput = document.getElementById('docsInput');

    if (scopeParts.checked) {
        // Habilita as checkboxes
        partsOptions.querySelectorAll('input').forEach(el => el.disabled = false);
        // Desabilita o input de docs
        docsInput.disabled = true;
    } else {
        // Desabilita checkboxes
        partsOptions.querySelectorAll('input').forEach(el => el.disabled = true);
        // Habilita input de docs
        docsInput.disabled = false;
        docsInput.focus();
    }
}

async function performSearch() {
    const query = document.getElementById('modalSearchInput').value;
    if (!query) {
        alert("Por favor, digite algo para buscar.");
        return;
    }

    // New Fields Mapping
    const LanguageIdToSearch = parseInt(document.querySelector('input[name="LanguageIdToSearch"]:checked').value);
    const SearchResultsOrder = parseInt(document.querySelector('input[name="SearchResultsOrder"]:checked').value);

    const scopePartsChecked = document.getElementById('scopeParts').checked;

    // Boolean flags
    const SearchParts = scopePartsChecked;
    const SearchDocuments = !scopePartsChecked; // or check scopeDocs.checked

    const SearchIntroduction = document.getElementById('partIntro').checked;
    const SearchPartI = document.getElementById('part1').checked;
    const SearchPartII = document.getElementById('part2').checked;
    const SearchPartIII = document.getElementById('part3').checked;
    const SearchPartIV = document.getElementById('part4').checked;

    const SearchDocumentsList = document.getElementById('docsInput').value;

    const SearchMaxResults = parseInt(document.getElementById('maxResults').value);
    const SearchItemsToShow = parseInt(document.getElementById('pageSize').value);

    const payload = {
        query: query,
        LanguageIdToSearch: LanguageIdToSearch,
        SearchResultsOrder: SearchResultsOrder,
        SearchParts: SearchParts,
        SearchDocuments: SearchDocuments,
        SearchIntroduction: SearchIntroduction,
        SearchPartI: SearchPartI,
        SearchPartII: SearchPartII,
        SearchPartIII: SearchPartIII,
        SearchPartIV: SearchPartIV,
        SearchDocumentsList: SearchDocumentsList,
        SearchMaxResults: SearchMaxResults,
        SearchItemsToShow: SearchItemsToShow
    };

    try {
        // We only send the payload to save the config.
        // We ignore the returned results because the requirement is to "return to SearchFragment".
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Erro ao salvar busca');

        // Hide Modal
        const el = document.getElementById('searchResultsModal');
        const modal = bootstrap.Modal.getInstance(el);
        if (modal) {
            modal.hide();
        }

        // Trigger reload of the search page.
        // This causes the SearchFragment to render again.
        // The SearchFragment will read the updated global_config (saved by /search endpoint).
        window.justPerformedSearch = true;
        loadContent('/search?action=perform_search');

    } catch (error) {
        console.error(error);
        alert(`Erro ao iniciar busca: ${error.message}`);
    }
}

// renderSearchResults is no longer needed in the modal
/*
function renderSearchResults(results) {
    const list = document.getElementById('searchResultsList');
    list.innerHTML = '';

    if (!results || results.length === 0) {
        list.innerHTML = '<div class="alert alert-warning">Nenhum resultado encontrado.</div>';
        return;
    }

    results.forEach(item => {
        const div = document.createElement('div');
        div.className = 'list-group-item list-group-item-action bg-dark text-white border-secondary mb-2';

        const header = document.createElement('div');
        header.className = 'd-flex w-100 justify-content-between';

        const h5 = document.createElement('h5');
        h5.className = 'mb-1 text-info';
        h5.innerHTML = item.title || item.doc_id;

        if (item.score) {
            const small = document.createElement('small');
            small.className = 'text-muted';
            small.innerText = `Score: ${item.score.toFixed(2)}`;
            header.appendChild(h5);
            header.appendChild(small);
        } else {
            header.appendChild(h5);
        }

        const p = document.createElement('p');
        p.className = 'mb-1';
        p.innerHTML = item.snippet || item.text || '(Sem amostra)';

        div.onclick = () => {
            console.log("Clicou em", item);
            // Implement navigation logic here if needed
            const modalEl = document.getElementById('searchResultsModal');
            const modal = bootstrap.Modal.getInstance(modalEl);
            modal.hide();
        };

        div.appendChild(header);
        div.appendChild(p);
        list.appendChild(div);
    });
}
*/
