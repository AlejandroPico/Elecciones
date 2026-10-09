import {
  catalanMembersAt,
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";
export {
  catalanMembersAt as madridMembersAt,
  catalanGroupsAt as madridGroupsAt,
} from "./catalonia-model";
export const madridGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Madrid/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const madridParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Madrid/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const madridGovernmentChronology = madridGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const madridParliamentChronology = madridParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [
        ...period.records,
        ...period.board,
        ...period.groups.flatMap((g) => g.members),
      ],
      period.currentOnly,
    )
      // No abrir ni animar fechas sin ningún mandato documentado.
      // Los intervalos individuales se conservan íntegros en las fichas.
      .filter(
        (date) =>
          period.nominalOnly || catalanMembersAt(period, date).length > 0,
      )
      .map((date) => ({ id: `${period.id}-${date}`, date, period })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
