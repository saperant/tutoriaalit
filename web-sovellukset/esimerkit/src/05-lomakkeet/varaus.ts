// @alku tyypit
export type Luonnos = {
  tilaId: string;
  paiva: string;      // VVVV-KK-PP, kuten <input type="date">
  alku: string;       // TT:MM
  kesto: number;      // minuutteja
  aihe: string;
};

export type Kentta = "paiva" | "alku" | "kesto" | "aihe";
export type Virheet = Partial<Record<Kentta, string>>;
// @loppu tyypit

// @alku validoi
/** Sama validointi ajetaan selaimessa ja palvelimella. Selaimen
 *  tarkistus palvelee käyttäjää, palvelimen tarkistus suojaa dataa. */
export function validoi(l: Luonnos, tanaan: string): Virheet {
  const virheet: Virheet = {};
  if (!/^\d{4}-\d{2}-\d{2}$/.test(l.paiva)) {
    virheet.paiva = "Valitse päivä.";
  } else if (l.paiva < tanaan) {
    virheet.paiva = "Päivä on menneisyydessä.";
  }
  if (!/^\d{2}:\d{2}$/.test(l.alku)) virheet.alku = "Anna alkamisaika.";
  if (!Number.isInteger(l.kesto) || l.kesto < 15 || l.kesto > 480) {
    virheet.kesto = "Keston on oltava 15–480 minuuttia.";
  }
  if (l.aihe.trim().length < 3) {
    virheet.aihe = "Kirjoita aihe (väh. 3 merkkiä).";
  }
  return virheet;
}
// @loppu validoi
