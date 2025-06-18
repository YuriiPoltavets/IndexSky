import { FETCH_DELAY_MS, CLASS_SUCCESS } from './constants.js';
import { fetchRowData } from './fetchRow.js';
import { hasRequiredFields } from './validators.js';
import { fillRowWithData, setRowStatus } from './domUtils.js';

async function onDataSearch(event) {
  event.preventDefault();
  const rows = Array.from(document.querySelectorAll('tbody tr'));

  for (const row of rows) {
    if (row.classList.contains(CLASS_SUCCESS)) continue;

    const rowIndex = row.dataset.rowId;
    const symbol = row.querySelector('.symbol-input')?.value.trim();
    if (!symbol) continue;
    const sector = row.querySelector('.sector-select')?.value.trim();

    try {
      const data = await fetchRowData({ symbol, sector, rowIndex });
      fillRowWithData(row, data);

      const valid = hasRequiredFields(data);
      setRowStatus(row, valid);
    } catch (err) {
      console.error('Fetch row failed', err);
      setRowStatus(row, false);
    }

    await new Promise(r => setTimeout(r, FETCH_DELAY_MS));
  }
}

document.querySelector('button[value="data_search"]')?.addEventListener('click', onDataSearch);
