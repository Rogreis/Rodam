// JavaScript para controlar a abertura do modal de busca
function showSearchModal() {
    var myModal = new bootstrap.Modal(document.getElementById('searchResultsModal'));
    myModal.show();
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

    const resultsList = document.getElementById('searchResultsList');
    resultsList.innerHTML = '<div class="text-center text-white"><div class="spinner-border" role="status"></div><br>Buscando...</div>';

    try {
        const response = await fetch('/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) throw new Error('Erro na busca');

        const results = await response.json();
        renderSearchResults(results);

    } catch (error) {
        console.error(error);
        resultsList.innerHTML = `<div class="alert alert-danger">Erro ao realizar busca: ${error.message}</div>`;
    }
}

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
