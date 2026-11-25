import { SUODATTIMET, type Suodatin } from "../../yhteinen/logiikka.ts";

// @alku suodatin
interface Props { arvo: Suodatin; onMuutos: (arvo: Suodatin) => void }

/** Ohjattu komponentti: arvo tulee alas, muutos ilmoitetaan ylös. */
export function SuodatinValinta({ arvo, onMuutos }: Props) {
  return (
    <fieldset className="suodatin">
      <legend>Näytä</legend>
      {SUODATTIMET.map((s) =>
        <label key={s.arvo}>
          <input type="radio" name="suodatin" value={s.arvo}
                 checked={arvo === s.arvo}
                 onChange={() => onMuutos(s.arvo)} /> {s.nimi}
        </label>)}
    </fieldset>
  );
}
// @loppu suodatin
