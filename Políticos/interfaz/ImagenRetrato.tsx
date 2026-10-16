import { useEffect, useState } from "react";
/** Retrato sin dependencia del catálogo completo; útil para vistas pequeñas. */
export function PortraitImage({
  src,
  name,
  initials,
  position,
}: {
  src?: string;
  name: string;
  initials: string;
  position?: string;
}) {
  const [error, setError] = useState(false);
  useEffect(() => setError(false), [src]);
  return src && !error ? (
    <img
      src={src}
      alt={name}
      style={position ? { objectPosition: position } : undefined}
      loading="lazy"
      onError={() => setError(true)}
    />
  ) : (
    <div className="portrait-placeholder">
      <span>{initials}</span>
      <small>Retrato pendiente</small>
    </div>
  );
}
