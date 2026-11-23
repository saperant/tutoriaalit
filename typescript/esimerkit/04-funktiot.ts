// Funktiotyypit, valinnaiset ja oletusparametrit, ylikuormitus.
type Muunnin = (euroa: number) => string;

const suomeksi: Muunnin = (e) => `${e.toFixed(2).replace(".", ",")} €`;

function hinta(euroa: number, alv = 0.255, muoto: Muunnin = suomeksi) {
  return muoto(euroa * (1 + alv)); // paluutyyppi päätellään: string
}

// Ylikuormitus: eri syötetyypeille eri paluutyyppi.
function jasenna(syote: string): number;
function jasenna(syote: readonly string[]): number[];
function jasenna(syote: string | readonly string[]): number | number[] {
  return typeof syote === "string" ? Number(syote) : syote.map(Number);
}

const yksi = jasenna("12"); // number
const monta = jasenna(["1", "2"]); // number[]
console.log(hinta(10), hinta(10, 0.14), yksi + 1, monta.length);

// Jäännösparametri ja monikkotyyppi.
function loki(taso: "info" | "varoitus", ...osat: unknown[]): void {
  console.log(`[${taso}]`, ...osat);
}
loki("info", "tilaus", 1042, { rivit: 3 });
