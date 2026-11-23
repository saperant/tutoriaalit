// @alku viipalejasennin
/// Nollakopioinen jäsennin: Kentta lainaa syöterivin osia, joten
/// rakenne ei saa elää syötettä pidempään. Elinaikaparametri 'a
/// kirjaa tämän riippuvuuden tyyppiin.
#[derive(Debug)]
struct Pyynto<'a> {
    metodi: &'a str,
    polku: &'a str,
    otsakkeet: Vec<(&'a str, &'a str)>,
}

fn jasenna(teksti: &str) -> Option<Pyynto<'_>> {
    let mut rivit = teksti.lines();
    let mut alku = rivit.next()?.split_whitespace();
    let metodi = alku.next()?;
    let polku = alku.next()?;
    let otsakkeet = rivit
        .take_while(|r| !r.is_empty())
        .filter_map(|r| r.split_once(':'))
        .map(|(k, v)| (k.trim(), v.trim()))
        .collect();
    Some(Pyynto { metodi, polku, otsakkeet })
}

impl<'a> Pyynto<'a> {
    /// Palautettu viite elää syötteen ('a) eikä &self:n ajan.
    fn otsake(&self, nimi: &str) -> Option<&'a str> {
        self.otsakkeet
            .iter()
            .find(|(k, _)| k.eq_ignore_ascii_case(nimi))
            .map(|&(_, v)| v)
    }
}
// @loppu viipalejasennin

// @alku pidempi
/// Kun funktio saa kaksi viitettä ja palauttaa toisen, kääntäjä ei voi
/// päätellä elinaikaa: se kirjoitetaan näkyviin.
fn pidempi<'a>(a: &'a str, b: &'a str) -> &'a str {
    if b.len() > a.len() { b } else { a }
}
// @loppu pidempi

fn main() {
    // @alku kaytto
    let syote = String::from(
        "GET /api/tuotteet HTTP/1.1\nHost: example.org\n\
         Accept: application/json\n\nrunko",
    );
    let isanta;
    {
        let pyynto = jasenna(&syote).expect("kelvollinen pyyntö");
        println!("{} {}", pyynto.metodi, pyynto.polku);
        for (avain, arvo) in &pyynto.otsakkeet {
            println!("  {avain} = {arvo}");
        }
        isanta = pyynto.otsake("host");
    } // pyynto vapautuu, isanta viittaa yhä syötteeseen
    println!("{isanta:?}");
    println!("{}", pidempi("lyhyt", "pidempi"));
    // @loppu kaytto
}
