fn keskiarvo(summa: i64, maara: usize) -> f64 {
    summa as f64 / maara as f64
}

fn main() {
    let mittaukset: Vec<i32> = vec![12, 15, 9];
    let summa: i32 = mittaukset.iter().sum();
    println!("{}", keskiarvo(summa, mittaukset.len())); // @virhe: i32 ≠ i64
    println!("{}", keskiarvo(i64::from(summa), mittaukset.len()));
}
