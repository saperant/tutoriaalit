// @alku paniikki
/// Paniikki on ohjelmointivirhe, ei odotettu tilanne: invariantin
/// rikkoutuminen, jota kutsuja ei voi korjata. expect kertoo, miksi
/// arvon pitäisi olla olemassa.
fn lataa_oletusasetukset() -> Vec<(String, u16)> {
    let upotettu = "http=80\nhttps=443\nssh=22x";
    upotettu
        .lines()
        .map(|rivi| {
            let (nimi, portti) = rivi.split_once('=')
                .expect("upotetussa asetuksessa on oltava '='");
            let portti = portti.parse()
                .expect("upotetun portin on oltava luku");
            (nimi.to_string(), portti)
        })
        .collect()
}
// @loppu paniikki

fn main() {
    let asetukset = lataa_oletusasetukset();
    println!("{} palvelua", asetukset.len());
}
