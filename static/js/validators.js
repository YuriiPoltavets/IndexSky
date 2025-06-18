import { REQUIRED_FIELDS } from './constants.js';

export function hasRequiredFields(data) {
  for (const rule of REQUIRED_FIELDS) {
    const val = data[rule.key];
    if (val === undefined || val === null || val === '') {
      return false;
    }
    if (rule.type === 'number') {
      const num = typeof val === 'number' ? val : parseFloat(val);
      if (Number.isNaN(num)) {
        return false;
      }
    }
  }
  return true;
}
