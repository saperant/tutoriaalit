// @alku juuri
//! Varastokirjanpito. Paketin (crate) juuri esittelee modulit;
//! kukin `mod` etsii tiedoston <nimi>.rs tämän tiedoston vierestä.

mod raportti;
mod varasto;

use std::io::{self, BufRead};

use raportti::Raportti;
use varasto::{Tuotekoodi, Varasto};
// @loppu juuri

fn main() {
    // @alku kaytto
    let mut varasto = Varasto::new();
    for (n, rivi) in io::stdin().lock().lines().enumerate() {
        let rivi = rivi.expect("syötteen luku");
        let tulos = rivi
            .split_once(' ')
            .ok_or_else(|| "odotettiin: KOODI MÄÄRÄ".to_string())
            .and_then(|(koodi, maara)| {
                let koodi = Tuotekoodi::new(koodi)?;
                let maara: i32 = maara.trim().parse()
                    .map_err(|_| format!("huono määrä {maara:?}"))?;
                varasto.muuta(koodi, maara).map_err(|e| e.to_string())
            });
        if let Err(virhe) = tulos {
            println!("rivi {}: {virhe}", n + 1);
        }
    }
    print!("{}", Raportti::new(&varasto).vahissa(5));
    // @loppu kaytto
}
