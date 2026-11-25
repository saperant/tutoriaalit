<!-- @alku skripti -->
<script setup lang="ts">
import { computed, ref, useTemplateRef } from "vue";
import { validoi, type Kiire } from "../../yhteinen/logiikka.ts";
import { useTehtavat } from "./tila.ts";

const tila = useTehtavat();
const nimi = ref("");
const kiire = ref<Kiire>("tavallinen");
const yritetty = ref(false);
const kentta = useTemplateRef("kentta");
const virhe = computed(() =>
  yritetty.value ? validoi(nimi.value, tila.tehtavat.value) : null);

function laheta() {
  if (validoi(nimi.value, tila.tehtavat.value) === null) {
    tila.lisaa(nimi.value, kiire.value);
    nimi.value = "";
    yritetty.value = false;
  } else {
    yritetty.value = true;
  }
  kentta.value?.focus();
}
</script>
<!-- @loppu skripti -->

<!-- @alku pohja -->
<template>
  <form class="lisays" novalidate aria-label="Uusi tehtävä"
        @submit.prevent="laheta">
    <label for="nimi">Tehtävä</label>
    <input id="nimi" ref="kentta" v-model="nimi" name="nimi"
           autocomplete="off" :aria-invalid="virhe !== null"
           aria-describedby="nimi-virhe">
    <label for="kiire">Kiireellisyys</label>
    <select id="kiire" v-model="kiire" name="kiire">
      <option value="tavallinen">Tavallinen</option>
      <option value="kiireellinen">Kiireellinen</option>
    </select>
    <button type="submit">Lisää</button>
    <p id="nimi-virhe" class="virhe" role="alert">{{ virhe }}</p>
  </form>
</template>
<!-- @loppu pohja -->
