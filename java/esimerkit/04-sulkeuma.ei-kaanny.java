import java.util.List;
import java.util.function.Predicate;

/** Lambda saa käyttää vain käytännössä vakioita paikallisia muuttujia. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        // @alku koodi
        int raja = 100;
        raja = 200; // @virhe: muuttuja ei ole enää käytännössä vakio
        Predicate<Integer> suuri = n -> n > raja;
        // @loppu koodi
        System.out.println(List.of(50, 150, 250).stream()
                .filter(suuri).toList());
    }
}
