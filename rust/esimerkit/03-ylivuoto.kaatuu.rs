/// Laskee tavujen summan. Kehitysversiossa ylivuoto aiheuttaa paniikin;
/// julkaisuversiossa (--release) arvo kiertää, ellei toisin määrätä.
fn summa(tavut: &[u8]) -> u8 {
    let mut s: u8 = 0;
    for &t in tavut {
        s += t;
    }
    s
}

fn main() {
    let tavut: Vec<u8> = std::env::args().map(|_| 200).chain([100]).collect();
    println!("{}", summa(&tavut));
}
