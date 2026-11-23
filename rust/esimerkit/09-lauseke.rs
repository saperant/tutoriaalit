use std::fmt;

// @alku puu
/// Rekursiivinen tyyppi tarvitsee epäsuoruuden: Box<T> on yksi
/// kekovaraus, jonka omistaja vapauttaa (vrt. std::unique_ptr).
#[derive(Debug, Clone, PartialEq)]
enum Lauseke {
    Luku(f64),
    Muuttuja(String),
    Summa(Box<Lauseke>, Box<Lauseke>),
    Tulo(Box<Lauseke>, Box<Lauseke>),
}

use Lauseke::*;

fn summa(a: Lauseke, b: Lauseke) -> Lauseke {
    Summa(Box::new(a), Box::new(b))
}

fn tulo(a: Lauseke, b: Lauseke) -> Lauseke {
    Tulo(Box::new(a), Box::new(b))
}
// @loppu puu

// @alku sievennys
/// Sievennys kuluttaa vanhan puun ja rakentaa uuden. Box-sisällön voi
/// siirtää ulos (*laatikko), joten solmuja ei kopioida.
fn sievenna(lauseke: Lauseke) -> Lauseke {
    match lauseke {
        Summa(a, b) => match (sievenna(*a), sievenna(*b)) {
            (Luku(x), Luku(y)) => Luku(x + y),
            (Luku(z), e) | (e, Luku(z)) if z == 0.0 => e,
            (a, b) => summa(a, b),
        },
        Tulo(a, b) => match (sievenna(*a), sievenna(*b)) {
            (Luku(x), Luku(y)) => Luku(x * y),
            (Luku(z), _) | (_, Luku(z)) if z == 0.0 => Luku(0.0),
            (Luku(y), e) | (e, Luku(y)) if y == 1.0 => e,
            (a, b) => tulo(a, b),
        },
        muu => muu,
    }
}
// @loppu sievennys

impl fmt::Display for Lauseke {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Luku(x) => write!(f, "{x}"),
            Muuttuja(nimi) => write!(f, "{nimi}"),
            Summa(a, b) => write!(f, "({a} + {b})"),
            Tulo(a, b) => write!(f, "{a} * {b}"),
        }
    }
}

fn main() {
    // @alku kaytto
    let x = || Muuttuja("x".to_string());
    let lauseke = summa(
        tulo(Luku(1.0), x()),
        tulo(summa(Luku(2.0), Luku(-2.0)), x()),
    );
    println!("{lauseke}");
    println!("{}", sievenna(lauseke.clone()));
    let lauseke2 = tulo(summa(x(), Luku(0.0)), summa(Luku(1.5), Luku(2.0)));
    println!("{lauseke2}  =>  {}", sievenna(lauseke2.clone()));
    println!("{}", std::mem::size_of::<Lauseke>());
    // @loppu kaytto
}
