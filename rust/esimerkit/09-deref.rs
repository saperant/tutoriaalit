use std::rc::Rc;

// @alku deref
fn tavuja(teksti: &str) -> usize {
    teksti.len()
}

fn summa(arvot: &[f64]) -> f64 {
    arvot.iter().sum()
}

fn main() {
    let nimi = String::from("Ääkköset");
    let mittaukset = vec![1.5, 2.5];
    let jaetut = Rc::new(vec![1.0, 2.0, 3.0]);

    // &String kelpaa &str-parametrille ja &Vec<f64> viipaleeksi.
    println!("{} {}", tavuja(&nimi), summa(&mittaukset));
    // Kaksi askelta: &Rc<Vec<f64>> -> &Vec<f64> -> &[f64].
    println!("{}", summa(&jaetut));
    // Metodikutsu etsii metodia samaa ketjua pitkin: len on Vecin
    // metodi ja first viipaleen.
    println!("{} {:?}", jaetut.len(), jaetut.first());
}
// @loppu deref
