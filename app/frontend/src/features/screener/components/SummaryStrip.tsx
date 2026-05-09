export function SummaryStrip({ totalCandidates, idealCount }: { totalCandidates: number; idealCount: number }) {
  return (
    <section data-testid="summary-strip" className="mt-3 rounded border border-zinc-800 bg-zinc-900/50 p-3">
      <p>Total candidates: {totalCandidates}</p>
      <p>Ideal count: {idealCount}</p>
    </section>
  );
}
