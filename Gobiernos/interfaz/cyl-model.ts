import {
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";
export const cylGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Castilla y León/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const cylParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Castilla y León/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const cylGovernmentChronology = cylGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms, period.currentOnly).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const cylParliamentChronology = cylParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [...period.records, ...period.board],
      period.currentOnly,
    ).map((date) => ({ id: `${period.id}-${date}`, date, period })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
