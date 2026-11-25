import type { Tehtava } from "../../yhteinen/logiikka.ts";

// @alku rivi
interface Props {
  tehtava: Tehtava;
  onVaihda: () => void;
  onPoista: () => void;
}

export function TehtavaRivi({ tehtava, onVaihda, onPoista }: Props) {
  const luokat = ["tehtava", tehtava.valmis && "valmis"]
    .filter(Boolean).join(" ");
  return (
    <li className={luokat}>
      <label>
        <input type="checkbox" checked={tehtava.valmis}
               onChange={onVaihda} /> <span>{tehtava.nimi}</span>
      </label>
      {tehtava.kiire === "kiireellinen" &&
        <span className="merkki">kiireellinen</span>}
      <button type="button" aria-label={`Poista ${tehtava.nimi}`}
              onClick={onPoista}>Poista</button>
    </li>
  );
}
// @loppu rivi
