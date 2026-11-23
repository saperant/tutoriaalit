fn main() {
    let mittaukset = [12.5, 13.0, 12.8];
    // Indeksi tulee ajon aikana, kuten C:ssä.
    let indeksi = std::env::args().count() + 2;
    println!("{}", mittaukset[indeksi]);
}
