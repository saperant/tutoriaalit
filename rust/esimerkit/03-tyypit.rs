fn main() {
    // @alku perustyypit
    let tavu: u8 = 200;
    let mittaus: i32 = -40;
    let koko: usize = 3; // indeksit ja pituudet
    let lampotila: f64 = 21.5;
    let valmis: bool = true;
    let merkki: char = 'ä'; // Unicode-skalaari, 4 tavua
    let pari: (i32, &str) = (7, "seitsemän");
    println!("{tavu} {mittaus} {koko} {lampotila} {valmis} {merkki}");
    println!("{} {} ({} tavua)", pari.0, pari.1, std::mem::size_of::<char>());
    // @loppu perustyypit

    // @alku muunnokset
    let pieni: i32 = 70_000;
    let laaja: i64 = i64::from(pieni); // häviötön: aina onnistuu
    let kapea = u16::try_from(pieni); // voi epäonnistua
    let katkaistu = pieni as u16; // as katkaisee hiljaa, kuten C
    println!("{laaja} {kapea:?} {katkaistu}");
    // @loppu muunnokset

    // @alku ylivuoto
    let a: u8 = 250;
    println!("checked:    {:?}", a.checked_add(10));
    println!("wrapping:   {}", a.wrapping_add(10));
    println!("saturating: {}", a.saturating_add(10));
    let (arvo, ylivuoti) = a.overflowing_add(10);
    println!("overflowing: {arvo} {ylivuoti}");
    // @loppu ylivuoto

    // @alku varjostus
    let syote = " 42 ";
    let syote = syote.trim(); // uusi muuttuja samalla nimellä
    let syote: i32 = syote.parse().expect("testisyöte on luku");
    println!("{}", syote * 2);
    // @loppu varjostus
}
