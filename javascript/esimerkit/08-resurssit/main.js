// Node 22 ei jäsennä using-määrittelyä, jolloin modulin lataus
// epäonnistuu ja tilalle ladataan try–finally-versio. Tuloste on sama.
const { raportti } = await import("./using.js").catch(
  () => import("./finally.js"),
);

console.log(raportti("SELECT saldo"));
try {
  raportti("DROP TABLE saldot");
} catch (virhe) {
  console.log("virhe:", virhe instanceof Error && virhe.message);
}
