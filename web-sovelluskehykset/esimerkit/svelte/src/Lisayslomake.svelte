<!-- @alku skripti -->
<script lang="ts">
  import { validoi, type Kiire } from "../../yhteinen/logiikka.ts";
  import { tehtavat } from "./tila.svelte.ts";

  let nimi = $state("");
  let kiire = $state<Kiire>("tavallinen");
  let yritetty = $state(false);
  let kentta: HTMLInputElement;
  const virhe = $derived(yritetty ? validoi(nimi, tehtavat.lista) : null);

  function laheta(tapahtuma: SubmitEvent) {
    tapahtuma.preventDefault();
    if (validoi(nimi, tehtavat.lista) === null) {
      tehtavat.lisaa(nimi, kiire);
      nimi = "";
      yritetty = false;
    } else {
      yritetty = true;
    }
    kentta.focus();
  }
</script>
<!-- @loppu skripti -->

<!-- @alku pohja -->
<form class="lisays" novalidate aria-label="Uusi tehtävä" onsubmit={laheta}>
  <label for="nimi">Tehtävä</label>
  <input id="nimi" name="nimi" autocomplete="off" bind:value={nimi}
         bind:this={kentta} aria-invalid={virhe !== null}
         aria-describedby="nimi-virhe">
  <label for="kiire">Kiireellisyys</label>
  <select id="kiire" name="kiire" bind:value={kiire}>
    <option value="tavallinen">Tavallinen</option>
    <option value="kiireellinen">Kiireellinen</option>
  </select>
  <button type="submit">Lisää</button>
  <p id="nimi-virhe" class="virhe" role="alert">{virhe}</p>
</form>
<!-- @loppu pohja -->
