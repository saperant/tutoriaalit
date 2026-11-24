// Esimerkkien yhteinen aihe: kokoustilojen varaus.

export type Tila = {
  id: string;
  nimi: string;
  kerros: number;
  paikkoja: number;
  varusteet: readonly string[];
};

export const TILAT: readonly Tila[] = [
  { id: "aalto", nimi: "Aalto", kerros: 2, paikkoja: 8,
    varusteet: ["näyttö", "videoneuvottelu"] },
  { id: "kivi", nimi: "Kivi", kerros: 2, paikkoja: 4,
    varusteet: ["näyttö"] },
  { id: "sibelius", nimi: "Sibelius", kerros: 3, paikkoja: 20,
    varusteet: ["projektori", "videoneuvottelu", "mikrofonit"] },
  { id: "tove", nimi: "Tove", kerros: 3, paikkoja: 6,
    varusteet: [] },
];
