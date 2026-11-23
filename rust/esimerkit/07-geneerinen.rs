use std::fmt::Display;

// @alku rengas
/// Rengaspuskuri, joka säilyttää N viimeisintä arvoa.
struct Rengas<T> {
    alkiot: Vec<Option<T>>,
    seuraava: usize,
}

impl<T: Clone> Rengas<T> {
    fn new(koko: usize) -> Self {
        assert!(koko > 0, "koon on oltava positiivinen");
        Rengas { alkiot: vec![None; koko], seuraava: 0 }
    }

    fn lisaa(&mut self, arvo: T) {
        let koko = self.alkiot.len();
        self.alkiot[self.seuraava] = Some(arvo);
        self.seuraava = (self.seuraava + 1) % koko;
    }

    /// Vanhimmasta uusimpaan.
    fn iter(&self) -> impl Iterator<Item = &T> + '_ {
        let (uudet, vanhat) = self.alkiot.split_at(self.seuraava);
        vanhat.iter().chain(uudet).flatten()
    }
}
// @loppu rengas

// @alku rajat
/// Piirrerajat kertovat, mitä tyypiltä vaaditaan; virheilmoitus syntyy
/// kutsukohdassa eikä mallin sisällä (vrt. C++:n konseptit).
fn raportoi<T>(otsikko: &str, arvot: impl Iterator<Item = T>) -> String
where
    T: Display,
{
    let osat: Vec<String> = arvot.map(|a| a.to_string()).collect();
    format!("{otsikko}: [{}]", osat.join(", "))
}
// @loppu rajat

// @alku iterator
/// Oma iteraattori: Fibonaccin luvut, kunnes u64 ylivuotaisi.
struct Fibonacci {
    a: u64,
    b: u64,
}

impl Iterator for Fibonacci {
    type Item = u64;
    fn next(&mut self) -> Option<u64> {
        let tulos = self.a;
        let seuraava = self.a.checked_add(self.b)?;
        self.a = self.b;
        self.b = seuraava;
        Some(tulos)
    }
}
// @loppu iterator

fn main() {
    // @alku kaytto
    let mut viimeiset = Rengas::new(3);
    for lampotila in [18, 19, 21, 24, 22] {
        viimeiset.lisaa(lampotila);
    }
    println!("{}", raportoi("viimeiset", viimeiset.iter()));

    let fib = Fibonacci { a: 0, b: 1 };
    println!("{}", raportoi("fib", fib.skip(10).take(5)));
    let kaikki = Fibonacci { a: 0, b: 1 }.count();
    println!("u64:ään mahtuu {kaikki} Fibonaccin lukua");
    // @loppu kaytto
}
