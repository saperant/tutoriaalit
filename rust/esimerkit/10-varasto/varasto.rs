// @alku tuotekoodi
use std::collections::BTreeMap;
use std::fmt;

/// Validoitu tuotekoodi: kaksi kirjainta ja neljä numeroa. Kenttä on
/// yksityinen, joten koodin voi luoda vain new-funktiolla, eikä
/// virheellistä arvoa voi olla olemassa ("parse, don't validate").
#[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord)]
pub struct Tuotekoodi(String);

impl Tuotekoodi {
    pub fn new(teksti: &str) -> Result<Self, String> {
        let t = teksti.as_bytes();
        let kelpaa = t.len() == 6
            && t[..2].iter().all(u8::is_ascii_uppercase)
            && t[2..].iter().all(u8::is_ascii_digit);
        if kelpaa {
            Ok(Tuotekoodi(teksti.to_string()))
        } else {
            Err(format!("virheellinen tuotekoodi {teksti:?}"))
        }
    }
}

impl fmt::Display for Tuotekoodi {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.write_str(&self.0)
    }
}
// @loppu tuotekoodi

// @alku varasto
#[derive(Debug, PartialEq)]
pub enum VarastoVirhe {
    EiRiita { koodi: Tuotekoodi, saldo: u32, pyydetty: u32 },
}

impl fmt::Display for VarastoVirhe {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            VarastoVirhe::EiRiita { koodi, saldo, pyydetty } => write!(
                f, "{koodi}: saldo {saldo}, pyydetty {pyydetty}"),
        }
    }
}

/// Saldot eivät voi mennä negatiivisiksi, koska ainoa muuttava
/// operaatio tarkistaa sen. Siksi kenttä on yksityinen.
#[derive(Default)]
pub struct Varasto {
    saldot: BTreeMap<Tuotekoodi, u32>,
}

impl Varasto {
    pub fn new() -> Self {
        Self::default()
    }

    pub fn muuta(&mut self, koodi: Tuotekoodi, maara: i32)
        -> Result<u32, VarastoVirhe>
    {
        let saldo = self.saldot.get(&koodi).copied().unwrap_or(0);
        let uusi = saldo.checked_add_signed(maara).ok_or(
            VarastoVirhe::EiRiita {
                koodi: koodi.clone(),
                saldo,
                pyydetty: maara.unsigned_abs(),
            })?;
        self.saldot.insert(koodi, uusi);
        Ok(uusi)
    }

    /// Näkyy vain tämän paketin sisällä, ei ulkoisille käyttäjille.
    pub(crate) fn saldot(&self)
        -> impl Iterator<Item = (&Tuotekoodi, u32)> + '_
    {
        self.saldot.iter().map(|(k, &s)| (k, s))
    }
}
// @loppu varasto
