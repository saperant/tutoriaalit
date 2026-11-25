use std::collections::BTreeMap;

// @alku makro
/// Hakemistoliteraali: hakemisto! { avain => arvo, ... }.
/// $( ... ),+ toistaa hahmon pilkuilla erotettuna, ja $(,)? sallii
/// pilkun viimeisen parin perässä.
macro_rules! hakemisto {
    ($($avain:expr => $arvo:expr),+ $(,)?) => {{
        let mut hakemisto = BTreeMap::new();
        $( hakemisto.insert($avain, $arvo); )+
        hakemisto
    }};
}
// @loppu makro

// @alku derive
/// derive tuottaa neljä impl-lohkoa, jotka käyvät kentät läpi.
#[derive(Debug, Clone, PartialEq, Default)]
struct Raja {
    ala: i32,
    yla: i32,
}
// @loppu derive

fn main() {
    // @alku kaytto
    let portit = hakemisto! {
        "https" => 443,
        "ssh" => 22,
        "http" => 80,
    };
    println!("{portit:?}");

    let raja = Raja { ala: 0, yla: 10 };
    let kopio = raja.clone();
    println!("{raja:?} {} {:?}", raja == kopio, Raja::default());
    // @loppu kaytto
}
