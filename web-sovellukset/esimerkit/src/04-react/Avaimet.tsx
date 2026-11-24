import { useState } from "react";

// @alku avaimet
type Rivi = { id: number; nimi: string };

/** Osallistujalista, jossa jokaisella rivillä on oma muistiinpanokenttä
 *  (komponentin sisäinen tila). Avain ratkaisee, kenelle tila kuuluu. */
export function Osallistujat({ alku, avain }: {
  alku: readonly Rivi[];
  avain: "id" | "indeksi";
}) {
  const [rivit, setRivit] = useState(alku);
  return (
    <ul>
      {rivit.map((r, i) => (
        <li key={avain === "id" ? r.id : i}>
          <Muistiinpano nimi={r.nimi} />
          <button type="button"
                  onClick={() => setRivit(rivit.filter((x) => x !== r))}>
            Poista {r.nimi}
          </button>
        </li>
      ))}
    </ul>
  );
}

function Muistiinpano({ nimi }: { nimi: string }) {
  const [teksti, setTeksti] = useState("");
  return (
    <label>
      {nimi}{" "}
      <input value={teksti} onChange={(e) => setTeksti(e.target.value)} />
    </label>
  );
}
// @loppu avaimet
