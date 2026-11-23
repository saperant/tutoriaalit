fn pisin_rivi(teksti: &str) -> &str {
    teksti.lines().max_by_key(|r| r.len()).unwrap_or("")
}

fn oletusviesti() -> &'static str {
    let viesti = String::from("ei viestejä"); // @virhe
    if !viesti.is_empty() { return &viesti; } // @virhe: paikallinen arvo
    "ei viestejä"
}

fn main() {
    println!("{}", pisin_rivi("lyhyt\npitkä rivi\nkeski"));
    println!("{}", oletusviesti());
}
