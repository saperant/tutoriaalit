// @alku jarjestys
console.log("1 synkroninen alku");
setTimeout(() => console.log("7 ajastin (makrotehtävä)"), 0);
Promise.resolve().then(() => console.log("3 lupaus (mikrotehtävä)"));
queueMicrotask(() => console.log("4 queueMicrotask"));
console.log("2 synkroninen loppu");
// @loppu jarjestys

// @alku tyhjennys
// Mikrotehtävät ajetaan loppuun ennen seuraavaa makrotehtävää: lupaus,
// jonka käsittelijä lisää uuden mikrotehtävän, ohittaa ajastimen.
setTimeout(() => console.log("8 toinen ajastin"), 0);
Promise.resolve()
  .then(() => console.log("5 ketju 1"))
  .then(() => console.log("6 ketju 2"));
// @loppu tyhjennys
