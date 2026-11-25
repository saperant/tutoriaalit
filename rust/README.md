# Rust

Tiivis suomenkielinen Rust-tutoriaali C- ja C++-ohjelmoijalle (Rust
1.80, painos 2021). Valmis dokumentti: [rust.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rust.pdf), pikaopas:
[rust-pikaopas.pdf](https://saperant.github.io/tutoriaalit/materiaalit/rust-pikaopas.pdf).

## Sisältö

1. Johdanto – käyttökohteet, versiot ja painokset, työkalut
2. Rust kokeneelle – ajattelutapa, vastaavuudet C:hen ja C++:aan,
   hinnat, sudenkuopat
3. Tyypit, lausekkeet ja syöte – muunnokset, ylivuoto, muotoilu,
   `let-else`, tiedostot ja argumentit
4. Ohjausrakenteet, `enum` ja `match` – funktiot, tilakone, kattavuus,
   rekursiivisesti laskeutuva jäsennin
5. Omistajuus ja lainaus – siirto, `Copy`, lainaussäännöt, viipaleet,
   `Drop` ja RAII
6. Kokoelmat, merkkijonot ja iteraattorit – sulkeumat, `entry`, UTF-8
7. Rakenteet, piirteet ja geneerisyys – newtype, `dyn` vs. geneerinen,
   oma iteraattori, rakentaja, makrot
8. Virheenkäsittely – `?`, oma virhetyyppi, syyketju, paniikki
9. Älykkäät osoittimet ja elinajat – `Box`, `Deref`, `Rc`/`Weak`,
   `RefCell`, nollakopioinen jäsennin
10. Modulit, paketit ja Cargo – näkyvyys, invariantit, `Cargo.toml`
11. Säikeet, `Send`, `Sync` ja async – `scope`, kanavat, `Mutex`,
    atomiset tyypit, minimaalinen suorittaja
12. `unsafe` ja C-rajapinta – turvallinen kääre, `extern "C"`,
    `#[repr(C)]`
13. Työkalut, testaus ja laatu – profiilit, Clippy, testit,
    dokumentaatio ja doctestit
14. Lopuksi – mallit, nyrkkisäännöt, hinnat, kirjastot ja lähteet

## Rakentaminen

```text
make testaa   # Clippy (-D warnings), esimerkkien ajo ja Cargo-paketti
make pdf      # rakentaa rust.pdf:n ja rust-pikaopas.pdf:n
```

Riippuvuudet on lueteltu repositorion juuren README-tiedostossa.
Kehityskontti: `.devcontainer/rust`.

Esimerkkien avaaminen kehityskontissa ja ajaminen: ks. [Kehitysympäristöt ja Dev Containers](../kehitysymparistot/), luku 2.
