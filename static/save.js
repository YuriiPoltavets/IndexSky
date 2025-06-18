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
    const REQUIRED_FIELDS = [
        { key: 'sector' },
        { key: 'zacks', type: 'number' },
        { key: 'tipranks', type: 'number' },
        { key: 'sector_growth' }
    ];

    const rows = Array.from(document.querySelectorAll('tbody tr'));

    for (const row of rows) {
        if (row.classList.contains('status-success')) continue;
        const rowIndex = row.dataset.rowId;
        const symbol = row.querySelector('.symbol-input')?.value.trim();
        if (!symbol) continue;
        const sector = row.querySelector('.sector-select')?.value.trim();

        await fetch('/fetch-data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ symbol, sector, rowIndex })
        })
            .then(resp => resp.json())
            .then(data => {
                const { zacks, tipranks, sector_growth, date, sector } = data;

                const sectorEl = row.querySelector('.sector-select');
                if (sectorEl && sector && !sectorEl.value) {
                    sectorEl.value = sector;
                }

                const zacksEl = row.querySelector('.zacks-output');
                if (zacksEl) zacksEl.value = zacks ?? '';

                const tipEl = row.querySelector(`input[name="tipranks_${rowIndex}"]`);
                if (tipEl) tipEl.value = tipranks ?? '';

                const sectorGrowthEl = row.querySelector('.sector-growth');
                if (sectorGrowthEl) sectorGrowthEl.value = sector_growth ?? '';

                const dateEl = row.querySelector('.date-cell');
                if (dateEl) dateEl.textContent = date ?? '';

                const epsEl = row.querySelector('.eps-growth');
                if (epsEl) epsEl.value = data.eps ?? '';

                const revEl = row.querySelector('.revenue-growth');
                if (revEl) revEl.value = data.revenue ?? '';

                const peEl = row.querySelector('.pe-ratio');
                if (peEl) peEl.value = data.pe_ratio ?? '';

                const volEl = row.querySelector('.volume-change');
                if (volEl) volEl.value = data.volume ?? '';

                let allValid = true;
                for (const f of REQUIRED_FIELDS) {
                    const val = data[f.key];
                    if (val === undefined || val === null || val === '') {
                        allValid = false;
                        break;
                    }
                    if (f.type === 'number') {
                        const num = typeof val === 'number' ? val : parseFloat(val);
                        if (Number.isNaN(num)) {
                            allValid = false;
                            break;
                        }
                    }
                }

                if (allValid) {
                    row.classList.add('status-success');
                    row.classList.remove('status-error');
                } else {
                    row.classList.add('status-error');
                    row.classList.remove('status-success');
                }
            })
            .catch(err => {
                console.error('Fetch row failed', err);
                row.classList.add('status-error');
                row.classList.remove('status-success');
            });

        await new Promise(r => setTimeout(r, 300));
    }
}

document.querySelector('button[value="data_search"]')?.addEventListener('click', onDataSearch);
