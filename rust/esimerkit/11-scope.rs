use std::thread;

// @alku scope
/// Rinnakkainen histogrammi. thread::scope takaa, että säikeet päättyvät
/// ennen kuin lohko palaa, joten ne saavat lainata pinossa olevaa dataa
/// ilman Arcia tai kopiointia.
fn histogrammi(data: &[u8], saikeita: usize) -> [u64; 256] {
    let palan_koko = data.len().div_ceil(saikeita).max(1);
    let osat: Vec<[u64; 256]> = thread::scope(|s| {
        let kahvat: Vec<_> = data
            .chunks(palan_koko)
            .map(|pala| {
                s.spawn(move || {
                    let mut h = [0u64; 256];
                    for &tavu in pala {
                        h[usize::from(tavu)] += 1;
                    }
                    h
                })
            })
            .collect();
        kahvat.into_iter().map(|k| k.join().expect("säie")).collect()
    });
    // Yhdistetään vasta lopuksi: ei jaettua muuttuvaa tilaa.
    let mut tulos = [0u64; 256];
    for osa in &osat {
        for (t, o) in tulos.iter_mut().zip(osa) {
            *t += o;
        }
    }
    tulos
}
// @loppu scope

fn main() {
    // @alku kaytto
    let teksti = "rinnakkaisuus ilman datakilpailuja ".repeat(10_000);
    let h = histogrammi(teksti.as_bytes(), 4);
    let mut yleisimmat: Vec<(u8, u64)> = (0..=255u8)
        .map(|b| (b, h[usize::from(b)]))
        .filter(|&(_, n)| n > 0)
        .collect();
    yleisimmat.sort_by(|a, b| b.1.cmp(&a.1).then(a.0.cmp(&b.0)));
    for (tavu, n) in yleisimmat.iter().take(3) {
        println!("{:?}: {n}", char::from(*tavu));
    }
    assert_eq!(h, histogrammi(teksti.as_bytes(), 1));
    // @loppu kaytto
}
