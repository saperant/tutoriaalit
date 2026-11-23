use std::collections::HashMap;
use std::error::Error;
use std::fmt;
use std::io::{self, Read};
use std::num::ParseIntError;
use std::str::FromStr;

// @alku virhetyyppi
/// Kirjaston virhetyyppi: enum, jonka muunnelmat kuvaavat kutsujalle
/// merkitykselliset virhetilanteet. Tämä on sama malli, jonka
/// thiserror-kirjasto tuottaa makrolla.
#[derive(Debug)]
enum AsetusVirhe {
    Io(io::Error),
    Syntaksi { rivi: usize, sisalto: String },
    Luku { rivi: usize, avain: String, syy: ParseIntError },
    Puuttuu(&'static str),
}

impl fmt::Display for AsetusVirhe {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            AsetusVirhe::Io(_) => write!(f, "syötteen luku epäonnistui"),
            AsetusVirhe::Syntaksi { rivi, sisalto } => {
                write!(f, "rivi {rivi}: odotettiin avain = arvo: {sisalto:?}")
            }
            AsetusVirhe::Luku { rivi, avain, .. } => {
                write!(f, "rivi {rivi}: avaimen {avain} arvo ei ole luku")
            }
            AsetusVirhe::Puuttuu(avain) => write!(f, "avain {avain} puuttuu"),
        }
    }
}

impl Error for AsetusVirhe {
    /// Alkuperäinen syy säilyy ketjussa, mutta ei sotke viestiä.
    fn source(&self) -> Option<&(dyn Error + 'static)> {
        match self {
            AsetusVirhe::Io(e) => Some(e),
            AsetusVirhe::Luku { syy, .. } => Some(syy),
            _ => None,
        }
    }
}

/// From-muunnos antaa ?-operaattorin muuntaa io::Errorin automaattisesti.
impl From<io::Error> for AsetusVirhe {
    fn from(e: io::Error) -> Self {
        AsetusVirhe::Io(e)
    }
}
// @loppu virhetyyppi

// @alku jasennys
#[derive(Debug)]
struct Asetukset {
    portti: u16,
    tyontekijat: u32,
    nimi: String,
}

fn jasenna(teksti: &str) -> Result<Asetukset, AsetusVirhe> {
    let mut arvot = HashMap::new();
    for (i, rivi) in teksti.lines().enumerate() {
        let rivi = rivi.trim();
        if rivi.is_empty() || rivi.starts_with('#') {
            continue;
        }
        let Some((avain, arvo)) = rivi.split_once('=') else {
            return Err(AsetusVirhe::Syntaksi {
                rivi: i + 1,
                sisalto: rivi.to_string(),
            });
        };
        arvot.insert(avain.trim(), (i + 1, arvo.trim()));
    }

    Ok(Asetukset {
        portti: hae(&arvot, "portti")?
            .ok_or(AsetusVirhe::Puuttuu("portti"))?,
        tyontekijat: hae(&arvot, "tyontekijat")?.unwrap_or(4),
        nimi: arvot.get("nimi")
            .map_or("palvelu".to_string(), |(_, n)| n.to_string()),
    })
}

type Arvot<'a> = HashMap<&'a str, (usize, &'a str)>;

/// Hakee valinnaisen avaimen ja jäsentää sen mihin tahansa
/// kokonaislukutyyppiin. Ok(None): avain puuttuu, Err: arvo on huono.
fn hae<T>(arvot: &Arvot, avain: &str) -> Result<Option<T>, AsetusVirhe>
where
    T: FromStr<Err = ParseIntError>,
{
    let Some(&(rivi, arvo)) = arvot.get(avain) else {
        return Ok(None);
    };
    arvo.parse().map(Some).map_err(|syy| AsetusVirhe::Luku {
        rivi,
        avain: avain.to_string(),
        syy,
    })
}

fn lue_asetukset() -> Result<Asetukset, AsetusVirhe> {
    let mut teksti = String::new();
    io::stdin().read_to_string(&mut teksti)?; // io::Error -> AsetusVirhe
    jasenna(&teksti)
}
// @loppu jasennys

// @alku raportti
/// Tulostaa virheen ja koko syyketjun.
fn raportoi(virhe: &dyn Error) {
    println!("virhe: {virhe}");
    let mut syy = virhe.source();
    while let Some(s) = syy {
        println!("  syy: {s}");
        syy = s.source();
    }
}
// @loppu raportti

fn main() {
    // @alku kaytto
    match lue_asetukset() {
        Ok(a) => println!("{}: portti {}, {} säiettä",
                          a.nimi, a.portti, a.tyontekijat),
        Err(e) => raportoi(&e),
    }
    let tapaukset = [
        "portti = 8080\nnimi = kassa",
        "portti 8080",
        "portti = 80a",
        "nimi = kassa",
        "portti = 70000",
    ];
    for teksti in tapaukset {
        match jasenna(teksti) {
            Ok(a) => println!("{a:?}"),
            Err(e) => raportoi(&e),
        }
    }
    // @loppu kaytto
}
