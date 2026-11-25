// @alku crate
//! Kestojen jäsennys ja muotoilu.
//!
//! Crate muuntaa merkkijonon, kuten `"1h30m"`, sekunneiksi ja takaisin:
//!
//! ```
//! let sekunnit = kesto::jasenna("1h30m")?;
//! assert_eq!(sekunnit, 5400);
//! assert_eq!(kesto::muotoile(sekunnit), "1h30m");
//! # Ok::<(), kesto::Virhe>(())
//! ```
// @loppu crate

use std::fmt;

// @alku virhe
/// Virhe, jonka [`jasenna`] palauttaa.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum Virhe {
    /// Syöte on tyhjä.
    Tyhja,
    /// Luvun perässä ei ole yksikköä.
    PuuttuvaYksikko,
    /// Yksikkö ei ole `h`, `m` eikä `s`, tai sen edellä ei ole lukua.
    TuntematonYksikko(char),
    /// Tulos ei mahdu `u64`-tyyppiin.
    Ylivuoto,
}
// @loppu virhe

impl fmt::Display for Virhe {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            Virhe::Tyhja => write!(f, "kesto on tyhjä"),
            Virhe::PuuttuvaYksikko => write!(f, "yksikkö puuttuu"),
            Virhe::TuntematonYksikko(merkki) => {
                write!(f, "tuntematon yksikkö '{merkki}'")
            }
            Virhe::Ylivuoto => write!(f, "kesto on liian suuri"),
        }
    }
}

impl std::error::Error for Virhe {}

// @alku jasenna
/// Jäsentää keston sekunneiksi.
///
/// Kesto on jono osia, joista jokaisessa on kokonaisluku ja yksikkö
/// `h`, `m` tai `s`. Tulos on sama, jonka [`muotoile`] muuttaa takaisin
/// tekstiksi.
///
/// # Examples
///
/// ```
/// use kesto::{jasenna, Virhe};
///
/// assert_eq!(jasenna("90s"), Ok(90));
/// assert_eq!(jasenna("2h5m"), Ok(7500));
/// assert_eq!(jasenna("15"), Err(Virhe::PuuttuvaYksikko));
/// ```
///
/// # Errors
///
/// Palauttaa virheen, jos syöte on tyhjä, luvulta puuttuu yksikkö,
/// yksikkö on tuntematon tai tulos ei mahdu `u64`-tyyppiin.
pub fn jasenna(teksti: &str) -> Result<u64, Virhe> {
    if teksti.is_empty() {
        return Err(Virhe::Tyhja);
    }
    let mut yhteensa: u64 = 0;
    let mut luku: Option<u64> = None;
    for merkki in teksti.chars() {
        if let Some(numero) = merkki.to_digit(10) {
            let uusi = luku
                .unwrap_or(0)
                .checked_mul(10)
                .and_then(|l| l.checked_add(u64::from(numero)))
                .ok_or(Virhe::Ylivuoto)?;
            luku = Some(uusi);
            continue;
        }
        let kerroin = match merkki {
            'h' => 3600,
            'm' => 60,
            's' => 1,
            muu => return Err(Virhe::TuntematonYksikko(muu)),
        };
        let maara = luku.take().ok_or(Virhe::TuntematonYksikko(merkki))?;
        yhteensa = maara
            .checked_mul(kerroin)
            .and_then(|s| yhteensa.checked_add(s))
            .ok_or(Virhe::Ylivuoto)?;
    }
    match luku {
        Some(_) => Err(Virhe::PuuttuvaYksikko),
        None => Ok(yhteensa),
    }
}
// @loppu jasenna

/// Muotoilee sekunnit lyhimpään muotoon, jonka [`jasenna`] hyväksyy.
///
/// ```
/// assert_eq!(kesto::muotoile(3661), "1h1m1s");
/// assert_eq!(kesto::muotoile(0), "0s");
/// ```
#[must_use]
pub fn muotoile(sekunnit: u64) -> String {
    let osat = [
        (sekunnit / 3600, 'h'),
        (sekunnit / 60 % 60, 'm'),
        (sekunnit % 60, 's'),
    ];
    let mut teksti = String::new();
    for (maara, yksikko) in osat {
        if maara > 0 {
            teksti.push_str(&maara.to_string());
            teksti.push(yksikko);
        }
    }
    if teksti.is_empty() {
        teksti.push_str("0s");
    }
    teksti
}

// @alku jaa
/// Jakaa keston tasan `osia` osaan ja pyöristää alaspäin.
///
/// # Panics
///
/// Aiheuttaa paniikin, jos `osia` on nolla.
///
/// ```should_panic
/// kesto::jaa(60, 0);
/// ```
#[must_use]
pub fn jaa(sekunnit: u64, osia: u64) -> u64 {
    assert!(osia > 0, "osia on oltava vähintään yksi");
    sekunnit / osia
}
// @loppu jaa

// @alku yksikkotestit
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn yksikon_edella_on_oltava_luku() {
        assert_eq!(jasenna("m"), Err(Virhe::TuntematonYksikko('m')));
        assert_eq!(jasenna("5x"), Err(Virhe::TuntematonYksikko('x')));
    }

    #[test]
    fn ylivuoto_havaitaan() {
        assert_eq!(jasenna("99999999999999999999s"), Err(Virhe::Ylivuoto));
        assert_eq!(jasenna("9999999999999999h"), Err(Virhe::Ylivuoto));
    }
}
// @loppu yksikkotestit
