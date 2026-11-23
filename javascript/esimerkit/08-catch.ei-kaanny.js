try {
  JSON.parse("{ rikki");
} catch (virhe) {
  console.log(virhe.message); // @virhe
  // catch-muuttujan tyyppi on unknown: heitetty arvo voi olla mitä vain.
  console.log(virhe instanceof SyntaxError ? virhe.name : String(virhe));
}
