// JavaScript para controlar a abertura do modal de busca
function showSearchModal() {
    // Check if we are returning from a performed search
    const urlParams = new URLSearchParams(window.location.search); // Note: window.location.search might be empty if hash routing or SPA-like loading.

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
    const form = document.getElementById('searchForm');
    if (!form) return;

    // Check query validity
    const queryInput = document.getElementById('modalSearchInput');
    if (!queryInput.value.trim()) {
        alert("Por favor, digite algo para buscar.");
        return;
    }

    // Capture Form Data
    const formData = new FormData(form);

    // Explicitly add checkbox values as true/false or similar, 
    // because FormData only includes checked boxes. Unchecked are missing.
    // Our Python helper handles missing boolean keys as False (default), 
    // EXCEPT that we need to transmit 'true' for checked ones.
    // FormData sends 'on' for checkboxes by default if no value attribute.
    // Let's create a plain object.
    const payload = {};
    formData.forEach((value, key) => {
        payload[key] = value;
    });

    // Handle checkboxes specifically if they need to be explicit booleans?
    // The Python helper `get_bool` handles 'on' as True.
    // Missing keys are distinct.
    // So standard FormData -> Object mapping is sufficient for 'checked=on'.

    try {
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
