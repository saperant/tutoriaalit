// Komentoinjektio: komentotulkki vastaan suora ohjelmakutsu.
import { exec, execFile } from "node:child_process";
import { promisify } from "node:util";

const execP = promisify(exec);
const execFileP = promisify(execFile);

// @alku haavoittuva
export async function kokoHaavoittuva(hak: string,
                                      nimi: string): Promise<string> {
  // Komentotulkki tulkitsee merkit ; | & $( ) ` ja välilyönnit.
  const { stdout } = await execP(`wc -c ${nimi}`, { cwd: hak });
  return stdout.trim();
}
// @loppu haavoittuva

// @alku korjattu
const NIMI = /^[\w.-]{1,64}$/;

export async function koko(hak: string, nimi: string): Promise<string> {
  if (!NIMI.test(nimi) || nimi.startsWith("-")) {
    throw new Error("virheellinen tiedostonimi");
  }
  // Ei komentotulkkia: argumentit menevät ohjelmalle sellaisinaan,
  // ja "--" päättää valitsimet.
  const { stdout } = await execFileP("wc", ["-c", "--", nimi], { cwd: hak });
  return stdout.trim();
}
// @loppu korjattu
