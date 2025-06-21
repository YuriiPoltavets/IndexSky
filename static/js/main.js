/*📄 form_handler.py — логіка обробки HTML-форми з даними акцій

🔹 Основні функції:

1. extract_form_data(form)
   - Зчитує всі символи (tickers) і сектори з форми.
   - Пропускає порожні рядки.
   - Повертає список рядків із введеними даними.

2. get_sector(symbol, user_sector)
   - Визначає сектор для акції:
     ▪️ якщо користувач вказав вручну — бере його;
     ▪️ інакше — шукає у словнику custom_sectors.

3. handle_form_submission(form)
   - Головна функція: обробляє всі дії після натискання кнопки.
   - Для кожного символу:
     ▪️ підбирає сектор;
     ▪️ парсить метрики (Zacks, TipRanks, сектор);
     ▪️ записує статус рядка (успіх або помилка);
     ▪️ зберігає оновлені дані у список.

💡 Використовується у Flask-маршруті '/' для оновлення таблиці в інтерфейсі. */




import {
  FETCH_DELAY_MS,
  LOGIC_OK,
  LOGIC_ERROR,
  STYLE_SUCCESS,
  STYLE_ERROR,
  STYLE_OK_BLUE
} from './constants.js';
import { fetchRowData } from './fetchRow.js';
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
        console.log(`Setting status for row ${rowIndex}:`, data.row_class);
        setRowStatus(row, 'ok-blue', STYLE_OK_BLUE, '🔍 OK');
      } else {
        setRowStatus(row, LOGIC_ERROR, STYLE_ERROR, '❌ Error');
      }
    } catch (err) {
      console.error('Fetch row failed', err);
      setRowStatus(row, LOGIC_ERROR, STYLE_ERROR, '❌ Error');
    }
    await new Promise(resolve => requestAnimationFrame(resolve));
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
    if (row.dataset.status !== 'ok-blue') continue;

    setRowStatus(row, LOGIC_OK, STYLE_SUCCESS, '✅ OK');
  }
}

document.querySelector('button[value="calculate"]')?.addEventListener('click', handleCalculate);
