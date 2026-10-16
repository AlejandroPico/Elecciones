import {
  regionalDates,
  type CatalanGovernment,
  type CatalanParliament,
} from "./catalonia-model";

export function institutions(
  executives: Record<string, CatalanGovernment>,
  chambers: Record<string, CatalanParliament>,
) {
  const governments = Object.values(executives).sort((a, b) =>
    b.start.localeCompare(a.start),
  );
  const parliaments = Object.values(chambers).sort((a, b) =>
    b.start.localeCompare(a.start),
  );
  return {
    governments,
    parliaments,
    governmentChronology: governments
      .flatMap((period) =>
        regionalDates(period, period.terms, period.currentOnly).map((date) => ({
          id: `${period.id}-${date}`,
          date,
          period,
        })),
      )
      .sort((a, b) => a.date.localeCompare(b.date)),
    parliamentChronology: parliaments
      .flatMap((period) =>
        (
          period.snapshotDates ??
          regionalDates(
            period,
            [...period.records, ...period.board],
            period.currentOnly,
          )
        ).map((date) => ({
          id: `${period.id}-${date}`,
          date,
          period,
        })),
      )
      .sort((a, b) => a.date.localeCompare(b.date)),
  };
}

export const basqueInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/País Vasco/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/País Vasco/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
export const navarreInstitutions = institutions(
  import.meta.glob<CatalanGovernment>(
    "../Autonomías/Navarra/Gobierno/*/composicion.json",
    { eager: true, import: "default" },
  ),
  import.meta.glob<CatalanParliament>(
    "../Autonomías/Navarra/Parlamento/*/composicion.json",
    { eager: true, import: "default" },
  ),
);
