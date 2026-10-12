import {
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";
export const canariasGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Canarias/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const canariasParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Canarias/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const canariasGovernmentChronology = canariasGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms, period.currentOnly).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const canariasParliamentChronology = canariasParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [...period.records, ...period.board],
      period.currentOnly,
    ).map((date) => ({ id: `${period.id}-${date}`, date, period })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
