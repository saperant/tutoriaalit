import { createApp } from "vue";
import "../../yhteinen/tyyli.css";
import Sovellus from "./Sovellus.vue";
import { luoTehtavat, TEHTAVAT } from "./tila.ts";

// provide tekee tilasta saatavan kaikille sovelluksen komponenteille.
createApp(Sovellus).provide(TEHTAVAT, luoTehtavat()).mount("#juuri");
