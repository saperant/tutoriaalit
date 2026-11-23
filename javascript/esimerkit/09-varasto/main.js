import muotoileTilaus from "./muotoilu.js";
import { luoVarasto, TILAUSRAJA } from "./varasto.js";

const varasto = luoVarasto([["kahvi", 12], ["tee", 6], ["mehu", 2]]);
varasto.kirjaa("tee", -3);
varasto.kirjaa("kahvi", -4);

try {
  varasto.kirjaa("mehu", -5);
} catch (virhe) {
  console.log(virhe instanceof RangeError ? virhe.message : virhe);
}

console.log(`Tilausraja ${TILAUSRAJA}:`);
console.log(muotoileTilaus(varasto.tilattavat()));
