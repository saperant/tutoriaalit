import type { Tila } from "../tilat.ts";
import { TilaKortti } from "./TilaKortti.tsx";

// @alku lista
export function TilaLista({ tilat, onVaraa }: {
  tilat: readonly Tila[];
  onVaraa: (id: string) => void;
}) {
  if (tilat.length === 0) return <p>Ei hakuehtoja vastaavia tiloja.</p>;
  return (
    <ul>
      {tilat.map((tila) => (
        <li key={tila.id}>        {/* vakaa avain datasta, ei indeksi */}
          <TilaKortti tila={tila} onVaraa={onVaraa} />
        </li>
      ))}
    </ul>
  );
}
// @loppu lista
