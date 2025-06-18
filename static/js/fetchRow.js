export async function fetchRowData({ symbol, sector, rowIndex }) {
  const resp = await fetch('/fetch-data', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ symbol, sector, rowIndex })
  });

  if (!resp.ok) {
    throw new Error(`Request failed with status ${resp.status}`);
  }

  return resp.json();
}
