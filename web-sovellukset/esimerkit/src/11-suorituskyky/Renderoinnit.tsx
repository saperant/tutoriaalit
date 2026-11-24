import { memo, useCallback, useState } from "react";
import { TilaLista } from "../04-react/TilaLista.tsx";
import { type Tila, TILAT } from "../tilat.ts";

// @alku memo
type ListaProps = {
  tilat: readonly Tila[];
  onVaraa: (id: string) => void;
  laske: () => void;            // mittaus: kutsutaan joka renderöinnissä
};
function MitattuLista({ tilat, onVaraa, laske }: ListaProps) {
  laske();
  return <TilaLista tilat={tilat} onVaraa={onVaraa} />;
}
// memo vertaa propseja (Object.is) ja ohittaa renderöinnin, jos ne
// ovat samat kuin edellisellä kerralla.
const MuistettuLista = memo(MitattuLista);

export type Versio = "tavallinen" | "memo-uusi-funktio" | "memo-useCallback";

/** Muistiinpanokenttä samassa komponentissa kuin raskas lista. */
export function Muistiinpanot({ versio, laske }: {
  versio: Versio;
  laske: () => void;
}) {
  const [teksti, setTeksti] = useState("");
  const vakaa = useCallback((id: string) => console.log(id), []);
  const uusi = (id: string) => console.log(id);  // uusi joka renderöinnissä

  return (
    <>
      <textarea aria-label="Muistiinpano" value={teksti}
                onChange={(e) => setTeksti(e.target.value)} />
      {versio === "tavallinen"
        ? <MitattuLista tilat={TILAT} onVaraa={uusi} laske={laske} />
        : <MuistettuLista tilat={TILAT} laske={laske}
            onVaraa={versio === "memo-useCallback" ? vakaa : uusi} />}
    </>
  );
}
// @loppu memo
