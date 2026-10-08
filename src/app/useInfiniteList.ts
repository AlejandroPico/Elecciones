import { useEffect, useRef, useState } from "react";
export function useInfiniteList(total: number, resetKey: string, batch = 40, active = true) {
  const [visibleCount, setVisibleCount] = useState(batch);
  const sentinel = useRef<HTMLDivElement>(null);
  useEffect(() => setVisibleCount(batch), [resetKey, batch]);
  useEffect(() => {
    const element = sentinel.current;
    if (!active || !element || visibleCount >= total) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting)
          setVisibleCount((count) => Math.min(total, count + batch));
      },
      { rootMargin: "240px 0px" },
    );
    observer.observe(element);
    return () => observer.disconnect();
  }, [total, visibleCount, batch, resetKey, active]);
  return { visibleCount, sentinel };
}
