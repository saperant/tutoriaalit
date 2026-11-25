<!-- @alku skripti -->
<script lang="ts">
  import { suodata, type Suodatin } from "../../yhteinen/logiikka.ts";
  import Lisayslomake from "./Lisayslomake.svelte";
  import SuodatinValinta from "./SuodatinValinta.svelte";
  import TehtavaRivi from "./TehtavaRivi.svelte";
  import { tehtavat } from "./tila.svelte.ts";
  import Yhteenveto from "./Yhteenveto.svelte";

  let suodatin = $state<Suodatin>("kaikki");
  const nakyvat = $derived(suodata(tehtavat.lista, suodatin));
  const valmiita = $derived(tehtavat.lista.some((t) => t.valmis));

  tehtavat.lataa();
  // Efekti ajetaan uudelleen, kun jokin sen lukema tila muuttuu.
  $effect(() => tehtavat.tallenna());
</script>
<!-- @loppu skripti -->

<!-- @alku pohja -->
<header class="ylapalkki">
  <h1>Tehtävät</h1>
  <Yhteenveto />
</header>
<main>
  <Lisayslomake />
  <SuodatinValinta bind:arvo={suodatin} />
  {#if tehtavat.lataus === "ladataan"}
    <p class="tila">Ladataan tehtäviä…</p>
  {:else if tehtavat.lataus === "virhe"}
    <p class="virhe" role="alert">Tehtävien lataus epäonnistui.</p>
    <button type="button" onclick={tehtavat.lataa}>Yritä uudelleen</button>
  {:else}
    {#if nakyvat.length === 0}
      <p class="tila">Ei näytettäviä tehtäviä.</p>
    {:else}
      <ul class="tehtavat" aria-label="Tehtävät">
        {#each nakyvat as t (t.id)}
          <TehtavaRivi tehtava={t}
                       onvaihda={() => tehtavat.vaihda(t.id)}
                       onpoista={() => tehtavat.poista(t.id)} />
        {/each}
      </ul>
    {/if}
    <button type="button" disabled={!valmiita}
            onclick={tehtavat.poistaValmiit}>Poista valmiit</button>
  {/if}
</main>
<!-- @loppu pohja -->
