use std::collections::HashMap;

#[derive(Debug)]
struct Kayttaja {
    nimi: String,
    esimies: Option<u32>,
    sahkoposti: Option<String>,
}

// @alku yhdistimet
/// Option-yhdistimet korvaavat sisäkkäiset NULL-tarkistukset.
fn esimiehen_posti(
    kayttajat: &HashMap<u32, Kayttaja>,
    id: u32,
) -> Option<&str> {
    let kayttaja = kayttajat.get(&id)?;
    let esimies = kayttajat.get(&kayttaja.esimies?)?;
    esimies.sahkoposti.as_deref()
}

fn kuvaus(kayttajat: &HashMap<u32, Kayttaja>, id: u32) -> String {
    kayttajat
        .get(&id)
        .map(|k| k.nimi.to_uppercase())
        .filter(|nimi| !nimi.is_empty())
        .unwrap_or_else(|| format!("<tuntematon {id}>"))
}
// @loppu yhdistimet

// @alku muunnos
/// Option ja Result muuntuvat toisikseen: ok_or lisää virheen,
/// ok() hylkää sen.
fn ika(teksti: &str) -> Result<u8, String> {
    let luku: u8 = teksti.trim().parse().ok()
        .ok_or_else(|| format!("{teksti:?} ei ole ikä"))?;
    (luku <= 150).then_some(luku)
        .ok_or_else(|| format!("{luku} on epäuskottava ikä"))
}
// @loppu muunnos

fn main() {
    // @alku kaytto
    let mut kayttajat = HashMap::new();
    kayttajat.insert(1, Kayttaja {
        nimi: "Grace".into(),
        esimies: None,
        sahkoposti: Some("grace@example.org".into()),
    });
    kayttajat.insert(2, Kayttaja {
        nimi: "Linus".into(),
        esimies: Some(1),
        sahkoposti: None,
    });
    for id in [1, 2, 3] {
        println!("{}: {:?}", kuvaus(&kayttajat, id),
                 esimiehen_posti(&kayttajat, id));
    }
    for syote in ["42", "x", "200"] {
        println!("{:?}", ika(syote));
    }
    // Kaikki tai ei mitään: Result-iteraattorin collect.
    let iat: Result<Vec<u8>, String> =
        ["30", "41", "x"].iter().map(|s| ika(s)).collect();
    println!("{iat:?}");
    println!("{:?}", kayttajat[&2]);
    // @loppu kaytto
}
