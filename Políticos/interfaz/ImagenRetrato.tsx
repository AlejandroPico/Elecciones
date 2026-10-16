import { useEffect, useState, type CSSProperties } from "react";
/** Retrato sin dependencia del catálogo completo; útil para vistas pequeñas. */
export function PortraitImage({
  src,
  name,
  initials,
  position,
  scale,
}: {
  src?: string;
  name: string;
  initials: string;
  position?: string;
  scale?: number;
}) {
  const [error, setError] = useState(false);
  const cropScale = scale && scale > 1 ? scale : undefined;
  useEffect(() => setError(false), [src]);
  return src && !error ? (
    <img
      src={src}
      alt={name}
      data-crop-scale={cropScale}
      style={
        position || cropScale
          ? ({
              objectPosition: position,
              "--portrait-scale": cropScale,
            } as CSSProperties)
          : undefined
      }
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
