enum Taso {
    Virhe,
    Varoitus,
    Tieto,
    Jaljitys, // @virhe: uusi taso lisättiin, match-lausetta ei päivitetty
}

fn merkki(taso: &Taso) -> char {
    match taso {
        Taso::Virhe => 'E',
        Taso::Varoitus => 'W',
        Taso::Tieto => 'I',
    }
}

fn main() {
    let tasot = [Taso::Virhe, Taso::Varoitus, Taso::Tieto];
    let merkit: String = tasot.iter().map(merkki).collect();
    println!("{merkit}");
}
