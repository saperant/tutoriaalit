fn main() {
    // @alku utf8
    let sana = "Hääyö";
    println!("tavuja {}, merkkejä {}", sana.len(), sana.chars().count());
    println!("ensimmäinen merkki: {:?}", sana.chars().next());
    println!("tavut 0..2: {:?}", sana.get(0..2));
    println!("tavut 0..3: {:?}", sana.get(0..3)); // ä alkaa tavusta 1
    // @loppu utf8

    // @alku muokkaus
    let mut nimi = String::with_capacity(16); // varaa kerralla
    nimi.push_str("ada");
    nimi.push(' ');
    nimi += "lovelace";
    let isot: String = nimi
        .split(' ')
        .map(|osa| {
            let mut merkit = osa.chars();
            match merkit.next() {
                Some(eka) => eka.to_uppercase().chain(merkit).collect(),
                None => String::new(),
            }
        })
        .collect::<Vec<String>>()
        .join(" ");
    println!("{isot}");
    // @loppu muokkaus

    // @alku jasennys
    let otsake = "Content-Type: text/html; charset=utf-8";
    if let Some((avain, arvo)) = otsake.split_once(": ") {
        let parametrit: Vec<&str> = arvo.split(';').map(str::trim).collect();
        println!("{avain} -> {parametrit:?}");
    }
    let luvut: Result<Vec<i32>, _> =
        "1,2,x,4".split(',').map(str::parse).collect();
    println!("{luvut:?}");
    // @loppu jasennys
}
