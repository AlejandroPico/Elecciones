import { useState } from "react";
import { portraits, type Person } from "./datos/catalogo";
export function Portrait({ person }: { person: Person }) {
  const [error, setError] = useState(false);
  return person.portrait && !error ? (
    <img
      src={portraits[person.portrait]}
      alt={person.name}
      loading="lazy"
      onError={() => setError(true)}
    />
  ) : (
    <div className="portrait-placeholder">
      <span>{person.initials}</span>
      <small>Retrato pendiente</small>
    </div>
  );
}
