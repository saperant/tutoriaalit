import { Component, computed, inject, signal } from "@angular/core";
import { suodata, type Suodatin } from "../../../yhteinen/logiikka";
import { Lisayslomake } from "./lisayslomake";
import { SuodatinValinta } from "./suodatin-valinta";
import { TehtavaRivi } from "./tehtava-rivi";
import { TehtavatPalvelu } from "./tehtavat.palvelu";
import { Yhteenveto } from "./yhteenveto";

// @alku luokka
// Luokka on näkymän tietomalli: tila ja toiminnot. Miltä se näyttää,
// kerrotaan erillisessä mallipohjassa (sovellus.html).
@Component({
  selector: "app-juuri",
  imports: [Lisayslomake, SuodatinValinta, TehtavaRivi, Yhteenveto],
  templateUrl: "./sovellus.html",
})
export class Sovellus {
  protected readonly tila = inject(TehtavatPalvelu);
  protected readonly suodatin = signal<Suodatin>("kaikki");
  protected readonly nakyvat = computed(() =>
    suodata(this.tila.tehtavat(), this.suodatin()));
  protected readonly valmiita = computed(() =>
    this.tila.tehtavat().some((t) => t.valmis));
}
// @loppu luokka
