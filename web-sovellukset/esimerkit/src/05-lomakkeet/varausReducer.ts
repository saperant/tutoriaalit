import { type Luonnos, type Virheet, validoi } from "./varaus.ts";

// @alku tila
export type LomakeTila =
  | { vaihe: "muokkaus"; luonnos: Luonnos; virheet: Virheet }
  | { vaihe: "lahetys"; luonnos: Luonnos }
  | { vaihe: "valmis"; varausId: string }
  | { vaihe: "virhe"; luonnos: Luonnos; viesti: string };

export type Toiminto =
  | { tyyppi: "muuta"; kentta: keyof Luonnos; arvo: string }
  | { tyyppi: "laheta"; tanaan: string }
  | { tyyppi: "onnistui"; varausId: string }
  | { tyyppi: "epaonnistui"; viesti: string };
// @loppu tila

// @alku reducer
export function varausReducer(tila: LomakeTila, t: Toiminto): LomakeTila {
  switch (t.tyyppi) {
    case "muuta": {
      if (tila.vaihe !== "muokkaus" && tila.vaihe !== "virhe") return tila;
      const arvo = t.kentta === "kesto" ? Number(t.arvo) : t.arvo;
      const luonnos = { ...tila.luonnos, [t.kentta]: arvo };
      return { vaihe: "muokkaus", luonnos, virheet: {} };
    }
    case "laheta": {
      if (tila.vaihe !== "muokkaus" && tila.vaihe !== "virhe") return tila;
      const virheet = validoi(tila.luonnos, t.tanaan);
      return Object.keys(virheet).length > 0
        ? { vaihe: "muokkaus", luonnos: tila.luonnos, virheet }
        : { vaihe: "lahetys", luonnos: tila.luonnos };
    }
    case "onnistui":
      return tila.vaihe === "lahetys"
        ? { vaihe: "valmis", varausId: t.varausId } : tila;
    case "epaonnistui":
      return tila.vaihe === "lahetys"
        ? { vaihe: "virhe", luonnos: tila.luonnos, viesti: t.viesti }
        : tila;
    default: {
      const tuntematon: never = t;     // uusi toiminto unohtui käsitellä
      return tuntematon;
    }
  }
}
// @loppu reducer
