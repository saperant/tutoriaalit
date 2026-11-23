use std::sync::mpsc;
use std::thread;

// @alku tyojono
/// Tuottaja–kuluttaja kanavilla: työt jaetaan yhdellä kanavalla,
/// tulokset kerätään toisella. Säikeet eivät jaa muuttuvaa tilaa;
/// omistajuus siirtyy viestin mukana ("share memory by communicating").
fn tarkista_kaikki(tiedostot: Vec<String>, tyolaisia: usize)
    -> Vec<(String, usize)>
{
    let (tyo_tx, tyo_rx) = mpsc::channel::<String>();
    let tyo_rx = std::sync::Arc::new(std::sync::Mutex::new(tyo_rx));
    let (tulos_tx, tulos_rx) = mpsc::channel();

    let kahvat: Vec<_> = (0..tyolaisia)
        .map(|_| {
            let rx = std::sync::Arc::clone(&tyo_rx);
            let tx = tulos_tx.clone();
            thread::spawn(move || loop {
                // Lukko vapautuu heti, kun recv palaa.
                let tyo = rx.lock().expect("lukko").recv();
                let Ok(nimi) = tyo else { break };
                let pisteet = nimi.bytes().filter(|&b| b == b'.').count();
                tx.send((nimi, pisteet)).expect("vastaanottaja elää");
            })
        })
        .collect();
    drop(tulos_tx); // muuten tulos_rx odottaisi ikuisesti

    for t in tiedostot {
        tyo_tx.send(t).expect("työläinen elää");
    }
    drop(tyo_tx); // kanavan sulku pysäyttää työläiset

    let mut tulokset: Vec<_> = tulos_rx.iter().collect();
    for k in kahvat {
        k.join().expect("työläinen");
    }
    tulokset.sort();
    tulokset
}
// @loppu tyojono

fn main() {
    // @alku kaytto
    let tiedostot = ["raportti.tar.gz", "Makefile", "kuva.2026.11.png"]
        .map(String::from)
        .to_vec();
    for (nimi, pisteita) in tarkista_kaikki(tiedostot, 3) {
        println!("{nimi}: {pisteita}");
    }
    // @loppu kaytto
}
