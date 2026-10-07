/** Un plazo único por ficha: editar respuesta o importancia no lo reinicia. */
export function createAdvanceClock() {
  let timer: ReturnType<typeof setTimeout> | undefined;
  return {
    start(next: () => void) {
      if (timer !== undefined) return false;
      timer = setTimeout(() => {
        timer = undefined;
        next();
      }, 3000);
      return true;
    },
    cancel() {
      clearTimeout(timer);
      timer = undefined;
    },
  };
}
