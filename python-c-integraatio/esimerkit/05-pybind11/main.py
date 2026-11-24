"""pybind11-laajennuksen käyttö: luokka, ominaisuudet ja poikkeukset."""

import mittari


def main() -> None:
    # @alku kaytto
    t = mittari.Tilasto()
    for arvo in (20.1, 20.4, 19.8, 20.3):
        t.lisaa(arvo)
    print(t, f"keskiarvo {t.keskiarvo:.3f}, hajonta {t.hajonta:.3f}")
    print("pituus:", len(t))
    print("funktio:", mittari.keskiarvo([1.0, 2.0, 3.0]))
    # @loppu kaytto

    # @alku poikkeukset
    try:
        _ = mittari.Tilasto().keskiarvo
    except mittari.TyhjaOtos as e:
        print("TyhjaOtos:", e, "| ValueError:", isinstance(e, ValueError))
    try:
        t.lisaa(float("nan"))
    except ValueError as e:              # std::invalid_argument
        print("ValueError:", e)
    try:
        t.lisaa("kaksikymmentä")         # type: ignore[arg-type]
    except TypeError as e:
        print("TypeError:", str(e).split(".")[0])
    # @loppu poikkeukset


if __name__ == "__main__":
    main()
