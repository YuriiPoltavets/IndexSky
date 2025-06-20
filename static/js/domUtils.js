import { CLASS_SUCCESS, CLASS_ERROR, CLASS_OK_BLUE } from './constants.js';

export function fillRowWithData(row, data) {
  const { symbol, sector, zacks, tipranks, sector_growth, date } = data;
  const rowIndex = row.dataset.rowId;

  const symbolEl = row.querySelector('.symbol-input');
  if (symbolEl && symbol) {
    symbolEl.value = String(symbol).toUpperCase();
  }

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

}

export function isRowEmpty(row) {
  const fields = Array.from(row.querySelectorAll('input, select'));
  return fields.every(el => !el.value);
}

export function setRowStatus(row, statusClass, statusText = '') {
  const all = [CLASS_SUCCESS, CLASS_ERROR, CLASS_OK_BLUE];
  row.classList.remove(...all);
  if (statusClass) {
    row.classList.add(statusClass);
    row.dataset.status = statusClass;
  } else {
    delete row.dataset.status;
  }

  if (statusText !== undefined) {
    const label = row.querySelector('.status-label');
    if (label) label.textContent = statusText;
  }
}
