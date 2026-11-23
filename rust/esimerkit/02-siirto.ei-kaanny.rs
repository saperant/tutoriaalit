fn tallenna(rivi: String) -> usize {
    // Funktio ottaa merkkijonon omistukseensa.
    rivi.len()
}

fn main() {
    let rivi = String::from("mittaus 42");
    let pituus = tallenna(rivi);
    println!("{rivi}"); // @virhe: arvo on siirretty funktiolle
    println!("tallennettiin {pituus} tavua");
}
