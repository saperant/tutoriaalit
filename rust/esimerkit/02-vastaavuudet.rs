use std::collections::HashMap;

// @alku option
/// Palauttaa käyttäjän sähköpostin, jos käyttäjä on olemassa.
/// C:ssä paluuarvo olisi osoitin, joka voi olla NULL.
fn sahkoposti(kayttajat: &HashMap<u32, String>, id: u32) -> Option<&str> {
    kayttajat.get(&id).map(String::as_str)
}
// @loppu option

// @alku result
/// Jäsentää portin numeron. C:ssä virhe ilmaistaisiin paluuarvolla ja
/// errno-muuttujalla, C++:ssa usein poikkeuksella.
fn portti(teksti: &str) -> Result<u16, String> {
    let arvo: u16 = teksti
        .trim()
        .parse()
        .map_err(|e| format!("'{teksti}' ei ole portti: {e}"))?;
    if arvo == 0 {
        return Err("portti 0 on varattu".to_string());
    }
    Ok(arvo)
}
// @loppu result

fn main() {
    // @alku kaytto
    let mut kayttajat = HashMap::new();
    kayttajat.insert(7, String::from("ada@example.org"));

    match sahkoposti(&kayttajat, 7) {
        Some(osoite) => println!("käyttäjä 7: {osoite}"),
        None => println!("käyttäjää 7 ei ole"),
    }
    // Option ei muutu huomaamatta arvoksi: puuttuminen on käsiteltävä.
    let oletus = sahkoposti(&kayttajat, 8).unwrap_or("(ei osoitetta)");
    println!("käyttäjä 8: {oletus}");

    for syote in ["8080", "0", "http"] {
        match portti(syote) {
            Ok(p) => println!("portti {p}"),
            Err(virhe) => println!("virhe: {virhe}"),
        }
    }
    // @loppu kaytto
}
