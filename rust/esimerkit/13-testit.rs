// @alku toteutus
/// Normalisoi Unix-polun: poistaa tyhjät osat ja `.`-osat ja purkaa
/// `..`-osat. Absoluuttisen polun `..` juuressa jää pois.
#[must_use]
pub fn normalisoi(polku: &str) -> String {
    let absoluuttinen = polku.starts_with('/');
    let mut osat: Vec<&str> = Vec::new();
    for osa in polku.split('/') {
        match osa {
            "" | "." => {}
            ".." => match osat.last() {
                Some(&edellinen) if edellinen != ".." => {
                    osat.pop();
                }
                _ if absoluuttinen => {}
                _ => osat.push(".."),
            },
            muu => osat.push(muu),
        }
    }
    let runko = osat.join("/");
    match (absoluuttinen, runko.is_empty()) {
        (true, _) => format!("/{runko}"),
        (false, true) => ".".to_string(),
        (false, false) => runko,
    }
}
// @loppu toteutus

// @alku testit
// cargo test kääntää tämän modulin ja ajaa #[test]-funktiot. Tässä
// yksitiedostoisessa esimerkissä main ajaa samat funktiot itse.
#[cfg_attr(not(test), allow(dead_code))]
mod testit {
    use super::normalisoi;

    #[cfg_attr(test, test)]
    pub fn taulukko() {
        let tapaukset = [
            ("/a/./b/../c", "/a/c"),
            ("a//b/", "a/b"),
            ("../x/..", ".."),
            ("/../..", "/"),
            ("", "."),
            ("./", "."),
        ];
        for (syote, odotettu) in tapaukset {
            assert_eq!(normalisoi(syote), odotettu, "syöte {syote:?}");
        }
    }

    /// Ominaisuustesti: normalisointi on idempotentti kaikille
    /// generoiduille poluille. (proptest-kirjasto tekee tämän
    /// kattavammin ja pienentää löydetyn vastaesimerkin.)
    #[cfg_attr(test, test)]
    pub fn idempotentti() {
        let osat = ["a", "b", ".", "..", ""];
        let mut tila: u32 = 12345;
        for _ in 0..1000 {
            let mut polku = String::new();
            for _ in 0..6 {
                tila = tila.wrapping_mul(1_103_515_245).wrapping_add(12_345);
                polku.push_str(osat[(tila >> 16) as usize % osat.len()]);
                polku.push('/');
            }
            let kerran = normalisoi(&polku);
            assert_eq!(normalisoi(&kerran), kerran, "polku {polku:?}");
        }
    }

    pub const KAIKKI: [(&str, fn()); 2] =
        [("taulukko", taulukko), ("idempotentti", idempotentti)];
}
// @loppu testit

fn main() {
    // @alku kaytto
    for (nimi, testi) in testit::KAIKKI {
        testi();
        println!("test testit::{nimi} ... ok");
    }
    println!("{}", normalisoi("/usr/local/../lib/./rustlib"));
    // @loppu kaytto
}
