import {
  Component, computed, inject, signal, viewChild, type ElementRef,
} from "@angular/core";
import { FormsModule } from "@angular/forms";
import { validoi, type Kiire } from "../../../yhteinen/logiikka";
import { TehtavatPalvelu } from "./tehtavat.palvelu";

// @alku luokka
@Component({
  selector: "app-lisayslomake",
  imports: [FormsModule],
  templateUrl: "./lisayslomake.html",
})
export class Lisayslomake {
  private readonly tila = inject(TehtavatPalvelu);
  private readonly kentta =
    viewChild.required<ElementRef<HTMLInputElement>>("kentta");

  protected readonly nimi = signal("");
  protected readonly kiire = signal<Kiire>("tavallinen");
  private readonly yritetty = signal(false);
  protected readonly virhe = computed(() => this.yritetty()
    ? validoi(this.nimi(), this.tila.tehtavat()) : null);

  protected laheta(): void {
    if (validoi(this.nimi(), this.tila.tehtavat()) === null) {
      this.tila.lisaa(this.nimi(), this.kiire());
      this.nimi.set("");
      this.yritetty.set(false);
    } else {
      this.yritetty.set(true);
    }
    this.kentta().nativeElement.focus();
  }
}
// @loppu luokka
