// @alku vartija
/// Pitää kirjaa avoimista resursseista ja ilmoittaa vapautuksesta.
struct Yhteys {
    nimi: String,
}

impl Yhteys {
    fn avaa(nimi: &str) -> Self {
        println!("  avataan {nimi}");
        Yhteys { nimi: nimi.to_string() }
    }
}

impl Drop for Yhteys {
    fn drop(&mut self) {
        println!("  suljetaan {}", self.nimi);
    }
}
// @loppu vartija

fn main() {
    // @alku jarjestys
    println!("lohko alkaa");
    {
        let _a = Yhteys::avaa("tietokanta");
        let _b = Yhteys::avaa("välimuisti");
        println!("  työtä");
    } // vapautetaan käänteisessä järjestyksessä: välimuisti, tietokanta
    println!("lohko päättyi");

    let c = Yhteys::avaa("loki");
    drop(c); // vapautus heti, ei vasta lohkon lopussa
    println!("loki suljettu ennen ohjelman loppua");
    // @loppu jarjestys

    // @alku take
    // Option::take siirtää arvon ulos ja jättää tilalle None:n.
    let mut aktiivinen = Some(Yhteys::avaa("istunto"));
    if let Some(yhteys) = aktiivinen.take() {
        println!("  siirrettiin {}", yhteys.nimi);
    }
    println!("aktiivinen on tyhjä: {}", aktiivinen.is_none());
    // @loppu take
}
