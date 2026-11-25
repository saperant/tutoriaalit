import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.Locale;

// @alku luokka
/** Pankkitili, jonka saldo ei voi mennä negatiiviseksi. */
final class Tili {
    /** Luokan yhteinen vakio: yksi arvo, ei oliokohtainen. */
    static final long KERTANOSTON_RAJA_SNT = 100_000;
    private static int seuraavaNumero = 1001;

    private final int numero;       // asetetaan kerran konstruktorissa
    private final String omistaja;
    private long saldoSnt;          // muuttuva tila, vain metodien kautta

    /** Konstruktori tarkistaa argumentit ja alustaa kentät. */
    Tili(String omistaja, long alkusaldoSnt) {
        if (omistaja.isBlank()) {
            throw new IllegalArgumentException("omistaja puuttuu");
        }
        if (alkusaldoSnt < 0) {
            throw new IllegalArgumentException("negatiivinen alkusaldo");
        }
        this.numero = seuraavaNumero++;
        this.omistaja = omistaja;
        this.saldoSnt = alkusaldoSnt;
    }

    /** Toinen konstruktori delegoi ensimmäiselle. */
    Tili(String omistaja) {
        this(omistaja, 0);
    }
    // @loppu luokka

    // @alku metodit
    void pane(long snt) {
        if (snt <= 0) {
            throw new IllegalArgumentException("summan on oltava > 0");
        }
        saldoSnt += snt;
    }

    void nosta(long snt) {
        if (snt <= 0 || snt > KERTANOSTON_RAJA_SNT) {
            throw new IllegalArgumentException("virheellinen summa");
        }
        if (snt > saldoSnt) {
            throw new IllegalStateException("kate ei riitä: saldo "
                    + euroina(saldoSnt));
        }
        saldoSnt -= snt;
    }

    /** Lukumetodi: kenttä näkyy ulos vain luettavana. */
    long saldoSnt() {
        return saldoSnt;
    }

    /** Staattinen metodi: kutsutaan luokan nimellä, ei oliolla. */
    static int avattuja() {
        return seuraavaNumero - 1001;
    }

    private static String euroina(long snt) {
        return String.format(Locale.ROOT, "%d,%02d €", snt / 100,
                snt % 100);
    }

    /** Korvaa Object-luokan metodin: olion esitys tekstinä. */
    @Override
    public String toString() {
        return "Tili " + numero + " (" + omistaja + "): "
                + euroina(saldoSnt);
    }
    // @loppu metodit
}

/** Luokan rakenne: kentät, konstruktorit, metodit ja static-jäsenet. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku kaytto
        Tili tili = new Tili("Maija Virtanen", 25_000);
        tili.pane(4_950);
        tili.nosta(12_000);
        System.out.println(tili);          // kutsuu toString-metodia
        try {
            tili.nosta(50_000);
        } catch (IllegalStateException e) {
            System.out.println("virhe: " + e.getMessage());
        }
        Tili toinen = new Tili("Pekka Mäki");
        System.out.println(toinen + ", saldo " + toinen.saldoSnt());
        System.out.println("tilejä avattu: " + Tili.avattuja());
        // @loppu kaytto
    }
}
