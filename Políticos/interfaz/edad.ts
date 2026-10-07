export function ageAt(birth: string, date = new Date()): number {
  const [year, month, day] = birth.split("-").map(Number);
  return (
    date.getFullYear() -
    year -
    (date.getMonth() + 1 < month ||
    (date.getMonth() + 1 === month && date.getDate() < day)
      ? 1
      : 0)
  );
}
