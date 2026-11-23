import { EventEmitter, once } from "node:events";

// @alku havainnoija
/**
 * Tilauskäsittely ilmoittaa tapahtumista havainnoijille. Tyyppiparametri
 * kuvaa tapahtumien nimet ja argumentit.
 * @extends {EventEmitter<{
 *   vastaanotettu: [id: number],
 *   lahetetty: [id: number, seurantakoodi: string],
 *   error: [virhe: Error],
 * }>}
 */
class Tilaukset extends EventEmitter {
  #seuraava = 1;

  /** @param {string} tuote */
  vastaanota(tuote) {
    const id = this.#seuraava++;
    if (tuote === "") {
      this.emit("error", new Error("tyhjä tilaus"));
      return;
    }
    this.emit("vastaanotettu", id);
    // Kuuntelijat kutsutaan synkronisesti emit-kutsun aikana.
    setTimeout(() => this.emit("lahetetty", id, `JJFI${1000 + id}`), 5);
  }
}

const tilaukset = new Tilaukset();
tilaukset.on("vastaanotettu", (id) => console.log(`#${id} vastaanotettu`));
tilaukset.on("lahetetty", (id, koodi) => console.log(`#${id} ${koodi}`));
// Ilman error-kuuntelijaa error-tapahtuma kaataa prosessin.
tilaukset.on("error", (virhe) => console.log(`virhe: ${virhe.message}`));

tilaukset.vastaanota("kahvi");
tilaukset.vastaanota("");
// @loppu havainnoija

// @alku once
// Tapahtuman odottaminen lupauksena:
const [id, koodi] = await once(tilaukset, "lahetetty");
console.log(`odotettu: #${id} ${koodi}`);
// @loppu once
