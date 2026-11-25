<script lang="ts">
  import type { Tehtava } from "../../yhteinen/logiikka.ts";

  // Rajapinta vanhempaan on yksi props-olio: tieto ja takaisinkutsut.
  interface Props {
    tehtava: Tehtava;
    onvaihda: () => void;
    onpoista: () => void;
  }
  const { tehtava, onvaihda, onpoista }: Props = $props();
</script>

<li class={["tehtava", tehtava.valmis && "valmis"]}>
  <label>
    <input type="checkbox" checked={tehtava.valmis} onchange={onvaihda}>
    <span>{tehtava.nimi}</span>
  </label>
  {#if tehtava.kiire === "kiireellinen"}
    <span class="merkki">kiireellinen</span>
  {/if}
  <button type="button" aria-label={`Poista ${tehtava.nimi}`}
          onclick={onpoista}>Poista</button>
</li>
