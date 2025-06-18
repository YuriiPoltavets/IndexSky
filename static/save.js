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

async function onDataSearch() {
    const rows = Array.from(document.querySelectorAll('tbody tr'));

    for (const tr of rows) {
        if (tr.dataset.processed === 'true') continue;

        const idx = tr.dataset.rowId;
        const symbol = tr.querySelector('.symbol-input')?.value.trim();
        if (!symbol) continue;

        const sector = tr.querySelector('.sector-select')?.value.trim();

        try {
            const resp = await fetch('/fetch-row', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ symbol, sector, idx })
            });
            if (!resp.ok) throw new Error('Request failed');
            const data = await resp.json();

            if (data.zacks !== undefined) tr.querySelector('.zacks-output').value = data.zacks || '';
            if (data.tipranks !== undefined) tr.querySelector(`input[name="tipranks_${idx}"]`).value = data.tipranks || '';
            if (data.eps !== undefined) tr.querySelector('.eps-growth').value = data.eps || '';
            if (data.revenue !== undefined) tr.querySelector('.revenue-growth').value = data.revenue || '';
            if (data.pe_ratio !== undefined) tr.querySelector('.pe-ratio').value = data.pe_ratio || '';
            if (data.volume !== undefined) tr.querySelector('.volume-change').value = data.volume || '';
            tr.querySelector('.date-cell').textContent = new Date().toISOString().slice(0,10);

            tr.classList.remove('row-error');
            tr.classList.add('row-success');
            tr.dataset.processed = 'true';
        } catch (err) {
            console.log('Fetch row failed', err);
            tr.classList.remove('row-success');
            tr.classList.add('row-error');
            break;
        }

        await new Promise(r => setTimeout(r, 300));
    }
}

document.getElementById('data-search-btn')?.addEventListener('click', onDataSearch);
