//! Integraatiotesti: käyttää cratea kuten ulkopuolinen käyttäjä.

// @alku integraatio
use kesto::{jasenna, muotoile};

#[test]
fn muotoiltu_kesto_jasentyy_samaksi() {
    for sekunnit in (0..200_000).step_by(37) {
        assert_eq!(jasenna(&muotoile(sekunnit)), Ok(sekunnit));
    }
}
// @loppu integraatio
