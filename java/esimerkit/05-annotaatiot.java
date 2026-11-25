import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.Method;
import java.util.Arrays;
import java.util.Comparator;

// @alku annotaatio
/** Merkitsee metodin käynnistystarkistukseksi. */
@Retention(RetentionPolicy.RUNTIME)     // säilyy ajoon asti
@Target(ElementType.METHOD)             // sallittu vain metodeissa
@interface Tarkistus {
    String value();                     // kuvaus: @Tarkistus("…")
}

/** Palvelun käynnistystarkistukset. */
final class Tarkistukset {
    private Tarkistukset() {
    }

    @Tarkistus("portti on välillä 1–65535")
    static boolean portti() {
        int portti = Integer.getInteger("palvelu.portti", 8080);
        return portti >= 1 && portti <= 65_535;
    }

    @Tarkistus("muistia on vähintään 16 Mt")
    static boolean muisti() {
        return Runtime.getRuntime().maxMemory() >= 16L * 1024 * 1024;
    }

    @Tarkistus("Java-versio on vähintään 99")
    static boolean versio() {
        return Runtime.version().feature() >= 99;
    }

    /** Ei annotaatiota: ajuri ohittaa tämän. */
    static boolean apumetodi() {
        return true;
    }
}
// @loppu annotaatio

/** Oma annotaatio ja sen lukeminen reflektiolla. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) throws Exception {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku ajuri
        Method[] metodit = Tarkistukset.class.getDeclaredMethods();
        Arrays.sort(metodit, Comparator.comparing(Method::getName));
        for (Method metodi : metodit) {
            Tarkistus tarkistus = metodi.getAnnotation(Tarkistus.class);
            if (tarkistus == null) {
                continue;
            }
            boolean ok = (boolean) metodi.invoke(null);
            System.out.println((ok ? "OK     " : "VIRHE  ")
                    + tarkistus.value());
        }
        // @loppu ajuri
    }
}
