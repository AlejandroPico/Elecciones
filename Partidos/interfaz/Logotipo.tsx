import { useState } from "react";
import { logos } from "./catalogo";
import type { Organization } from "../../Políticos/interfaz/datos/tipos";
export function PartyLogo({
  party,
  className,
}: {
  party: Organization;
  className?: string;
}) {
  const [failed, setFailed] = useState(false);
  return logos[party.id] && !failed ? (
    <img
      className={className}
      src={logos[party.id]}
      alt={party.name}
      loading="lazy"
      onError={() => setFailed(true)}
    />
  ) : (
    <span
      className="party-logo-pending"
      aria-label={`${party.fullName}. Logotipo pendiente`}
    >
      <strong>
        {party.name.length <= 15
          ? party.name
          : party.fullName
              .split(/\s+/)
              .slice(0, 4)
              .map((w) => w[0])
              .join("")}
      </strong>
      <small>{party.fullName}</small>
    </span>
  );
}
