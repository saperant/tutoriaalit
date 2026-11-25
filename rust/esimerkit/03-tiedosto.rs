use std::env;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, BufWriter, Write};
use std::path::{Path, PathBuf};
use std::process::ExitCode;

// @alku argumentit
/// Ainoa argumentti on tiedoston nimi. Indeksi 0 on ohjelman nimi.
fn polku_argumenteista() -> Result<PathBuf, String> {
    let mut argumentit = env::args_os().skip(1);
    match (argumentit.next(), argumentit.next()) {
        (Some(polku), None) => Ok(PathBuf::from(polku)),
        _ => Err("käyttö: tiedosto TIEDOSTO".to_string()),
    }
}
// @loppu argumentit

// @alku kirjoita
fn kirjoita(polku: &Path, arvot: &[f64]) -> io::Result<()> {
    let mut ulos = BufWriter::new(File::create(polku)?);
    for (i, arvo) in arvot.iter().enumerate() {
        writeln!(ulos, "anturi{} {arvo:.1}", i + 1)?;
    }
    ulos.flush() // tyhjennys näkyvästi: Drop nielisi virheen
}
// @loppu kirjoita

// @alku lue
/// Palauttaa rivin, jolla on suurin lukema. Tiedosto luetaan rivi
/// kerrallaan, joten sen ei tarvitse mahtua muistiin.
fn suurin(polku: &Path) -> io::Result<Option<(String, f64)>> {
    let mut paras: Option<(String, f64)> = None;
    for rivi in BufReader::new(File::open(polku)?).lines() {
        let rivi = rivi?;
        let Some((nimi, arvo)) = rivi.split_once(' ') else { continue };
        let Ok(arvo) = arvo.parse::<f64>() else { continue };
        let parempi = match &paras {
            Some((_, entinen)) => arvo > *entinen,
            None => true,
        };
        if parempi {
            paras = Some((nimi.to_string(), arvo));
        }
    }
    Ok(paras)
}
// @loppu lue

// @alku aja
fn aja(polku: &Path) -> io::Result<()> {
    kirjoita(polku, &[21.5, 23.0, 19.25])?;
    let sisalto = fs::read_to_string(polku)?; // pieni tiedosto kerralla
    println!("{} riviä, {} tavua", sisalto.lines().count(), sisalto.len());
    if let Some((nimi, arvo)) = suurin(polku)? {
        println!("suurin: {nimi} {arvo:.1}");
    }
    fs::remove_file(polku)?;

    // Sama polku uudelleen: tiedostoa ei enää ole.
    match File::open(polku) {
        Ok(_) => println!("tiedosto on yhä olemassa"),
        Err(virhe) => println!("{}: {virhe}", polku.display()),
    }
    Ok(())
}
// @loppu aja

fn main() -> ExitCode {
    let polku = match polku_argumenteista() {
        Ok(polku) => polku,
        Err(viesti) => {
            eprintln!("{viesti}");
            return ExitCode::from(2);
        }
    };
    match aja(&polku) {
        Ok(()) => ExitCode::SUCCESS,
        Err(virhe) => {
            eprintln!("{}: {virhe}", polku.display());
            ExitCode::FAILURE
        }
    }
}
