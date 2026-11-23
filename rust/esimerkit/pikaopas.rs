use std::cell::RefCell;
use std::collections::HashMap;
use std::fmt;
use std::rc::Rc;
use std::sync::{Arc, Mutex};
use std::thread;

// @alku tyypit
const RAJA: u32 = 1_000; // käännösaikainen vakio, tyyppi pakollinen
static NIMI: &str = "pikaopas"; // yksi osoite koko ohjelmalle
// @loppu tyypit

// @alku omat
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, PartialOrd, Ord)]
enum Taso {
    Info,
    Varoitus,
    Virhe,
}

#[derive(Debug, Clone)]
struct Tapahtuma {
    taso: Taso,
    viesti: String,
}

impl Tapahtuma {
    fn new(taso: Taso, viesti: impl Into<String>) -> Self {
        Tapahtuma { taso, viesti: viesti.into() }
    }
}

impl fmt::Display for Tapahtuma {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "[{:?}] {}", self.taso, self.viesti)
    }
}

trait Suodatin {
    fn hyvaksyy(&self, t: &Tapahtuma) -> bool;
}

struct VahintaanTaso(Taso);

impl Suodatin for VahintaanTaso {
    fn hyvaksyy(&self, t: &Tapahtuma) -> bool {
        t.taso >= self.0
    }
}

fn suodata<'a, S: Suodatin>(s: &S, kaikki: &'a [Tapahtuma])
    -> Vec<&'a Tapahtuma>
{
    kaikki.iter().filter(|t| s.hyvaksyy(t)).collect()
}
// @loppu omat

// @alku virheet
enum JasennysVirhe {
    Muoto(String),
    Taso(String),
}

fn jasenna(rivi: &str) -> Result<Tapahtuma, JasennysVirhe> {
    let (taso, viesti) = rivi
        .split_once(": ")
        .ok_or_else(|| JasennysVirhe::Muoto(rivi.to_string()))?;
    let taso = match taso {
        "INFO" => Taso::Info,
        "WARN" => Taso::Varoitus,
        "ERROR" => Taso::Virhe,
        muu => return Err(JasennysVirhe::Taso(muu.to_string())),
    };
    Ok(Tapahtuma::new(taso, viesti))
}
// @loppu virheet

fn main() {
    // @alku perus
    let n = 5_u32; // muuttumaton, tyyppi literaalista
    let mut summa: u64 = 0; // muuttuva, tyyppi annettu
    for i in 1..=n {
        summa += u64::from(i); // muunnokset aina näkyviin
    }
    let pari = (summa, "kpl"); // monikko
    let taulu = [0u8; 4]; // [T; N]
    let teksti = if summa > 10 { "iso" } else { "pieni" };
    println!("{NIMI}: {} {} {teksti} {taulu:?} {RAJA}", pari.0, pari.1);
    // @loppu perus

    // @alku ohjaus
    let rivit = ["INFO: käynnistys", "WARN: levy 91 %", "rikki",
                 "ERROR: yhteys katkesi", "DEBUG: x"];
    let mut tapahtumat = Vec::new();
    for rivi in rivit {
        match jasenna(rivi) {
            Ok(t) => tapahtumat.push(t),
            Err(JasennysVirhe::Taso(t)) => println!("ohitettu taso {t}"),
            Err(JasennysVirhe::Muoto(r)) => println!("huono rivi {r:?}"),
        }
    }
    let Some(eka) = tapahtumat.first() else { return };
    println!("ensimmäinen: {eka}");
    // @loppu ohjaus

    // @alku kokoelmat
    let mut maarat: HashMap<Taso, usize> = HashMap::new();
    for t in &tapahtumat {
        *maarat.entry(t.taso).or_default() += 1;
    }
    let mut avaimet: Vec<_> = maarat.keys().copied().collect();
    avaimet.sort();
    let pituudet: usize = tapahtumat.iter().map(|t| t.viesti.len()).sum();
    let vakavat = suodata(&VahintaanTaso(Taso::Varoitus), &tapahtumat);
    println!("{avaimet:?} {pituudet} {}", vakavat.len());
    // @loppu kokoelmat

    // @alku osoittimet
    let jaettu = Rc::new(RefCell::new(Vec::<String>::new()));
    let toinen = Rc::clone(&jaettu); // laskuri 2, ei kopiota
    toinen.borrow_mut().push("loki".into());
    println!("{} {}", jaettu.borrow().len(), Rc::strong_count(&jaettu));

    let laskuri = Arc::new(Mutex::new(0u32));
    let kahvat: Vec<_> = (0..4)
        .map(|_| {
            let l = Arc::clone(&laskuri);
            thread::spawn(move || *l.lock().expect("lukko") += 1)
        })
        .collect();
    for k in kahvat {
        k.join().expect("säie");
    }
    println!("säikeitä {}", laskuri.lock().expect("lukko"));
    // @loppu osoittimet

    // @alku raaka
    let mut arvo = 7_i32;
    let osoitin: *mut i32 = &mut arvo; // luonti on turvallista
    // SAFETY: osoitin on luotu elävästä muuttujasta, eikä muita
    // viitteitä siihen ole käytössä.
    unsafe { *osoitin += 1 };
    println!("{arvo}");
    // @loppu raaka
}
