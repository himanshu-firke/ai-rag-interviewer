"use client";

import { useEffect, useRef } from "react";

export default function BrandSlider({ brandList }) {
  const scrollRef = useRef(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    let raf;
    let pos = 0;
    const speed = 0.4;

    function step() {
      pos += speed;
      if (pos >= el.scrollWidth / 2) pos = 0;
      el.style.transform = `translateX(-${pos}px)`;
      raf = requestAnimationFrame(step);
    }
    raf = requestAnimationFrame(step);
    return () => cancelAnimationFrame(raf);
  }, []);

  const doubled = [...brandList, ...brandList];

  return (
    <div className="overflow-hidden border-t border-slate-800 bg-slate-900 py-10">
      <p className="mb-8 px-4 text-center text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
        Built with industry-leading technologies
      </p>

      <div className="relative">
        {/* Fade edges */}
        <div className="pointer-events-none absolute inset-y-0 left-0 z-10 w-24 bg-gradient-to-r from-slate-900 to-transparent" />
        <div className="pointer-events-none absolute inset-y-0 right-0 z-10 w-24 bg-gradient-to-l from-slate-900 to-transparent" />

        <div ref={scrollRef} className="flex w-max gap-10 will-change-transform">
          {doubled.map((brand, i) => (
            <div
              key={i}
              className="flex shrink-0 items-center gap-3 rounded-full border border-white/10 bg-white/5 px-5 py-2.5 text-slate-400 transition-colors hover:bg-white/10 hover:text-slate-200"
            >
              {brand.image ? (
                <img
                  src={brand.image}
                  alt={brand.name}
                  className="h-5 w-auto opacity-70"
                />
              ) : (
                <span className="h-2 w-2 shrink-0 rounded-full bg-blue-400" />
              )}
              <span className="whitespace-nowrap text-sm font-semibold tracking-wide">
                {brand.name}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
