export function GlobalNoticeBar({
  screenDate,
  warning,
}: {
  screenDate: string;
  warning: string | null;
}) {
  return (
    <div className="grid gap-3 lg:grid-cols-2">
      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
        <h2 className="text-sm font-medium text-zinc-200">Data Freshness</h2>
        <p className="mt-1 text-sm text-zinc-300">Latest screen date: {screenDate}</p>
        {warning && <p className="mt-2 rounded-md border border-amber-600/40 bg-amber-400/10 px-2 py-1 text-xs text-amber-200">Warning: {warning}</p>}
      </section>
      <section className="rounded-lg border border-zinc-800 bg-zinc-900/50 p-4">
        <h2 className="text-sm font-medium text-zinc-200">Disclaimer</h2>
        <p className="mt-1 text-sm text-zinc-300">Sinyal bersifat probabilistik, bukan jaminan hasil.</p>
      </section>
    </div>
  );
}
