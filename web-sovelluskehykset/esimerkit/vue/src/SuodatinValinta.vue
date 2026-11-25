<script setup lang="ts">
import { SUODATTIMET, type Suodatin } from "../../yhteinen/logiikka.ts";

// defineModel luo kaksisuuntaisen sidoksen: vanhempi kirjoittaa
// <SuodatinValinta v-model="suodatin" />. Pinnan alla se on props
// (modelValue) alas ja tapahtuma (update:modelValue) ylös.
const arvo = defineModel<Suodatin>({ required: true });
</script>

<template>
  <fieldset class="suodatin">
    <legend>Näytä</legend>
    <label v-for="s in SUODATTIMET" :key="s.arvo">
      <input type="radio" name="suodatin" :value="s.arvo" v-model="arvo">
      {{ s.nimi }}
    </label>
  </fieldset>
</template>
