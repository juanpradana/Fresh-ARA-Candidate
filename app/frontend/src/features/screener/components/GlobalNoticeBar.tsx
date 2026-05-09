export function GlobalNoticeBar({
  screenDate,
  warning,
}: {
  screenDate: string;
  warning: string | null;
}) {
  return (
    <>
      <section>
        <h2>Data Freshness</h2>
        <p>Latest screen date: {screenDate}</p>
        {warning && <p>Warning: {warning}</p>}
      </section>
      <section>
        <h2>Disclaimer</h2>
        <p>Sinyal bersifat probabilistik, bukan jaminan hasil.</p>
      </section>
    </>
  );
}
