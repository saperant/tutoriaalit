import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.function.Function;

/** Geneeriset metodit, rajatut tyyppiparametrit ja jokerit (PECS). */
final class Main {
    private Main() {
    }

    // @alku suurin
    /** Suurin alkio; T:n ei tarvitse itse olla Comparable<T>. */
    static <T extends Comparable<? super T>> T suurin(Collection<T> alkiot) {
        if (alkiot.isEmpty()) {
            throw new IllegalArgumentException("tyhjä kokoelma");
        }
        T paras = null;
        for (T a : alkiot) {
            if (paras == null || a.compareTo(paras) > 0) {
                paras = a;
            }
        }
        return paras;
    }
    // @loppu suurin

    // @alku pecs
    /**
     * PECS: producer extends, consumer super. Lähteestä luetaan,
     * kohteeseen kirjoitetaan.
     */
    static <T, R> void muunna(List<? extends T> lahde,
            Function<? super T, ? extends R> f, Collection<? super R> kohde) {
        for (T alkio : lahde) {
            kohde.add(f.apply(alkio));
        }
    }
    // @loppu pecs

    public static void main(String[] args) {
        // @alku kaytto
        System.out.println(suurin(List.of(3, 9, 4)));
        System.out.println(suurin(List.of("omena", "banaani")));

        List<Integer> kokonaisluvut = List.of(1, 2, 3);
        List<Number> luvut = new ArrayList<>();
        Function<Number, Double> puolitus = n -> n.doubleValue() / 2;
        muunna(kokonaisluvut, puolitus, luvut);
        System.out.println(luvut);

        // Tyyppien poisto: ajonaikana lista on vain List.
        System.out.println(new ArrayList<Integer>().getClass()
                == new ArrayList<String>().getClass());
        // @loppu kaytto
    }
}
