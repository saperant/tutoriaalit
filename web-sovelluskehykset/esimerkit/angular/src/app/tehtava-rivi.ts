import { Component, input, output } from "@angular/core";
import type { Tehtava } from "../../../yhteinen/logiikka";

// @alku rivi
// Valitsin on attribuutti, koska <ul>:n lapsen on oltava <li>: komponentti
// liitetään olemassa olevaan elementtiin (<li app-tehtava-rivi>).
// Isäntäelementin luokat sidotaan host-kentässä.
@Component({
  selector: "li[app-tehtava-rivi]",
  templateUrl: "./tehtava-rivi.html",
  host: { class: "tehtava", "[class.valmis]": "tehtava().valmis" },
})
export class TehtavaRivi {
  readonly tehtava = input.required<Tehtava>();    // tieto alas
  readonly vaihda = output<void>();                // tapahtumat ylös
  readonly poista = output<void>();
}
// @loppu rivi
