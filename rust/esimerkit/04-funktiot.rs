// @alku funktiot
/// Paluuarvo on viimeinen lauseke; return palaa aiemmin.
fn alennusprosentti(ostot_snt: u64, kanta_asiakas: bool) -> u32 {
    if ostot_snt == 0 {
        return 0;
    }
    let perus = if ostot_snt >= 10_000 { 10 } else { 0 };
    if kanta_asiakas { perus + 5 } else { perus }
}

/// Useita arvoja palautetaan monikkona.
fn jaa(jaettava: u32, jakaja: u32) -> (u32, u32) {
    (jaettava / jakaja, jaettava % jakaja)
}
// @loppu funktiot

// @alku osoitin
/// Funktio on arvo: tyyppi fn(f64) -> f64 on funktio-osoitin.
fn taulukoi(nimi: &str, f: fn(f64) -> f64) {
    let arvot: Vec<String> =
        [0.0, 0.5, 1.0].iter().map(|&x| format!("{:.2}", f(x))).collect();
    println!("{nimi:<8} {}", arvot.join(" "));
}

fn nelio(x: f64) -> f64 {
    x * x
}
// @loppu osoitin

fn main() {
    // @alku kaytto
    println!("{} {} {}", alennusprosentti(0, true),
             alennusprosentti(2_500, true), alennusprosentti(12_000, true));
    let (osamaara, jakojaannos) = jaa(17, 5);
    println!("17 = 5 * {osamaara} + {jakojaannos}");

    taulukoi("neliö", nelio);
    taulukoi("juuri", f64::sqrt);
    taulukoi("kaksi x", |x| 2.0 * x); // sulkeuma, joka ei sieppaa mitään
    // @loppu kaytto
}
