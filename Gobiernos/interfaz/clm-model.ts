import {
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";
export const clmGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Castilla-La Mancha/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const clmParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Castilla-La Mancha/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const clmGovernmentChronology = clmGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms, period.currentOnly).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const clmParliamentChronology = clmParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [...period.records, ...period.board],
      period.currentOnly,
    ).map((date) => ({ id: `${period.id}-${date}`, date, period })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
