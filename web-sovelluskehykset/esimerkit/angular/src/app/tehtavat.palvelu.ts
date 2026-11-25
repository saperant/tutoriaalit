// Jaettu tila: palvelu, jonka Angularin riippuvuuksien injektointi
// luo kerran ja antaa jokaiselle sitä pyytävälle komponentille.
import {
  computed, effect, inject, Injectable, signal,
} from "@angular/core";
import { Title } from "@angular/platform-browser";
import * as logiikka from "../../../yhteinen/logiikka";
import type { Kiire, Lataus, Tehtava } from "../../../yhteinen/logiikka";

// @alku palvelu
@Injectable({ providedIn: "root" })
export class TehtavatPalvelu {
  private readonly otsikko = inject(Title);
  // Signaalit ovat yksityisiä: muut lukevat tilaa mutta muuttavat sitä
  // vain palvelun metodeilla.
  private readonly lista = signal<readonly Tehtava[]>([]);
  private readonly tila = signal<Lataus>("ladataan");

  readonly tehtavat = this.lista.asReadonly();
  readonly lataus = this.tila.asReadonly();
  readonly yhteenveto = computed(() =>
    this.tila() === "valmis" ? logiikka.yhteenveto(this.lista()) : "");

  constructor() {
    this.lataa();
    // Efekti ajetaan uudelleen, kun jokin sen lukema signaali muuttuu.
    effect(() => {
      if (this.tila() !== "valmis") return;
      logiikka.tallenna(localStorage, this.lista());
      this.otsikko.setTitle(logiikka.otsikko(this.lista()));
    });
  }

  lataa(): void {
    this.tila.set("ladataan");
    logiikka.haeTehtavat(localStorage).then(
      (haetut) => { this.lista.set(haetut); this.tila.set("valmis"); },
      () => { this.tila.set("virhe"); },
    );
  }

  lisaa(nimi: string, kiire: Kiire): void {
    this.lista.update((l) => logiikka.lisaa(l, nimi, kiire));
  }
  vaihda(id: number): void {
    this.lista.update((l) => logiikka.vaihda(l, id));
  }
  poista(id: number): void {
    this.lista.update((l) => logiikka.poista(l, id));
  }
  poistaValmiit(): void {
    this.lista.update((l) => logiikka.poistaValmiit(l));
  }
}
// @loppu palvelu
