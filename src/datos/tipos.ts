export type Reference = {
  label: string;
  url: string;
  kind?: "institutional" | "encyclopedic";
};
export type Dossier = {
  date: string;
  title: string;
  text: string;
  status: string;
  source: Reference;
  additionalSources?: Reference[];
};
export type Person = {
  id: string;
  legacyIds?: string[];
  name: string;
  fullName?: string;
  initials: string;
  organization: string | null;
  relation: string;
  role: string;
  summary: string;
  offices: string[];
  portrait?: string;
  photoCredit?: string;
  photoSource?: string;
  birth?: string;
  birthDate?: string | null;
  birthYear?: number | null;
  deathYear?: number | null;
  deathDate?: string;
  personalSources?: Reference[];
  education?: string[];
  formationSources?: Reference[];
  timeline: { period: string; title: string; source: Reference }[];
  dossier?: Dossier[];
  references: Reference[];
  folder: string;
  sections: string[];
};
export type Organization = {
  id: string;
  name: string;
  fullName: string;
  foundation?: string;
  summary?: string;
  references: Reference[];
  documents: { title: string; election: string; url: string }[];
  history: {
    period: string;
    title: string;
    person?: string;
    source?: Reference;
  }[];
  leadership: {
    period: string;
    title: string;
    person: string;
    source: Reference;
  }[];
  website?: string;
  logo?: string;
  logoSource?: string;
  folder: string;
};
export type GovernmentMember = {
  person: string;
  name: string;
  role: string;
  level: string;
};
export type Cabinet = {
  id: string;
  label: string;
  date: string;
  members: GovernmentMember[];
};
export type Government = {
  id: string;
  legislature: string;
  name: string;
  source: string;
  cabinets: Cabinet[];
};
