import { useEffect, useState } from "react";
import { getScreener } from "../../shared/api/client";

export function ScreenerPage() {
  const [rows, setRows] = useState<{ ticker: string }[]>([]);

  useEffect(() => {
    getScreener().then(setRows);
  }, []);

  return (
    <div>
      <h1>Fresh ARA Screener</h1>
      <ul>{rows.map((row) => <li key={row.ticker}>{row.ticker}</li>)}</ul>
    </div>
  );
}
