// @alku nakyvyys
mod aika {
    /// Kellonaika, jonka invariantti (h < 24, min < 60) taataan
    /// yksityisillä kentillä ja tarkistavalla muodostimella.
    pub struct Kellonaika {
        tunnit: u8,
        minuutit: u8,
    }

    impl Kellonaika {
        pub fn new(tunnit: u8, minuutit: u8) -> Option<Self> {
            (tunnit < 24 && minuutit < 60)
                .then_some(Kellonaika { tunnit, minuutit })
        }

        pub fn minuutteina(&self) -> u32 {
            u32::from(self.tunnit) * 60 + u32::from(self.minuutit)
        }
    }
}

use aika::Kellonaika;

fn main() {
    let rikki = Kellonaika { tunnit: 25, minuutit: 0 }; // @virhe
    let _ = rikki.minuutteina(); // @virhe
    let kokous = Kellonaika::new(14, 30).expect("kelvollinen aika");
    println!("{}", kokous.minuutteina());
    println!("{}", Kellonaika::new(25, 0).is_none());
}
// @loppu nakyvyys
