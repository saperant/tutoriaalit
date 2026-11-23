use std::cmp::Ordering;
use std::ffi::{c_char, c_int, c_void, CStr, CString};

// @alku esittely
// C-kirjaston funktioiden esittely. Linkitys tapahtuu libc:tä vastaan,
// joka on joka tapauksessa mukana. Kääntäjä ei voi tarkistaa, että
// allekirjoitukset vastaavat C:n otsikkotiedostoja: se on ohjelmoijan
// vastuulla (bindgen tuottaa ne automaattisesti).
extern "C" {
    fn strlen(s: *const c_char) -> usize;
    fn snprintf(buf: *mut c_char, n: usize, fmt: *const c_char, ...)
        -> c_int;
    fn qsort(
        alku: *mut c_void,
        lkm: usize,
        koko: usize,
        vertaa: extern "C" fn(*const c_void, *const c_void) -> c_int,
    );
}
// @loppu esittely

// @alku kaareet
/// Turvallinen kääre: CStr takaa NUL-päätteen, joten kutsu on aina
/// kelvollinen. Kutsujan ei tarvitse kirjoittaa unsafe.
fn c_pituus(s: &CStr) -> usize {
    // SAFETY: s.as_ptr() osoittaa NUL-päätteiseen merkkijonoon, joka
    // elää vähintään kutsun ajan.
    unsafe { strlen(s.as_ptr()) }
}

/// Muotoilee luvun C:n printf-tyylillä. Virhe palautetaan Resultina.
fn c_muotoile(arvo: f64, desimaalit: c_int) -> Result<String, String> {
    let mut puskuri = vec![0u8; 64];
    // SAFETY: puskurin koko välitetään, joten snprintf ei kirjoita
    // sen yli; muotoilujono vastaa argumentteja (%.*f: int, double).
    let n = unsafe {
        snprintf(puskuri.as_mut_ptr().cast(), puskuri.len(),
                 c"%.*f".as_ptr(), desimaalit, arvo)
    };
    let n = usize::try_from(n).map_err(|_| "snprintf epäonnistui")?;
    if n >= puskuri.len() {
        return Err(format!("tulos katkesi ({n} merkkiä)"));
    }
    puskuri.truncate(n);
    String::from_utf8(puskuri).map_err(|e| e.to_string())
}

extern "C" fn vertaa_i32(a: *const c_void, b: *const c_void) -> c_int {
    // SAFETY: qsort antaa osoittimet lajiteltavan i32-taulukon alkioihin.
    let (a, b) = unsafe { (*a.cast::<i32>(), *b.cast::<i32>()) };
    match a.cmp(&b) {
        Ordering::Less => -1,
        Ordering::Equal => 0,
        Ordering::Greater => 1,
    }
}

fn c_lajittele(luvut: &mut [i32]) {
    // SAFETY: osoitin, pituus ja alkion koko kuvaavat saman viipaleen,
    // ja vertailufunktio vastaa alkiotyyppiä.
    unsafe {
        qsort(luvut.as_mut_ptr().cast(), luvut.len(),
              std::mem::size_of::<i32>(), vertaa_i32);
    }
}
// @loppu kaareet

fn main() {
    // @alku kaytto
    let nimi = CString::new("Ääkköset").expect("ei NUL-tavuja");
    println!("C:n mukaan {} tavua", c_pituus(&nimi));
    println!("{:?}", CString::new("väli\0NUL").map_err(|e| e.to_string()));
    println!("{:?}", c_muotoile(std::f64::consts::PI, 3));
    let mut luvut = [42, -7, 0, 19, -7];
    c_lajittele(&mut luvut);
    println!("{luvut:?}");
    // @loppu kaytto
}
