import type { Asiakas } from "../07-verkko/asiakas.ts";
import { useHaku } from "../07-verkko/useHaku.ts";
import { Sivu } from "./Sivu.tsx";

/** Varusteiden yhteenveto. Oletusvienti, jotta React.lazy voi ladata
 *  modulin erillisenä tiedostona. */
export default function Raportti({ api }: { api: Asiakas }) {
  const haku = useHaku("tilat", (signal) => api.haeTilat(signal));
  if (haku.tila !== "valmis") return <Sivu otsikko="Raportti">{null}</Sivu>;
  const maarat = new Map<string, number>();
  for (const t of haku.data) {
    for (const v of t.varusteet) maarat.set(v, (maarat.get(v) ?? 0) + 1);
  }
  return (
    <Sivu otsikko="Raportti">
      <table>
        <caption>Varusteet tiloittain</caption>
        <thead><tr><th scope="col">Varuste</th><th scope="col">Tiloja</th>
        </tr></thead>
        <tbody>
          {[...maarat].sort().map(([v, n]) => (
            <tr key={v}><td>{v}</td><td>{n}</td></tr>))}
        </tbody>
      </table>
    </Sivu>
  );
}
