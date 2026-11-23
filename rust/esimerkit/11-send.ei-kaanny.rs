use std::rc::Rc; // @virhe
use std::sync::Arc;
use std::thread;

// @alku send
fn main() {
    let sanat = Arc::new(vec!["muisti", "turva"]);
    let kopio = Arc::clone(&sanat);
    // Rc:n viitelaskuri ei ole atominen, joten Rc ei ole Send, eikä
    // mikään sitä sisältävä tyyppi. Kääntäjä estää siirron säikeeseen.
    let kopio = Rc::new(kopio); // @virhe
    let kahva = thread::spawn(move || kopio.len());
    println!("{} {}", kahva.join().expect("säie"), sanat[0]);
}
// @loppu send
