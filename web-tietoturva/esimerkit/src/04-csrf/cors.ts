// CORS-otsakkeet: alkuperän heijastus vastaan sallittujen luettelo.

// @alku haavoittuva
// VÄÄRIN: mikä tahansa alkuperä kelpaa, ja evästeet kulkevat mukana.
// Hyökkääjän sivu voi lukea kirjautuneen käyttäjän vastaukset.
export function corsHaavoittuva(origin: string | undefined):
    Record<string, string> {
  if (!origin) return {};
  return { "Access-Control-Allow-Origin": origin,
           "Access-Control-Allow-Credentials": "true" };
}
// @loppu haavoittuva

// @alku korjattu
// Täsmällinen vertailu luetteloon: ei alkuosia, ei säännöllisiä
// lausekkeita eikä "null"-alkuperää. Vary kertoo välimuistille, että
// vastaus riippuu Origin-otsakkeesta.
export function cors(origin: string | undefined, sallitut: Set<string>):
    Record<string, string> {
  if (!origin || !sallitut.has(origin)) return { Vary: "Origin" };
  return { "Access-Control-Allow-Origin": origin,
           "Access-Control-Allow-Credentials": "true",
           Vary: "Origin" };
}
// @loppu korjattu
