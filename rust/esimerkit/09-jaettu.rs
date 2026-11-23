use std::cell::RefCell;
use std::rc::{Rc, Weak};

// @alku hakemisto
/// Hakemistopuu: vanhempi omistaa lapsensa (Rc), lapsi viittaa
/// vanhempaansa heikosti (Weak), jotta viittaussykli ei estä
/// vapauttamista. RefCell siirtää lainaussääntöjen tarkistuksen
/// ajonaikaiseksi.
#[derive(Debug)]
struct Hakemisto {
    nimi: String,
    vanhempi: RefCell<Weak<Hakemisto>>,
    lapset: RefCell<Vec<Rc<Hakemisto>>>,
}

impl Hakemisto {
    fn new(nimi: &str) -> Rc<Hakemisto> {
        Rc::new(Hakemisto {
            nimi: nimi.to_string(),
            vanhempi: RefCell::new(Weak::new()),
            lapset: RefCell::new(Vec::new()),
        })
    }

    fn lisaa(vanhempi: &Rc<Hakemisto>, lapsi: Rc<Hakemisto>) {
        *lapsi.vanhempi.borrow_mut() = Rc::downgrade(vanhempi);
        vanhempi.lapset.borrow_mut().push(lapsi);
    }

    /// Polku juuresta: kuljetaan Weak-viittauksia ylöspäin.
    fn polku(&self) -> String {
        match self.vanhempi.borrow().upgrade() {
            Some(v) => format!("{}/{}", v.polku(), self.nimi),
            None => self.nimi.clone(),
        }
    }
}
// @loppu hakemisto

fn main() {
    // @alku kaytto
    let juuri = Hakemisto::new("");
    let koti = Hakemisto::new("home");
    let ada = Hakemisto::new("ada");
    Hakemisto::lisaa(&juuri, Rc::clone(&koti));
    Hakemisto::lisaa(&koti, Rc::clone(&ada));
    println!("{}", ada.polku());
    println!("koti: vahvat {}, heikot {}",
             Rc::strong_count(&koti), Rc::weak_count(&koti));
    println!("juuren lapsia: {}", juuri.lapset.borrow().len());

    drop(juuri);
    drop(koti);
    // Juuren vapautus pudottaa lapsivektorin, jolloin kodin viimeinen
    // vahva viite katoaa. Ada elää yhä, mutta sen vanhempi ei.
    println!("{}", ada.polku());
    println!("vanhempi elossa: {}",
             ada.vanhempi.borrow().upgrade().is_some());
    // @loppu kaytto
}
