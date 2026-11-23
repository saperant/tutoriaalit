use std::fmt;

// @alku display
struct Lampotila {
    celsius: f64,
}

impl fmt::Display for Lampotila {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        // Välitetään leveys- ja tarkkuusmääreet eteenpäin.
        let tarkkuus = f.precision().unwrap_or(1);
        write!(f, "{:.*} °C", tarkkuus, self.celsius)
    }
}
// @loppu display

#[derive(Debug)]
struct Anturi {
    tunnus: u32,
    sijainti: &'static str,
}

fn main() {
    // @alku muotoilu
    let nimi = "lämpötila";
    let arvo = 21.456;
    println!("[{nimi:<10}] [{arvo:>8.2}] [{arvo:08.3}]");
    println!("{:#x} {:#b} {:e}", 255, 5, 1234.5);
    let (alku, loppu) = ("ping", "pong");
    println!("{0}, {1}, {0}", alku, loppu);
    // @loppu muotoilu

    // @alku debug
    let anturi = Anturi { tunnus: 3, sijainti: "konehuone" };
    println!("{anturi:?}");
    println!("{anturi:#?}");
    println!("anturi {} sijaitsee: {}", anturi.tunnus, anturi.sijainti);
    // @loppu debug

    println!("{} / {:.3}", Lampotila { celsius: 21.456 },
             Lampotila { celsius: -4.0 });
    eprintln!("virheviestit kirjoitetaan stderr-virtaan");
}
