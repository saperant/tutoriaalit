use std::f64::consts::PI;

// @alku piirre
trait Muoto {
    fn ala(&self) -> f64;
    fn nimi(&self) -> String {
        "muoto".to_string() // oletustoteutus
    }
}

struct Ympyra {
    sade: f64,
}

struct Suorakulmio {
    leveys: f64,
    korkeus: f64,
}

impl Muoto for Ympyra {
    fn ala(&self) -> f64 {
        PI * self.sade * self.sade
    }
    fn nimi(&self) -> String {
        format!("ympyrä r={}", self.sade)
    }
}

impl Muoto for Suorakulmio {
    fn ala(&self) -> f64 {
        self.leveys * self.korkeus
    }
}
// @loppu piirre

// @alku staattinen
/// Staattinen sidonta: kääntäjä tuottaa oman version kullekin tyypille
/// (monomorfisaatio), kuten C++:n mallit. Ei ajonaikaista hintaa.
fn tulosta_ala<M: Muoto>(muoto: &M) {
    println!("{}: {:.2}", muoto.nimi(), muoto.ala());
}
// @loppu staattinen

// @alku dynaaminen
/// Dynaaminen sidonta: yksi versio, kutsu virtuaalitaulun kautta.
/// Mahdollistaa eri tyyppien kokoamisen samaan vektoriin.
fn yhteisala(muodot: &[Box<dyn Muoto>]) -> f64 {
    muodot.iter().map(|m| m.ala()).sum()
}
// @loppu dynaaminen

fn main() {
    // @alku kaytto
    tulosta_ala(&Ympyra { sade: 1.0 });
    tulosta_ala(&Suorakulmio { leveys: 2.0, korkeus: 3.0 });

    let muodot: Vec<Box<dyn Muoto>> = vec![
        Box::new(Ympyra { sade: 2.0 }),
        Box::new(Suorakulmio { leveys: 4.0, korkeus: 0.5 }),
    ];
    println!("yhteensä {:.2}", yhteisala(&muodot));
    // @loppu kaytto
}
