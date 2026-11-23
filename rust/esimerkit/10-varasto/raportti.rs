// @alku raportti
use std::fmt;

use crate::varasto::Varasto;

/// Raportti lainaa varastoa: se ei voi elää varastoa pidempään eikä
/// muuttaa sitä.
pub struct Raportti<'a> {
    varasto: &'a Varasto,
    raja: u32,
}

impl<'a> Raportti<'a> {
    pub fn new(varasto: &'a Varasto) -> Self {
        Raportti { varasto, raja: 0 }
    }

    /// Näytetään vain tuotteet, joiden saldo on alle rajan.
    pub fn vahissa(mut self, raja: u32) -> Self {
        self.raja = raja;
        self
    }
}

impl fmt::Display for Raportti<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        for (koodi, saldo) in self.varasto.saldot() {
            if saldo < self.raja {
                writeln!(f, "tilaa lisää: {koodi} (saldo {saldo})")?;
            }
        }
        Ok(())
    }
}
// @loppu raportti
