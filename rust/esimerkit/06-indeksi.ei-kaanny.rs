fn main() {
    let tunnus = String::from("Ärrä-42");
    let eka = tunnus[0]; // @virhe: merkkijonoa ei voi indeksoida
    println!("{eka}"); // @virhe
    let eka = tunnus.chars().next();
    println!("{eka:?}");
}
