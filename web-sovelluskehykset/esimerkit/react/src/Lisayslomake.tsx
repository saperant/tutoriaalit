import { useRef, useState, type FormEvent } from "react";
import { validoi, type Kiire } from "../../yhteinen/logiikka.ts";
import { useTehtavat } from "./tila.tsx";

// @alku lomake
export function Lisayslomake() {
  const { tila, laheta } = useTehtavat();
  const [nimi, setNimi] = useState("");
  const [kiire, setKiire] = useState<Kiire>("tavallinen");
  const [yritetty, setYritetty] = useState(false);
  const kentta = useRef<HTMLInputElement>(null);
  // Virhe on johdettu tieto, ja se näytetään vasta lähetysyrityksen
  // jälkeen.
  const virhe = yritetty ? validoi(nimi, tila.tehtavat) : null;

  function kasittele(tapahtuma: FormEvent) {
    tapahtuma.preventDefault();
    if (validoi(nimi, tila.tehtavat) === null) {
      laheta({ tyyppi: "lisaa", nimi, kiire });
      setNimi("");
      setYritetty(false);
    } else {
      setYritetty(true);
    }
    kentta.current?.focus();
  }

  return (
    <form className="lisays" noValidate aria-label="Uusi tehtävä"
          onSubmit={kasittele}>
      <label htmlFor="nimi">Tehtävä</label>
      <input id="nimi" name="nimi" ref={kentta} autoComplete="off"
             value={nimi} onChange={(e) => setNimi(e.target.value)}
             aria-invalid={virhe !== null} aria-describedby="nimi-virhe" />
      <label htmlFor="kiire">Kiireellisyys</label>
      <select id="kiire" name="kiire" value={kiire}
              onChange={(e) => setKiire(e.target.value as Kiire)}>
        <option value="tavallinen">Tavallinen</option>
        <option value="kiireellinen">Kiireellinen</option>
      </select>
      <button type="submit">Lisää</button>
      <p id="nimi-virhe" className="virhe" role="alert">{virhe}</p>
    </form>
  );
}
// @loppu lomake
