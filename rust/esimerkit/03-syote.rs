//! Lukee mittauksia muodossa "anturi arvo" ja raportoi virheelliset rivit.
use std::io::{self, BufRead};

// @alku jasenna
fn jasenna(rivi: &str) -> Result<(&str, f64), String> {
    let mut osat = rivi.split_whitespace();
    let (Some(anturi), Some(arvo), None) =
        (osat.next(), osat.next(), osat.next())
    else {
        return Err(format!("odotettiin kaksi kenttää: '{rivi}'"));
    };
    let arvo: f64 = arvo
        .parse()
        .map_err(|_| format!("'{arvo}' ei ole luku"))?;
    Ok((anturi, arvo))
}
// @loppu jasenna

fn main() -> io::Result<()> {
    // @alku lue
    let mut summa = 0.0;
    let mut maara = 0;
    for (nro, rivi) in io::stdin().lock().lines().enumerate() {
        let rivi = rivi?;
        if rivi.trim().is_empty() || rivi.starts_with('#') {
            continue;
        }
        match jasenna(&rivi) {
            Ok((anturi, arvo)) => {
                println!("{anturi}: {arvo:.1}");
                summa += arvo;
                maara += 1;
            }
            Err(virhe) => println!("rivi {}: {virhe}", nro + 1),
        }
    }
    if maara > 0 {
        println!("keskiarvo {:.2} ({maara} mittausta)", summa / maara as f64);
    }
    Ok(())
    // @loppu lue
}
