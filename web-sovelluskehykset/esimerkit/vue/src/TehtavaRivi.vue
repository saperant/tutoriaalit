<script setup lang="ts">
import type { Tehtava } from "../../yhteinen/logiikka.ts";

// Rajapinta vanhempaan: tieto alas (props), tapahtumat ylös (emits).
defineProps<{ tehtava: Tehtava }>();
defineEmits<{ vaihda: []; poista: [] }>();
</script>

<template>
  <li class="tehtava" :class="{ valmis: tehtava.valmis }">
    <label>
      <input type="checkbox" :checked="tehtava.valmis"
             @change="$emit('vaihda')">
      <span>{{ tehtava.nimi }}</span>
    </label>
    <span v-if="tehtava.kiire === 'kiireellinen'" class="merkki">
      kiireellinen
    </span>
    <button type="button" :aria-label="`Poista ${tehtava.nimi}`"
            @click="$emit('poista')">Poista</button>
  </li>
</template>
