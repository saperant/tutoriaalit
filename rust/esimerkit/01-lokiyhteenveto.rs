//! Lukee lokirivejä syötteestä ja tiivistää ne tasoittain.
use std::collections::BTreeMap;
use std::io::{self, BufRead};

fn main() -> io::Result<()> {
    let mut maarat: BTreeMap<String, usize> = BTreeMap::new();
    let mut virheelliset = 0;

    for rivi in io::stdin().lock().lines() {
        let rivi = rivi?;
        // Muoto: "TASO: viesti"
        match rivi.split_once(':') {
            Some((taso, _)) => {
                *maarat.entry(taso.to_string()).or_insert(0) += 1;
            }
            None => virheelliset += 1,
        }
    }

    for (taso, maara) in &maarat {
        println!("{taso:<6} {maara:>3}");
    }
    println!("virheellisiä rivejä: {virheelliset}");
    Ok(())
}
