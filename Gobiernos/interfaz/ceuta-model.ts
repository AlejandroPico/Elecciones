import {
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";
export const ceutaGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Ceuta/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const ceutaParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Ceuta/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const ceutaGovernmentChronology = ceutaGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms, period.currentOnly).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const ceutaParliamentChronology = ceutaParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [...period.records, ...period.board],
      period.currentOnly,
    ).map((date) => ({ id: `${period.id}-${date}`, date, period })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
