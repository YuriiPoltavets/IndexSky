import {
  FETCH_DELAY_MS,
  LOGIC_OK,
  LOGIC_ERROR,
  STYLE_SUCCESS,
  STYLE_ERROR,
  STYLE_OK_BLUE
} from './constants.js';
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
      const data = response.data ?? response;
      if (!data || !data.symbol) {
        console.error('Invalid or empty response', response);
        setRowStatus(row, LOGIC_ERROR, STYLE_ERROR, '❌ Error');
        continue;
      }
      fillRowWithData(row, data);
      if (data.row_class === 'ok-blue') {
        setRowStatus(row, 'ok-blue', STYLE_OK_BLUE, '🔍 OK');
      } else {
        setRowStatus(row, LOGIC_ERROR, STYLE_ERROR, '❌ Error');
      }
    } catch (err) {
      console.error('Fetch row failed', err);
      setRowStatus(row, LOGIC_ERROR, STYLE_ERROR, '❌ Error');
    }

    await new Promise(r => setTimeout(r, FETCH_DELAY_MS));
  }
}

const dataSearchBtn = document.querySelector('button[value="data_search"]');
dataSearchBtn?.addEventListener('click', async (event) => {
  await onDataSearch(event);
  const res = await fetch('/api/logs');
  const data = await res.json();
  if (data.logs) {
    data.logs.forEach(msg => console.log(msg));
  }
});

function handleCalculate(event) {
  event.preventDefault();
  const rows = Array.from(document.querySelectorAll('tbody tr'));

  for (const row of rows) {
    if (isRowEmpty(row)) continue;
    if (row.dataset.status !== 'ok-blue') continue;

    const data = {
      sector: row.querySelector('.sector-select')?.value.trim(),
      zacks: row.querySelector('.zacks-output')?.value.trim(),
      tipranks: row.querySelector(`input[name="tipranks_${row.dataset.rowId}"]`)?.value.trim(),
      sector_growth: row.querySelector('.sector-growth')?.value.trim()
    };

    const ok = hasRequiredFields(data);
    if (ok) {
      setRowStatus(row, LOGIC_OK, STYLE_SUCCESS, '✅ OK');
    } else {
      setRowStatus(row, LOGIC_ERROR, STYLE_ERROR, '❌ Error');
    }
  }
}

document.querySelector('button[value="calculate"]')?.addEventListener('click', handleCalculate);
