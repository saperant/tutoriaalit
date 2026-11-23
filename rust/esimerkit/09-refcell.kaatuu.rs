use std::cell::RefCell;

// @alku kaksoislaina
/// Tarkkailijalista RefCellissä. Ilmoituksen aikana lista on lainattu,
/// joten tarkkailija ei saa muuttaa sitä: käännösaikainen virhe
/// muuttuu ajonaikaiseksi paniikiksi.
struct Tapahtumat {
    kuuntelijat: RefCell<Vec<String>>,
}

impl Tapahtumat {
    fn ilmoita(&self, viesti: &str) {
        for k in self.kuuntelijat.borrow().iter() {
            println!("{k} <- {viesti}");
            if viesti == "sulje" {
                self.kuuntelijat.borrow_mut().clear(); // paniikki
            }
        }
    }
}
// @loppu kaksoislaina

fn main() {
    let t = Tapahtumat {
        kuuntelijat: RefCell::new(vec!["loki".into(), "ui".into()]),
    };
    t.ilmoita("avaa");
    t.ilmoita("sulje");
}
