import { type FormEvent, useEffect, useReducer, useRef } from "react";
import { type Kentta, type Luonnos, validoi } from "./varaus.ts";
import { varausReducer } from "./varausReducer.ts";

type Props = {
  tilaId: string;
  tanaan: string;
  laheta: (luonnos: Luonnos) => Promise<string>;   // palauttaa varaus-id:n
};

// @alku lomake
export function VarausLomake({ tilaId, tanaan, laheta }: Props) {
  const [tila, dispatch] = useReducer(varausReducer, {
    vaihe: "muokkaus",
    luonnos: { tilaId, paiva: tanaan, alku: "09:00", kesto: 60, aihe: "" },
    virheet: {},
  });
  const lomake = useRef<HTMLFormElement>(null);

  // Virheellisen lähetyksen jälkeen fokus ensimmäiseen virheelliseen
  // kenttään, jotta näppäimistön ja ruudunlukijan käyttäjä löytää sen.
  const virheet = tila.vaihe === "muokkaus" ? tila.virheet : {};
  useEffect(() => {
    lomake.current?.querySelector<HTMLElement>("[aria-invalid=true]")
      ?.focus();
  }, [virheet]);

  if (tila.vaihe === "valmis") {
    return <p role="status">Varaus tehty (tunnus {tila.varausId}).</p>;
  }
  const arvot = tila.luonnos;
  const lahettaa = tila.vaihe === "lahetys";

  // Käyttäjän toiminnon aiheuttama pyyntö lähetetään tapahtuman
  // käsittelijässä, ei efektissä. Tulos palaa reducerille toimintona.
  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    if (tila.vaihe !== "muokkaus" && tila.vaihe !== "virhe") return;
    dispatch({ tyyppi: "laheta", tanaan });
    if (Object.keys(validoi(tila.luonnos, tanaan)).length > 0) return;
    try {
      dispatch({ tyyppi: "onnistui", varausId: await laheta(tila.luonnos) });
    } catch (virhe) {
      dispatch({ tyyppi: "epaonnistui", viesti: virhe instanceof Error
        ? virhe.message : "Tuntematon virhe" });
    }
  }
  function kentta(nimi: Kentta, otsikko: string, tyyppi: string) {
    const virhe = virheet[nimi];
    return (
      <p>
        <label htmlFor={`varaus-${nimi}`}>{otsikko}</label>
        <input id={`varaus-${nimi}`} type={tyyppi} value={arvot[nimi]}
          aria-invalid={virhe ? true : undefined}
          aria-describedby={virhe ? `varaus-${nimi}-virhe` : undefined}
          onChange={(e) => dispatch({ tyyppi: "muuta", kentta: nimi,
                                      arvo: e.target.value })} />
        {virhe && <span id={`varaus-${nimi}-virhe`}>{virhe}</span>}
      </p>
    );
  }

  return (
    <form ref={lomake} onSubmit={onSubmit} noValidate>
      {kentta("paiva", "Päivä", "date")}
      {kentta("alku", "Alkaa", "time")}
      {kentta("kesto", "Kesto (min)", "number")}
      {kentta("aihe", "Aihe", "text")}
      {tila.vaihe === "virhe" && <p role="alert">{tila.viesti}</p>}
      <button disabled={lahettaa}>{lahettaa ? "Varataan…" : "Varaa"}</button>
    </form>
  );
}
// @loppu lomake
