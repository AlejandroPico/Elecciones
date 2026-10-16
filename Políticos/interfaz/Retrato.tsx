import { portraits, type Person } from "./datos/catalogo";
import { PortraitImage } from "./ImagenRetrato";
export function Portrait({ person }: { person: Person }) {
  return (
    <PortraitImage
      src={person.portrait ? portraits[person.portrait] : undefined}
      name={person.name}
      initials={person.initials}
      position={person.photoPosition}
      scale={person.photoScale}
    />
  );
}
