fn main() {
    // @alku lausekkeet
    let lampotila = -3;
    let kuvaus = if lampotila < 0 { "pakkasta" } else { "lämmintä" };
    println!("{kuvaus}");
    // @loppu lausekkeet

    // @alku loop
    // loop palauttaa arvon break-lauseella.
    let mut yritys = 0;
    let tulos = loop {
        yritys += 1;
        if yritys * yritys > 50 {
            break yritys;
        }
    };
    println!("pienin n, jolle n² > 50: {tulos}");
    // @loppu loop

    // @alku nimetty
    let ruudukko = [[3, 8, 1], [9, 4, 7], [2, 6, 5]];
    let mut loytyi = None;
    'rivit: for (r, rivi) in ruudukko.iter().enumerate() {
        for (s, &arvo) in rivi.iter().enumerate() {
            if arvo > 8 {
                loytyi = Some((r, s));
                break 'rivit;
            }
        }
    }
    println!("ensimmäinen yli 8: {loytyi:?}");
    // @loppu nimetty

    // @alku whilelet
    let mut pino = vec!["a", "b", "c"];
    while let Some(ylin) = pino.pop() {
        print!("{ylin} ");
    }
    println!();
    for i in (1..=10).rev().step_by(3) {
        print!("{i} ");
    }
    println!();
    // @loppu whilelet
}
