//! Laskee laskutoimituksia: jäsennin luokkaa "rekursiivinen laskeutuminen".

// @alku tokenit
#[derive(Debug, Clone, Copy, PartialEq)]
enum Tokeni {
    Luku(f64),
    Plus,
    Miinus,
    Kerto,
    Jako,
    Vasen,
    Oikea,
}

fn tokenisoi(teksti: &str) -> Result<Vec<Tokeni>, String> {
    let mut tokenit = Vec::new();
    let mut merkit = teksti.chars().peekable();
    while let Some(c) = merkit.next() {
        let tokeni = match c {
            ' ' => continue,
            '+' => Tokeni::Plus,
            '-' => Tokeni::Miinus,
            '*' => Tokeni::Kerto,
            '/' => Tokeni::Jako,
            '(' => Tokeni::Vasen,
            ')' => Tokeni::Oikea,
            '0'..='9' | '.' => {
                let mut luku = String::from(c);
                while let Some(d) =
                    merkit.next_if(|d| d.is_ascii_digit() || *d == '.')
                {
                    luku.push(d);
                }
                let arvo = luku.parse().map_err(|_| format!("luku {luku}"))?;
                Tokeni::Luku(arvo)
            }
            muu => return Err(format!("tuntematon merkki '{muu}'")),
        };
        tokenit.push(tokeni);
    }
    Ok(tokenit)
}
// @loppu tokenit

// @alku jasennin
struct Jasennin {
    tokenit: Vec<Tokeni>,
    kohta: usize,
}

impl Jasennin {
    fn katso(&self) -> Option<Tokeni> {
        self.tokenit.get(self.kohta).copied()
    }

    fn seuraava(&mut self) -> Option<Tokeni> {
        let t = self.katso();
        self.kohta += 1;
        t
    }

    // lauseke := termi (('+' | '-') termi)*
    fn lauseke(&mut self) -> Result<f64, String> {
        let mut arvo = self.termi()?;
        while let Some(op @ (Tokeni::Plus | Tokeni::Miinus)) = self.katso() {
            self.kohta += 1;
            let oikea = self.termi()?;
            arvo = if op == Tokeni::Plus {
                arvo + oikea
            } else {
                arvo - oikea
            };
        }
        Ok(arvo)
    }

    // termi := tekija (('*' | '/') tekija)*
    fn termi(&mut self) -> Result<f64, String> {
        let mut arvo = self.tekija()?;
        loop {
            match self.katso() {
                Some(Tokeni::Kerto) => {
                    self.kohta += 1;
                    arvo *= self.tekija()?;
                }
                Some(Tokeni::Jako) => {
                    self.kohta += 1;
                    let jakaja = self.tekija()?;
                    if jakaja == 0.0 {
                        return Err("jako nollalla".into());
                    }
                    arvo /= jakaja;
                }
                _ => return Ok(arvo),
            }
        }
    }

    // tekija := luku | '-' tekija | '(' lauseke ')'
    fn tekija(&mut self) -> Result<f64, String> {
        match self.seuraava() {
            Some(Tokeni::Luku(x)) => Ok(x),
            Some(Tokeni::Miinus) => Ok(-self.tekija()?),
            Some(Tokeni::Vasen) => {
                let arvo = self.lauseke()?;
                match self.seuraava() {
                    Some(Tokeni::Oikea) => Ok(arvo),
                    _ => Err("puuttuva ')'".into()),
                }
            }
            Some(t) => Err(format!("odottamaton {t:?}")),
            None => Err("lauseke loppui kesken".into()),
        }
    }
}
// @loppu jasennin

// @alku laske
fn laske(teksti: &str) -> Result<f64, String> {
    let mut j = Jasennin { tokenit: tokenisoi(teksti)?, kohta: 0 };
    let arvo = j.lauseke()?;
    if let Some(t) = j.katso() {
        return Err(format!("ylimääräinen {t:?}"));
    }
    Ok(arvo)
}

fn main() {
    for lauseke in ["1 + 2 * 3", "(1 + 2) * 3", "-4 / (2 - 2)",
                    "2 * (3 + 4", "7 % 2", "1.5 * 4 - 0.5"] {
        match laske(lauseke) {
            Ok(arvo) => println!("{lauseke:<14} = {arvo}"),
            Err(virhe) => println!("{lauseke:<14} : {virhe}"),
        }
    }
}
// @loppu laske
