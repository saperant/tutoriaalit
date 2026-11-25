<!-- @alku skripti -->
<script setup lang="ts">
import { computed, ref } from "vue";
import { suodata, type Suodatin } from "../../yhteinen/logiikka.ts";
import Lisayslomake from "./Lisayslomake.vue";
import SuodatinValinta from "./SuodatinValinta.vue";
import TehtavaRivi from "./TehtavaRivi.vue";
import { useTehtavat } from "./tila.ts";
import Yhteenveto from "./Yhteenveto.vue";

const tila = useTehtavat();
const { tehtavat, lataus } = tila;
const suodatin = ref<Suodatin>("kaikki");
// computed laskee arvon uudelleen vain, kun sen lukemat arvot muuttuvat.
const nakyvat = computed(() => suodata(tehtavat.value, suodatin.value));
const valmiita = computed(() => tehtavat.value.some((t) => t.valmis));
</script>
<!-- @loppu skripti -->

<!-- @alku pohja -->
<template>
  <header class="ylapalkki">
    <h1>Tehtävät</h1>
    <Yhteenveto />
  </header>
  <main>
    <Lisayslomake />
    <SuodatinValinta v-model="suodatin" />
    <p v-if="lataus === 'ladataan'" class="tila">Ladataan tehtäviä…</p>
    <template v-else-if="lataus === 'virhe'">
      <p class="virhe" role="alert">Tehtävien lataus epäonnistui.</p>
      <button type="button" @click="tila.lataa">Yritä uudelleen</button>
    </template>
    <template v-else>
      <p v-if="nakyvat.length === 0" class="tila">
        Ei näytettäviä tehtäviä.
      </p>
      <ul v-else class="tehtavat" aria-label="Tehtävät">
        <TehtavaRivi v-for="t in nakyvat" :key="t.id" :tehtava="t"
                     @vaihda="tila.vaihda(t.id)"
                     @poista="tila.poista(t.id)" />
      </ul>
      <button type="button" :disabled="!valmiita"
              @click="tila.poistaValmiit">Poista valmiit</button>
    </template>
  </main>
</template>
<!-- @loppu pohja -->
