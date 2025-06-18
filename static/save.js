async function handleSave() {
    const rows = Array.from(document.querySelectorAll('tbody tr'))
        .filter(tr => tr.dataset.status !== 'ok')
        .map(tr => {
            const getVal = selector => tr.querySelector(selector)?.value.trim() || '';
            return {
                symbol: getVal('.symbol-input').toUpperCase(),
                Sector: getVal('.sector-select'),
                Zacks: getVal('.zacks-output'),
                'Sector Growth': getVal('.sector-growth'),
                'EPS Growth': getVal('.eps-growth'),
                'Revenue Growth': getVal('.revenue-growth'),
                'PE Ratio': getVal('.pe-ratio'),
                'Volume Change': getVal('.volume-change'),
                'Дата': tr.querySelector('.date-cell')?.textContent.trim() || ''
            };
        });

    if (rows.length === 0) {
        alert('No rows to save');
        return;
    }

    try {
        const response = await fetch('/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(rows)
        });
        const results = await response.json();
        results.forEach(res => {
            const symbol = (res.symbol || '').toUpperCase();
            const tr = Array.from(document.querySelectorAll('tbody tr'))
                .find(r => r.querySelector('.symbol-input')?.value.trim().toUpperCase() === symbol);
            if (!tr) return;

            const sectorEl = tr.querySelector('.sector-select');
            if (sectorEl) sectorEl.dataset.status = '';

            if (res.status === 'ok') {
                tr.dataset.status = 'ok';
                tr.classList.remove('row-error');
                tr.classList.add('row-ok');
                tr.title = '';
            } else if (res.status === 'error') {
                tr.dataset.status = 'error';
                tr.classList.remove('row-ok');
                tr.classList.add('row-error');
                if (res.field === 'Sector' && sectorEl) {
                    sectorEl.dataset.status = 'error';
                }
                if (res.reason) {
                    tr.title = res.reason;
                }
            }
        });
    } catch (err) {
        console.log('Save failed', err);
        alert('Failed to save data');
    }
}

// Remove error highlighting from sector dropdowns once a valid value is chosen
document.querySelectorAll('.sector-select').forEach(sel => {
    sel.addEventListener('change', () => {
        if (sel.value.trim() !== '') {
            sel.removeAttribute('data-status');
        }
    });
});

async function onDataSearch(event) {
    event.preventDefault();
    const rows = Array.from(document.querySelectorAll('tbody tr'));

    for (const row of rows) {
        const idx = row.dataset.rowId;
        const symbol = row.querySelector('.symbol-input')?.value.trim();
        if (!symbol) continue;
        const sector = row.querySelector('.sector-select')?.value.trim();

        await fetch('/fetch-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, sector, idx })
        })
            .then(resp => resp.json())
            .then(data => {
                row.querySelector('.zacks-output').value = data['zacks'] ?? '';
                row.querySelector(`input[name="tipranks_${idx}"]`).value = data['tipranks'] ?? '';
                row.querySelector('.sector-growth').value = data['sector_growth'] ?? '';
                row.querySelector('.eps-growth').value = data['eps'] ?? '';
                row.querySelector('.revenue-growth').value = data['revenue'] ?? '';
                row.querySelector('.pe-ratio').value = data['pe_ratio'] ?? '';
                row.querySelector('.volume-change').value = data['volume'] ?? '';
                row.querySelector('.date-cell').textContent = data['date'] ?? '';

                try {
                    row.classList.remove('status-error');
                    row.classList.add('status-success');
                } catch (e) {
                    row.classList.remove('status-success');
                    row.classList.add('status-error');
                }
            })
            .catch(err => {
                console.log('Fetch row failed', err);
                row.classList.remove('status-success');
                row.classList.add('status-error');
            });

        await new Promise(r => setTimeout(r, 300));
    }
}

document.querySelector('button[value="data_search"]')?.addEventListener('click', onDataSearch);
