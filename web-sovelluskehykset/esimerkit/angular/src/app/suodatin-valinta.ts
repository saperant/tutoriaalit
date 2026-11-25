import { Component, model } from "@angular/core";
import { SUODATTIMET, type Suodatin } from "../../../yhteinen/logiikka";

// model() on kaksisuuntainen syöte: vanhempi kirjoittaa
// <app-suodatin-valinta [(arvo)]="suodatin" />. Pinnan alla se on
// syöte (arvo) alas ja tapahtuma (arvoChange) ylös.
@Component({
  selector: "app-suodatin-valinta",
  templateUrl: "./suodatin-valinta.html",
})
export class SuodatinValinta {
  readonly arvo = model.required<Suodatin>();
  protected readonly suodattimet = SUODATTIMET;
}
