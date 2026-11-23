// @alku clippy
/// Kääntyy rustc:llä, mutta Clippy hylkää (needless_range_loop):
/// indeksisilmukka tekee rajatarkistuksen joka kierroksella ja kätkee
/// aikomuksen.
fn summa_indekseilla(luvut: &[u64]) -> u64 { // @virhe
    let mut summa = 0; // @virhe
    for i in 0..luvut.len() { // @virhe
        summa += luvut[i]; // @virhe
    } // @virhe
    summa // @virhe
} // @virhe

/// Idiomaattinen muoto: iteraattori, ei indeksejä eikä tarkistuksia.
fn summa(luvut: &[u64]) -> u64 {
    luvut.iter().sum()
}

fn main() {
    let mittaukset = [3, 5, 8, 13];
    println!("{}", summa_indekseilla(&mittaukset)); // @virhe
    println!("{}", summa(&mittaukset));
}
// @loppu clippy
