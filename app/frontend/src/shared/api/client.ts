export async function getScreener(): Promise<{ ticker: string }[]> {
  const res = await fetch("/api/v1/screener");
  const json = await res.json();
  return json.data;
}
