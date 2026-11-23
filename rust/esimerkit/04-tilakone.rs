// @alku tilat
#[derive(Debug)]
enum Tila {
    Suljettu,
    Yhdistaa { yritykset: u32 },
    Auki { istunto: u64 },
}

#[derive(Debug, Clone, Copy)]
enum Tapahtuma {
    Avaa,
    Onnistui(u64),
    Epaonnistui,
    Sulje,
}

const MAKSIMIYRITYKSET: u32 = 3;

fn siirtyma(tila: Tila, tapahtuma: Tapahtuma) -> Tila {
    use Tapahtuma as T;
    match (tila, tapahtuma) {
        (Tila::Suljettu, T::Avaa) => Tila::Yhdistaa { yritykset: 1 },
        (Tila::Yhdistaa { .. }, T::Onnistui(istunto)) => {
            Tila::Auki { istunto }
        }
        (Tila::Yhdistaa { yritykset }, T::Epaonnistui)
            if yritykset < MAKSIMIYRITYKSET =>
        {
            Tila::Yhdistaa { yritykset: yritykset + 1 }
        }
        (Tila::Yhdistaa { .. }, T::Epaonnistui) => Tila::Suljettu,
        (_, T::Sulje) => Tila::Suljettu,
        // Muut yhdistelmät eivät muuta tilaa.
        (tila, _) => tila,
    }
}
// @loppu tilat

fn main() {
    // @alku ajo
    let tapahtumat = [
        Tapahtuma::Avaa, Tapahtuma::Epaonnistui, Tapahtuma::Onnistui(42),
        Tapahtuma::Avaa, Tapahtuma::Sulje, Tapahtuma::Avaa,
        Tapahtuma::Epaonnistui, Tapahtuma::Epaonnistui,
        Tapahtuma::Epaonnistui,
    ];
    let mut tila = Tila::Suljettu;
    for t in tapahtumat {
        tila = siirtyma(tila, t);
        println!("{:<14} -> {tila:?}", format!("{t:?}"));
    }
    match tila {
        Tila::Auki { istunto } => println!("auki, istunto {istunto}"),
        Tila::Suljettu => println!("yhteys suljettu"),
        Tila::Yhdistaa { yritykset } => println!("yritys {yritykset}"),
    }
    // @loppu ajo
}
