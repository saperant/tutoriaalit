use std::time::Duration;

// @alku rakentaja
#[derive(Debug)]
struct Pyynto {
    osoite: String,
    metodi: &'static str,
    aikakatkaisu: Duration,
    yritykset: u32,
}

/// Rakentaja (builder): pakolliset kentät muodostimessa, valinnaiset
/// ketjutettavilla metodeilla. Korvaa C++:n kuormitetut muodostimet ja
/// pitkät parametrilistat.
struct PyyntoRakentaja {
    pyynto: Pyynto,
}

impl PyyntoRakentaja {
    fn new(osoite: &str) -> Self {
        PyyntoRakentaja {
            pyynto: Pyynto {
                osoite: osoite.to_string(),
                metodi: "GET",
                aikakatkaisu: Duration::from_secs(30),
                yritykset: 1,
            },
        }
    }

    fn metodi(mut self, metodi: &'static str) -> Self {
        self.pyynto.metodi = metodi;
        self
    }

    fn aikakatkaisu(mut self, aika: Duration) -> Self {
        self.pyynto.aikakatkaisu = aika;
        self
    }

    fn yritykset(mut self, n: u32) -> Self {
        self.pyynto.yritykset = n.max(1);
        self
    }

    fn rakenna(self) -> Pyynto {
        self.pyynto
    }
}
// @loppu rakentaja

fn main() {
    // @alku kaytto
    let oletus = PyyntoRakentaja::new("https://example.org/api").rakenna();
    let tallennus = PyyntoRakentaja::new("https://example.org/api/tilaus")
        .metodi("POST")
        .aikakatkaisu(Duration::from_millis(2500))
        .yritykset(3)
        .rakenna();
    println!("{oletus:#?}");
    println!("{} {} {:?} {}", tallennus.metodi, tallennus.osoite,
             tallennus.aikakatkaisu, tallennus.yritykset);
    // @loppu kaytto
}
