import { useRef, useState, type HTMLAttributes } from "react";

/** El táctil conserva el desplazamiento nativo; el ratón permite agarrar la fila. */
export default function DragRail({
  children,
  className = "",
  ...props
}: HTMLAttributes<HTMLDivElement>) {
  const gesture = useRef<{
    id: number;
    x: number;
    left: number;
    moved: boolean;
  } | null>(null);
  const suppressClick = useRef(false);
  const [dragging, setDragging] = useState(false);
  return (
    <div
      {...props}
      className={`${className} drag-rail${dragging ? " is-dragging" : ""}`}
      onPointerDown={(event) => {
        if (event.pointerType !== "mouse" || event.button !== 0) return;
        suppressClick.current = false;
        gesture.current = {
          id: event.pointerId,
          x: event.clientX,
          left: event.currentTarget.scrollLeft,
          moved: false,
        };
      }}
      onPointerMove={(event) => {
        const current = gesture.current;
        if (!current || current.id !== event.pointerId) return;
        if (!(event.buttons & 1)) {
          gesture.current = null;
          setDragging(false);
          return;
        }
        const distance = event.clientX - current.x;
        if (!current.moved && Math.abs(distance) < 5) return;
        current.moved = true;
        suppressClick.current = true;
        setDragging(true);
        event.currentTarget.setPointerCapture(event.pointerId);
        event.currentTarget.scrollLeft = current.left - distance;
        event.preventDefault();
      }}
      onPointerUp={(event) => {
        if (gesture.current?.id !== event.pointerId) return;
        gesture.current = null;
        setDragging(false);
        if (event.currentTarget.hasPointerCapture(event.pointerId))
          event.currentTarget.releasePointerCapture(event.pointerId);
      }}
      onPointerCancel={() => {
        gesture.current = null;
        setDragging(false);
      }}
      onLostPointerCapture={() => {
        gesture.current = null;
        setDragging(false);
      }}
      onClickCapture={(event) => {
        if (!suppressClick.current || event.detail === 0) return;
        event.preventDefault();
        event.stopPropagation();
        suppressClick.current = false;
      }}
      onDragStart={(event) => event.preventDefault()}
    >
      {children}
    </div>
  );
}
