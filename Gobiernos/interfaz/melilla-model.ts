import {
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";
export const melillaGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Melilla/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const melillaParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Melilla/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const melillaGovernmentChronology = melillaGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms, period.currentOnly).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const melillaParliamentChronology = melillaParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [...period.records, ...period.board],
      period.currentOnly,
    ).map((date) => ({ id: `${period.id}-${date}`, date, period })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
