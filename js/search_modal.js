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
    console.log("performSearch() called");
    const form = document.getElementById('searchForm');
    if (!form) {
        console.error("Search form not found!");
        return;
    }

    // Check query validity
    const queryInput = document.getElementById('modalSearchInput');
    const queryVal = queryInput.value.trim();
    if (!queryVal) {
        alert("Por favor, digite algo para buscar.");
        return;
    }

    // Capture Form Data
    const formData = new FormData(form);
    const payload = {};
    formData.forEach((value, key) => {
        payload[key] = value;
    });

    // Validar booleans que escapam do FormData
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    checkboxes.forEach(cb => {
        payload[cb.name] = cb.checked;
    });

    // Validar scopeType radio
    const scopeEl = form.querySelector('input[name="scopeType"]:checked');
    if (scopeEl) {
        payload['scopeType'] = scopeEl.value;
    }

    console.log("Sending Search Payload:", payload);

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        console.log("Search POST response status:", response.status);

        if (!response.ok) {
            let errorMsg = 'Erro ao salvar busca';
            try {
                const errJson = await response.json();
                if (errJson.error) errorMsg = errJson.error;
                else if (errJson.message) errorMsg = errJson.message;
            } catch (e) { }
            console.error("Search POST failed:", errorMsg);
            throw new Error(errorMsg);
        }

        // Hide Modal Forcefully
        const el = document.getElementById('searchResultsModal');
        // Try BS5 instance
        var modal = bootstrap.Modal.getInstance(el);
        if (modal) {
            modal.hide();
        } else {
            // Fallback
            console.warn("Bootstrap Modal instance not found, hiding manually.");
            el.classList.remove('show');
            el.style.display = 'none';
            document.body.classList.remove('modal-open');
            const backpack = document.querySelector('.modal-backdrop');
            if (backpack) backpack.remove();
        }

        // Trigger reload of the search page.
        console.log("Reloading content with action=perform_search");
        window.justPerformedSearch = true;
        loadContent('/search?action=perform_search');

    } catch (error) {
        console.error("Error in performSearch:", error);
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
