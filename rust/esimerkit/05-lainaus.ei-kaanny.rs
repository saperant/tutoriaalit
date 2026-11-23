fn main() {
    let mut jono = vec![String::from("eka"), String::from("toka")];
    let ensimmainen = &jono[0]; // jaettu lainaus vektorin alkioon
    jono.push(String::from("kolmas")); // @virhe: lainaus on yhä käytössä
    println!("ensimmäinen: {ensimmainen}"); // lainauksen viimeinen käyttö
    jono.push(String::from("kolmas")); // nyt sallittu
    println!("{} alkiota", jono.len());
}
