use std::fmt;
use std::ops::Add;

// @alku newtype
/// Uusi tyyppi estää sekoittamasta yksiköitä: Metrit ja Sekunnit ovat
/// molemmat f64:iä, mutta kääntäjä ei hyväksy niiden sekoittamista.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
struct Metrit(f64);

#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
struct Sekunnit(f64);

impl Add for Metrit {
    type Output = Metrit;
    fn add(self, muu: Metrit) -> Metrit {
        Metrit(self.0 + muu.0)
    }
}

fn nopeus(matka: Metrit, aika: Sekunnit) -> f64 {
    matka.0 / aika.0
}
// @loppu newtype

// @alku tili
#[derive(Debug)]
struct Tili {
    omistaja: String,
    saldo_snt: i64,
}

impl Tili {
    /// Liitännäisfunktio: Rustissa ei ole muodostimia, vaan konventio
    /// `new` palauttaa valmiin olion.
    fn new(omistaja: &str) -> Self {
        Tili { omistaja: omistaja.to_string(), saldo_snt: 0 }
    }

    fn talleta(&mut self, snt: i64) {
        self.saldo_snt += snt;
    }

    fn nosta(&mut self, snt: i64) -> Result<(), String> {
        if snt > self.saldo_snt {
            return Err(format!("kate ei riitä: {}", self));
        }
        self.saldo_snt -= snt;
        Ok(())
    }
}

impl fmt::Display for Tili {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let euroa = self.saldo_snt / 100;
        let senttia = self.saldo_snt % 100;
        write!(f, "{}: {euroa},{senttia:02} €", self.omistaja)
    }
}
// @loppu tili

fn main() {
    // @alku kaytto
    let matka = Metrit(100.0) + Metrit(300.0);
    println!("{:.2} m/s", nopeus(matka, Sekunnit(50.0)));

    let mut tili = Tili::new("Ada");
    tili.talleta(12_550);
    println!("{tili}");
    if let Err(virhe) = tili.nosta(20_000) {
        println!("{virhe}");
    }
    println!("{tili:?}");
    // @loppu kaytto
}
