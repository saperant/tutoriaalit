use std::collections::HashMap;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::{Arc, Mutex, RwLock};
use std::thread;

// @alku tilastot
/// Jaettu tila: Arc jakaa omistajuuden säikeiden kesken, Mutex ja
/// RwLock antavat muuttaa sitä. Lukko omistaa datan, joten dataan ei
/// pääse käsiksi ottamatta lukkoa (toisin kuin C:n pthread_mutex_t).
struct Tilastot {
    pyyntoja: AtomicUsize,
    polut: Mutex<HashMap<String, u32>>,
    asetukset: RwLock<u32>, // raja: paljon lukijoita, harvoin kirjoittaja
}
// @loppu tilastot

fn main() {
    // @alku kaytto
    let tilastot = Arc::new(Tilastot {
        pyyntoja: AtomicUsize::new(0),
        polut: Mutex::new(HashMap::new()),
        asetukset: RwLock::new(150),
    });
    let polut = ["/", "/api", "/", "/kirjaudu"];

    let kahvat: Vec<_> = (0..4)
        .map(|i| {
            let t = Arc::clone(&tilastot);
            thread::spawn(move || {
                for polku in polut.iter().cycle().skip(i).take(100) {
                    // Laskuri ei tarvitse lukkoa; järjestys ei merkitse.
                    t.pyyntoja.fetch_add(1, Ordering::Relaxed);
                    let raja = *t.asetukset.read().expect("lukko");
                    let mut p = t.polut.lock().expect("lukko");
                    let n = p.entry(polku.to_string()).or_insert(0);
                    *n = (*n + 1).min(raja);
                } // MutexGuard vapauttaa lukon tässä (RAII)
            })
        })
        .collect();
    for k in kahvat {
        k.join().expect("säie");
    }
    // Kirjoittaja odottaa, kunnes lukijoita ei ole.
    *tilastot.asetukset.write().expect("lukko") = 1000;

    println!("pyyntöjä {}, raja nyt {}",
             tilastot.pyyntoja.load(Ordering::Relaxed),
             tilastot.asetukset.read().expect("lukko"));
    let polut = tilastot.polut.lock().expect("lukko");
    let mut lajiteltu: Vec<_> = polut.iter().collect();
    lajiteltu.sort();
    println!("{lajiteltu:?}");
    // @loppu kaytto
}
