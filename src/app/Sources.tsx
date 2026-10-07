import { ArrowUpRight } from "lucide-react";
import type { Reference } from "../../Políticos/interfaz/datos/tipos";
export default function Sources({ sources }: { sources: Reference[] }) {
  return (
    <ul className="reference-list">
      {sources.map((s, index) => (
        <li key={`${s.url}-${index}`}>
          <a href={s.url} target="_blank" rel="noreferrer">
            {s.label}
            <ArrowUpRight size={14} />
          </a>
        </li>
      ))}
    </ul>
  );
}
