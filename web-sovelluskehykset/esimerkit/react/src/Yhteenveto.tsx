import { yhteenveto } from "../../yhteinen/logiikka.ts";
import { useTehtavat } from "./tila.tsx";

// @alku yhteenveto
/** Lukee jaettua tilaa kontekstista; ei saa mitään propseina. */
export function Yhteenveto() {
  const { tila } = useTehtavat();
  return (
    <p className="yhteenveto" role="status">
      {tila.lataus === "valmis" ? yhteenveto(tila.tehtavat) : ""}
    </p>
  );
}
// @loppu yhteenveto
