// SQL-injektio: kysely merkkijonona vastaan parametrit.
import { DatabaseSync } from "node:sqlite";

export function tietokanta(): DatabaseSync {
  const db = new DatabaseSync(":memory:");
  db.exec(`
    CREATE TABLE tilaus (id INTEGER PRIMARY KEY, asiakas TEXT,
                         tuote TEXT, summa INTEGER);
    INSERT INTO tilaus (asiakas, tuote, summa) VALUES
      ('aino', 'Kahvinkeitin', 89), ('aino', 'Suodatinpussit', 4),
      ('ville', 'Läppäri', 1299), ('ville', 'Laukku', 59);`);
  return db;
}

type Tilaus = { id: number; tuote: string; summa: number };

// @alku haavoittuva
export function tilauksetHaavoittuva(db: DatabaseSync,
                                     asiakas: string): Tilaus[] {
  const sql = `SELECT id, tuote, summa FROM tilaus
               WHERE asiakas = '${asiakas}'`;       // VÄÄRIN
  return db.prepare(sql).all() as Tilaus[];
}
// @loppu haavoittuva

// @alku korjattu
const JARJESTYS = new Map([["summa", "summa DESC"], ["tuote", "tuote"]]);

export function tilaukset(db: DatabaseSync, asiakas: string,
                          jarjestys = "tuote"): Tilaus[] {
  // Arvot parametreina; tunnisteita (sarakkeet, suunta) ei voi
  // parametroida, joten ne valitaan sallittujen luettelosta.
  const ehto = JARJESTYS.get(jarjestys);
  if (ehto === undefined) throw new Error("tuntematon järjestys");
  return db.prepare(`SELECT id, tuote, summa FROM tilaus
                     WHERE asiakas = ? ORDER BY ${ehto}`)
    .all(asiakas) as Tilaus[];
}
// @loppu korjattu
