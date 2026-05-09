export function SummaryStrip({ totalCandidates, idealCount }: { totalCandidates: number; idealCount: number }) {
  return (
    <section data-testid="summary-strip" className="mt-3 rounded border border-zinc-800 bg-zinc-900/50 p-3">
      <div className="grid gap-2 sm:grid-cols-2">
        <div className="rounded-md border border-zinc-800 bg-zinc-950/60 px-3 py-2">
          <p className="text-[11px] uppercase tracking-wide text-zinc-400">Total candidates</p>
          <p className="mt-1 text-base font-semibold text-zinc-100">Total candidates: {totalCandidates}</p>
        </div>
        <div className="rounded-md border border-zinc-800 bg-zinc-950/60 px-3 py-2">
          <p className="text-[11px] uppercase tracking-wide text-zinc-400">Ideal count</p>
          <p className="mt-1 text-base font-semibold text-zinc-100">Ideal count: {idealCount}</p>
        </div>
      </div>
    </section>
  );
}
