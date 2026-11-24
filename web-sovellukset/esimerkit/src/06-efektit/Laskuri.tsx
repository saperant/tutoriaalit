import { useEffect, useState } from "react";

// @alku sulkeuma
/** Laskee kuluneita sekunteja. Versio "vanha" sulkee ensimmäisen
 *  renderöinnin tilan sisäänsä (vanhentunut sulkeuma, stale closure). */
export function Sekunnit({ versio }: { versio: "vanha" | "oikea" }) {
  const [sekunnit, setSekunnit] = useState(0);
  useEffect(() => {
    const ajastin = setInterval(() => {
      if (versio === "vanha") setSekunnit(sekunnit + 1);  // aina 0 + 1
      else setSekunnit((s) => s + 1);                     // edellisestä
    }, 1000);
    return () => clearInterval(ajastin);
  }, [versio]);   // lint-sääntö exhaustive-deps huomauttaisi: sekunnit
  return <p>{sekunnit} s</p>;
}
// @loppu sulkeuma
