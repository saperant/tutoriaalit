// @alku tilastot
/// Toimii taulukoille, vektoreille ja niiden osille: &[f64] on
/// osoitin ja pituus, samaan tapaan kuin C:n (const double *, size_t).
fn keskiarvo(arvot: &[f64]) -> Option<f64> {
    if arvot.is_empty() {
        None
    } else {
        Some(arvot.iter().sum::<f64>() / arvot.len() as f64)
    }
}

/// Normalisoi arvot paikallaan välille 0..1.
fn normalisoi(arvot: &mut [f64]) {
    let pienin = arvot.iter().copied().fold(f64::INFINITY, f64::min);
    let suurin = arvot.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let vali = suurin - pienin;
    if vali > 0.0 {
        for x in arvot.iter_mut() {
            *x = (*x - pienin) / vali;
        }
    }
}
// @loppu tilastot

fn main() {
    // @alku kaytto
    let mut mittaukset = vec![12.0, 18.0, 15.0, 30.0, 24.0];
    let taulukko = [1.0, 2.0];
    println!("{:?} {:?}", keskiarvo(&mittaukset), keskiarvo(&taulukko));
    println!("kolme ensimmäistä: {:?}", keskiarvo(&mittaukset[..3]));
    println!("tyhjä: {:?}", keskiarvo(&[]));

    // Kaksi erillistä muokkaavaa lainausta saman vektorin eri osiin.
    let (alku, loppu) = mittaukset.split_at_mut(2);
    normalisoi(alku);
    normalisoi(loppu);
    println!("{mittaukset:?}");
    // @loppu kaytto
}
