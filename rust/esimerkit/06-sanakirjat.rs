use std::collections::{BTreeMap, HashMap, HashSet};

fn main() {
    let teksti = "kissa koira kissa hiiri koira kissa lintu";

    // @alku entry
    let mut maarat: HashMap<&str, usize> = HashMap::new();
    for sana in teksti.split_whitespace() {
        *maarat.entry(sana).or_insert(0) += 1;
    }
    // HashMapin järjestys on satunnainen: lajitellaan tulostusta varten.
    let mut jarjestetty: Vec<(&str, usize)> = maarat.into_iter().collect();
    jarjestetty.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(b.0)));
    println!("{jarjestetty:?}");
    // @loppu entry

    // @alku btree
    // BTreeMap pitää avaimet järjestyksessä ja tukee välihakuja.
    let mut hinnat = BTreeMap::new();
    hinnat.insert("2026-01", 92.5);
    hinnat.insert("2026-03", 95.1);
    hinnat.insert("2026-02", 93.0);
    for (kk, hinta) in hinnat.range("2026-02"..) {
        println!("{kk}: {hinta}");
    }
    // @loppu btree

    // @alku joukko
    let sallitut: HashSet<&str> = ["luku", "kirjoitus"].into_iter().collect();
    let pyydetyt = ["luku", "poisto"];
    let kielletyt: Vec<&&str> =
        pyydetyt.iter().filter(|o| !sallitut.contains(*o)).collect();
    println!("kielletyt: {kielletyt:?}");
    // @loppu joukko
}
