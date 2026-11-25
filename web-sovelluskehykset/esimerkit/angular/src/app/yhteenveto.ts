import { Component, inject } from "@angular/core";
import { TehtavatPalvelu } from "./tehtavat.palvelu";

// @alku yhteenveto
/** Pienen komponentin mallipohja mahtuu samaan tiedostoon. */
@Component({
  selector: "app-yhteenveto",
  template: `<p class="yhteenveto" role="status">{{ tila.yhteenveto() }}</p>`,
})
export class Yhteenveto {
  protected readonly tila = inject(TehtavatPalvelu);
}
// @loppu yhteenveto
