import { CLASS_SUCCESS, CLASS_ERROR } from './constants.js';

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

export function setRowStatus(row, isSuccess) {
  if (isSuccess) {
    row.classList.add(CLASS_SUCCESS);
    row.classList.remove(CLASS_ERROR);
  } else {
    row.classList.add(CLASS_ERROR);
    row.classList.remove(CLASS_SUCCESS);
  }
}
