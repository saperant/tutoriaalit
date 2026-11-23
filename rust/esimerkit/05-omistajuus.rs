// @alku funktiot
/// Ottaa omistuksen: kutsujan muuttuja ei ole enää käytettävissä.
fn arkistoi(raportti: String) -> usize {
    raportti.len()
} // raportti vapautetaan tässä, kuten C++:n hajottimessa

/// Lainaa lukemista varten: kutsuja säilyttää omistuksen.
fn otsikko(raportti: &str) -> &str {
    raportti.lines().next().unwrap_or("")
}

/// Lainaa muokkaamista varten: vain yksi muokkaava lainaus kerrallaan.
fn lisaa_allekirjoitus(raportti: &mut String, nimi: &str) {
    raportti.push_str("\n-- ");
    raportti.push_str(nimi);
}
// @loppu funktiot

fn main() {
    // @alku kaytto
    let mut raportti = String::from("Viikkoraportti\nKaikki kunnossa.");
    println!("otsikko: {}", otsikko(&raportti));
    lisaa_allekirjoitus(&mut raportti, "Ada");

    let kopio = raportti.clone(); // eksplisiittinen, näkyvä kopio
    let tavuja = arkistoi(raportti); // omistus siirtyy
    println!("arkistoitiin {tavuja} tavua");
    println!("kopio säilyi:\n{kopio}");
    // @loppu kaytto

    // @alku copy
    // Pienet arvotyypit (kokonaisluvut, f64, bool, char) ovat Copy:
    // sijoitus kopioi, eikä alkuperäinen muutu käyttökelvottomaksi.
    let a = 5;
    let b = a;
    println!("{a} {b}");
    // @loppu copy
}
