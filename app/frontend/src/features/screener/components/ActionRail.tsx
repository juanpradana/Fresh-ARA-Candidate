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
  return (
    <div data-testid="filter-action-rail" className="rounded border border-zinc-800 bg-zinc-900/40 p-3">
      <label htmlFor="preset">Preset</label>
      <select
        id="preset"
        value={filters.preset}
        onChange={(event) => onChangeFilters({ ...filters, preset: event.target.value })}
      >
        {presets.map((preset) => (
          <option key={preset.preset_name} value={preset.preset_name}>{preset.preset_name}</option>
        ))}
      </select>

      <label htmlFor="screen-date">Screen Date</label>
      <input
        id="screen-date"
        value={filters.screenDate}
        onChange={(event) => onChangeFilters({ ...filters, screenDate: event.target.value })}
      />

      <label htmlFor="start-date">Backtest Start</label>
      <input
        id="start-date"
        value={filters.start}
        onChange={(event) => onChangeFilters({ ...filters, start: event.target.value })}
      />

      <label htmlFor="end-date">Backtest End</label>
      <input
        id="end-date"
        value={filters.end}
        onChange={(event) => onChangeFilters({ ...filters, end: event.target.value })}
      />

      <button className="rounded border border-emerald-400 px-3 py-1 text-emerald-300" onClick={onApply}>Apply Filters</button>
      <a href={csvExportUrl}>Export CSV</a>
      <a href={xlsxExportUrl}>Export XLSX</a>
    </div>
  );
}
