import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.List;
import java.util.Locale;

/** Myyntirivi: tuote, kappalemäärä ja kappalehinta sentteinä. */
record Myynti(String tuote, int kpl, long snt) {
}

// @alku rajapinta
/** Rajapinta kertoo, mitä viejä osaa, ei miten se sen tekee. */
interface Vienti {
    String vie(List<Myynti> rivit);
}
// @loppu rajapinta

// @alku abstrakti
/** Taulukkomuotojen yhteinen runko: otsikko, rivit ja summarivi. */
abstract class Taulukkovienti implements Vienti {
    private final String nimi;

    protected Taulukkovienti(String nimi) {
        this.nimi = nimi;
    }

    /** Mallimetodi: vaiheiden järjestys on kiinteä (final). */
    @Override
    public final String vie(List<Myynti> rivit) {
        var sb = new StringBuilder("[" + nimi + "]\n");
        sb.append(otsikko()).append('\n');
        int kappaleet = 0;
        long summa = 0;
        for (Myynti m : rivit) {
            long rivisumma = m.kpl() * m.snt();
            sb.append(rivi(m.tuote(), m.kpl(), rivisumma)).append('\n');
            kappaleet += m.kpl();
            summa += rivisumma;
        }
        sb.append(yhteensa(kappaleet, summa)).append('\n');
        return sb.toString();
    }

    /** Abstraktit metodit: aliluokan on toteutettava nämä. */
    protected abstract String otsikko();

    protected abstract String rivi(String tuote, int kpl, long snt);

    /** Oletustoteutus, jonka aliluokka saa korvata. */
    protected String yhteensa(int kpl, long snt) {
        return rivi("yhteensä", kpl, snt);
    }
}
// @loppu abstrakti

// @alku aliluokat
final class CsvVienti extends Taulukkovienti {
    CsvVienti() {
        super("csv");               // yliluokan konstruktori ensin
    }

    @Override
    protected String otsikko() {
        return "tuote;kpl;snt";
    }

    @Override
    protected String rivi(String tuote, int kpl, long snt) {
        return tuote + ";" + kpl + ";" + snt;
    }
}

final class Tekstivienti extends Taulukkovienti {
    private final int leveys;

    Tekstivienti(int leveys) {
        super("teksti");
        this.leveys = leveys;
    }

    @Override
    protected String otsikko() {
        return String.format("%-" + leveys + "s %3s %8s", "Tuote", "kpl",
                "euroa");
    }

    @Override
    protected String rivi(String tuote, int kpl, long snt) {
        return String.format(Locale.ROOT, "%-" + leveys + "s %3d %5d,%02d",
                tuote, kpl, snt / 100, snt % 100);
    }

    /** Korvaa oletuksen ja kutsuu sitä super-viitteellä. */
    @Override
    protected String yhteensa(int kpl, long snt) {
        return "-".repeat(leveys + 13) + "\n" + super.yhteensa(kpl, snt);
    }
}
// @loppu aliluokat

/** Rajapinta, abstrakti luokka ja kaksi aliluokkaa. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        List<Myynti> myynnit = List.of(new Myynti("kahvi", 3, 695),
                new Myynti("suodatinpussit", 1, 249));
        List<Vienti> viennit = List.of(new CsvVienti(),
                new Tekstivienti(14),
                rivit -> "[määrä]\n" + rivit.size() + " riviä\n");
        for (Vienti vienti : viennit) {
            System.out.println(vienti.vie(myynnit));
        }
        Vienti v = new CsvVienti();     // muuttujan tyyppi on rajapinta
        System.out.println(v instanceof Taulukkovienti);
        System.out.println(v instanceof Tekstivienti);
        // @loppu kaytto
    }
}
