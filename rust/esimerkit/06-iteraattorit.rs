#[derive(Debug)]
struct Tilaus {
    asiakas: &'static str,
    summa_snt: u64,
    toimitettu: bool,
}

fn main() {
    let tilaukset = [
        Tilaus { asiakas: "Ada", summa_snt: 12_950, toimitettu: true },
        Tilaus { asiakas: "Bjarne", summa_snt: 4_500, toimitettu: false },
        Tilaus { asiakas: "Grace", summa_snt: 30_000, toimitettu: true },
        Tilaus { asiakas: "Ada", summa_snt: 2_000, toimitettu: true },
    ];

    // @alku ketju
    let toimitetut_euroina: Vec<String> = tilaukset
        .iter()
        .filter(|t| t.toimitettu)
        .map(|t| {
            format!("{} {:.2} €", t.asiakas, t.summa_snt as f64 / 100.0)
        })
        .collect();
    println!("{toimitetut_euroina:?}");
    // @loppu ketju

    // @alku koosteet
    let yhteensa: u64 = tilaukset.iter().map(|t| t.summa_snt).sum();
    let suurin = tilaukset.iter().max_by_key(|t| t.summa_snt);
    let kaikki_yli_10 = tilaukset.iter().all(|t| t.summa_snt > 1_000);
    let adan = tilaukset.iter().filter(|t| t.asiakas == "Ada").count();
    println!("{yhteensa} {:?} {kaikki_yli_10} {adan}",
             suurin.map(|t| t.asiakas));
    // @loppu koosteet

    // @alku ikkunat
    let lampotilat = [3, 5, 4, 8, 12, 11];
    let nousut: Vec<i32> = lampotilat
        .windows(2)
        .map(|w| w[1] - w[0])
        .collect();
    println!("muutokset {nousut:?}");
    for (i, pari) in lampotilat.chunks(2).enumerate() {
        print!("{i}:{pari:?} ");
    }
    println!();
    // @loppu ikkunat

    // @alku laiska
    // Iteraattorit ovat laiskoja: mitään ei lasketa ennen kulutusta.
    let ensimmainen_parillinen_nelio = (1..)
        .map(|n: u64| n * n)
        .find(|n| n % 2 == 0 && *n > 50);
    println!("{ensimmainen_parillinen_nelio:?}");
    // @loppu laiska

    // @alku sulkeuma
    let raja = 5_000;
    let isot = |t: &&Tilaus| t.summa_snt >= raja; // sieppaa rajan
    let mut nimet: Vec<&str> =
        tilaukset.iter().filter(isot).map(|t| t.asiakas).collect();
    nimet.sort_unstable();
    nimet.dedup();
    println!("{nimet:?}");
    // @loppu sulkeuma
}
