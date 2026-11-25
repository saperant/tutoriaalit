<script lang="ts">
  import { SUODATTIMET, type Suodatin } from "../../yhteinen/logiikka.ts";

  // $bindable sallii vanhemman sitoa arvon kaksisuuntaisesti:
  // <SuodatinValinta bind:arvo={suodatin} />.
  let { arvo = $bindable() }: { arvo: Suodatin } = $props();
</script>

<fieldset class="suodatin">
  <legend>Näytä</legend>
  {#each SUODATTIMET as s (s.arvo)}
    <label>
      <input type="radio" name="suodatin" value={s.arvo} bind:group={arvo}>
      {s.nimi}
    </label>
  {/each}
</fieldset>
