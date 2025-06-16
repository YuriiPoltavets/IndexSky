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
