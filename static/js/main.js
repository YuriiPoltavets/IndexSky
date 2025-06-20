import { FETCH_DELAY_MS, CLASS_SUCCESS, CLASS_ERROR, CLASS_OK_BLUE } from './constants.js';
import { fetchRowData } from './fetchRow.js';
import { hasRequiredFields } from './validators.js';
import { fillRowWithData, setRowStatus, isRowEmpty } from './domUtils.js';


async function onDataSearch(event) {
  event.preventDefault();
  const rows = Array.from(document.querySelectorAll('tbody tr'));

  for (const row of rows) {
    if (isRowEmpty(row)) continue;

    const rowIndex = row.dataset.rowId;
    const symbol = row.querySelector('.symbol-input')?.value.trim();
    if (!symbol) continue;
    const sector = row.querySelector('.sector-select')?.value.trim();

    try {
      const response = await fetchRowData({ symbol, sector, rowIndex });
      if (response.logs && Array.isArray(response.logs)) {
        response.logs.forEach(line => console.log(line));
      }
      const data = response.data || response;
      fillRowWithData(row, data);
      setRowStatus(row, CLASS_OK_BLUE, '🔍 OK');
    } catch (err) {
      console.error('Fetch row failed', err);
      setRowStatus(row, CLASS_ERROR, '❌ Error');
    }

    await new Promise(r => setTimeout(r, FETCH_DELAY_MS));
  }
}

document.querySelector('button[value="data_search"]')?.addEventListener('click', onDataSearch);

function handleCalculate(event) {
  event.preventDefault();
  const rows = Array.from(document.querySelectorAll('tbody tr'));

  for (const row of rows) {
    if (isRowEmpty(row)) continue;

    const data = {
      sector: row.querySelector('.sector-select')?.value.trim(),
      zacks: row.querySelector('.zacks-output')?.value.trim(),
      tipranks: row.querySelector(`input[name="tipranks_${row.dataset.rowId}"]`)?.value.trim(),
      sector_growth: row.querySelector('.sector-growth')?.value.trim()
    };

    const ok = hasRequiredFields(data);
    if (ok) {
      setRowStatus(row, CLASS_SUCCESS, '✅ OK');
    } else {
      setRowStatus(row, CLASS_ERROR, '❌ Error');
    }
  }
}

document.querySelector('button[value="calculate"]')?.addEventListener('click', handleCalculate);
