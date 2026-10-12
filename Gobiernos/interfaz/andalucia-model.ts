import {
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";
export {
  catalanMembersAt as andaluciaMembersAt,
  catalanGroupsAt as andaluciaGroupsAt,
} from "./catalonia-model";
export const andaluciaGovernments = Object.values(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Andalucía/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const andaluciaParliaments = Object.values(
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Andalucía/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
).sort((a, b) => b.start.localeCompare(a.start));
export const andaluciaGovernmentChronology = andaluciaGovernments
  .flatMap((period) =>
    regionalDates(period, period.terms).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
export const andaluciaParliamentChronology = andaluciaParliaments
  .flatMap((period) =>
    regionalDates(
      period,
      [
        ...period.records,
        ...period.board,
        ...period.groups.flatMap((g) => g.members),
      ],
      period.currentOnly,
    ).map((date) => ({
      id: `${period.id}-${date}`,
      date,
      period,
    })),
  )
  .sort((a, b) => a.date.localeCompare(b.date));
