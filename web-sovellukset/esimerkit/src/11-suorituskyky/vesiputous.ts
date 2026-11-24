import type { Asiakas } from "../07-verkko/asiakas.ts";

// @alku vesiputous
/** Peräkkäiset odotukset: toinen pyyntö lähtee vasta ensimmäisen
 *  valmistuttua, vaikka se ei tarvitse sen tulosta (vesiputous). */
export async function haePerakkain(api: Asiakas, idt: readonly string[]) {
  const tilat = [];
  for (const id of idt) tilat.push(await api.haeTila(id));
  return tilat;
}

/** Riippumattomat pyynnöt yhtä aikaa: kesto on hitaimman pyynnön kesto. */
export function haeRinnakkain(api: Asiakas, idt: readonly string[]) {
  return Promise.all(idt.map((id) => api.haeTila(id)));
}
// @loppu vesiputous
