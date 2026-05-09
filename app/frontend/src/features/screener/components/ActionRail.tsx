import type { PresetMeta, ScreenerFilters } from "../../../shared/api/client";

type ActionRailProps = {
  presets: PresetMeta[];
  filters: ScreenerFilters;
  onChangeFilters: (next: ScreenerFilters) => void;
  onApply: () => void;
  csvExportUrl: string;
  xlsxExportUrl: string;
};

export function ActionRail({
  presets,
  filters,
  onChangeFilters,
  onApply,
  csvExportUrl,
  xlsxExportUrl,
}: ActionRailProps) {
  const inputClass = "mt-1 w-full rounded-md border border-zinc-700 bg-zinc-950 px-2 py-1 text-sm text-zinc-100 outline-none ring-0 placeholder:text-zinc-500 focus:border-emerald-400";

  return (
    <div data-testid="filter-action-rail" className="rounded border border-zinc-800 bg-zinc-900/40 p-3">
      <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-4">
        <label htmlFor="preset" className="text-xs text-zinc-300">
          Preset
          <select
            id="preset"
            className={inputClass}
            value={filters.preset}
            onChange={(event) => onChangeFilters({ ...filters, preset: event.target.value })}
          >
            {presets.map((preset) => (
              <option key={preset.preset_name} value={preset.preset_name}>{preset.preset_name}</option>
            ))}
          </select>
        </label>

        <label htmlFor="screen-date" className="text-xs text-zinc-300">
          Screen Date
          <input
            id="screen-date"
            className={inputClass}
            value={filters.screenDate}
            onChange={(event) => onChangeFilters({ ...filters, screenDate: event.target.value })}
          />
        </label>

        <label htmlFor="start-date" className="text-xs text-zinc-300">
          Backtest Start
          <input
            id="start-date"
            className={inputClass}
            value={filters.start}
            onChange={(event) => onChangeFilters({ ...filters, start: event.target.value })}
          />
        </label>

        <label htmlFor="end-date" className="text-xs text-zinc-300">
          Backtest End
          <input
            id="end-date"
            className={inputClass}
            value={filters.end}
            onChange={(event) => onChangeFilters({ ...filters, end: event.target.value })}
          />
        </label>
      </div>

      <div className="mt-3 flex flex-wrap items-center gap-3">
        <button className="rounded border border-emerald-400 px-3 py-1 text-emerald-300 transition hover:bg-emerald-500/10" onClick={onApply}>Apply Filters</button>
        <a className="rounded border border-zinc-700 px-2 py-1 text-sm text-zinc-300 hover:border-zinc-500" href={csvExportUrl}>Export CSV</a>
        <a className="rounded border border-zinc-700 px-2 py-1 text-sm text-zinc-300 hover:border-zinc-500" href={xlsxExportUrl}>Export XLSX</a>
      </div>
    </div>
  );
}
