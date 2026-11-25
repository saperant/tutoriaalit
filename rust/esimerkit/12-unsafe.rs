// @alku jaa
/// Oma toteutus standardikirjaston split_at_mut-funktiosta. Lainaus-
/// tarkistin ei näe, että puolikkaat eivät mene päällekkäin, joten
/// toteutus tarvitsee unsafea. Rajapinta on silti turvallinen: kaikki
/// ehdot tarkistetaan ennen unsafe-lohkoa.
fn jaa_kahtia(viipale: &mut [u32], kohta: usize)
    -> (&mut [u32], &mut [u32])
{
    let pituus = viipale.len();
    assert!(kohta <= pituus, "jakokohta {kohta} > pituus {pituus}");
    let alku = viipale.as_mut_ptr();
    // SAFETY: kohta <= pituus, joten molemmat osat ovat saman varauksen
    // sisällä, eivätkä ne mene päällekkäin. Elinaika sidotaan
    // alkuperäiseen lainaan funktion allekirjoituksessa.
    unsafe {
        (
            std::slice::from_raw_parts_mut(alku, kohta),
            std::slice::from_raw_parts_mut(alku.add(kohta), pituus - kohta),
        )
    }
}
// @loppu jaa

// @alku asettelu
/// repr(C) takaa C:n mukaisen kenttäjärjestyksen ja täytteen. Ilman sitä
/// Rust saa järjestää kentät uudelleen tilan säästämiseksi.
#[repr(C)]
struct COtsake {
    tyyppi: u8,
    pituus: u32,
    lippu: u8,
}

struct RustOtsake {
    _tyyppi: u8,
    _pituus: u32,
    _lippu: u8,
}
// @loppu asettelu

fn main() {
    // @alku raaka
    let mut arvo = 7_i32;
    let osoitin: *mut i32 = &mut arvo; // luonti on turvallista
    // SAFETY: osoitin on luotu elävästä muuttujasta, eikä muita
    // viitteitä siihen ole käytössä.
    unsafe { *osoitin += 1 };
    println!("{arvo}");
    // @loppu raaka

    // @alku kaytto
    let mut naytteet = [1, 2, 3, 4, 5, 6];
    let (vasen, oikea) = jaa_kahtia(&mut naytteet, 2);
    vasen[0] = 100;
    oikea[0] = 300;
    println!("{naytteet:?}");

    let otsake = COtsake { tyyppi: 1, pituus: 512, lippu: 0 };
    println!("repr(C): {} tavua, Rust: {} tavua",
             std::mem::size_of::<COtsake>(),
             std::mem::size_of::<RustOtsake>());
    println!("{} {} {}", otsake.tyyppi, otsake.pituus, otsake.lippu);
    // @loppu kaytto
}
