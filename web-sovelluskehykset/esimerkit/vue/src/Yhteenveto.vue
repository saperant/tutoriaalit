<script setup lang="ts">
import { computed } from "vue";
import { yhteenveto } from "../../yhteinen/logiikka.ts";
import { useTehtavat } from "./tila.ts";

const { tehtavat, lataus } = useTehtavat();
const teksti = computed(() =>
  lataus.value === "valmis" ? yhteenveto(tehtavat.value) : "");
</script>

<template>
  <p class="yhteenveto" role="status">{{ teksti }}</p>
</template>
