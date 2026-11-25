// @alku parametri
/// Fn: sulkeuma vain lukee sieppaamaansa. Geneerinen parametri
/// (impl Fn) kääntyy suoraksi kutsuksi, jonka kääntäjä voi upottaa.
fn laske_ehdolla(arvot: &[u64], ehto: impl Fn(u64) -> bool) -> usize {
    arvot.iter().filter(|&&arvo| ehto(arvo)).count()
}

/// FnMut: sulkeuma saa muuttaa tilaansa kutsujen välillä.
fn jokaiselle(arvot: &[u64], mut tee: impl FnMut(u64)) {
    for &arvo in arvot {
        tee(arvo);
    }
}

/// Sulkeuman tyyppiä ei voi kirjoittaa, joten paluutyyppi on impl Fn.
/// move siirtää rajan sulkeumaan, joka elää funktiota pidempään.
fn vahintaan(raja: u64) -> impl Fn(u64) -> bool {
    move |arvo| arvo >= raja
}
// @loppu parametri

fn main() {
    // @alku kaytto
    let summat = [12_950, 4_500, 30_000, 2_000];

    let raja = 5_000;
    println!("yli rajan: {}", laske_ehdolla(&summat, |s| s >= raja));

    let mut yhteensa = 0;
    jokaiselle(&summat, |s| yhteensa += s); // lainaa muokattavaksi
    println!("yhteensä: {yhteensa}");

    let iso = vahintaan(10_000);
    println!("isoja: {}", laske_ehdolla(&summat, iso));

    // FnOnce: sulkeuma luovuttaa sieppaamansa arvon, joten sen voi
    // kutsua vain kerran.
    let nimet = vec![String::from("Ada"), String::from("Grace")];
    let luovuta = move || nimet;
    let takaisin = luovuta();
    println!("{takaisin:?}");
    // @loppu kaytto
}
