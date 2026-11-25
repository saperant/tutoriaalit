import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.util.Arrays;
import java.util.List;
import java.util.StringJoiner;

/** Merkkijonojen tavalliset sudenkuopat ja työkalut. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku split
        String csv = "Kahvi;6,95;;";
        System.out.println(Arrays.toString(csv.split(";")));
        System.out.println(Arrays.toString(csv.split(";", -1)));
        System.out.println(Arrays.toString("1.2.3".split(".")));
        System.out.println(Arrays.toString("1.2.3".split("\\.")));
        // @loppu split

        // @alku kokoaminen
        List<String> tuotteet = List.of("kahvi", "tee", "kaakao");
        StringBuilder sb = new StringBuilder();
        for (String t : tuotteet) {
            if (!sb.isEmpty()) {
                sb.append(", ");
            }
            sb.append(t);
        }
        System.out.println(sb);
        System.out.println(String.join(", ", tuotteet));
        var sj = new StringJoiner(", ", "[", "]");
        tuotteet.forEach(sj::add);
        System.out.println(sj);
        // @loppu kokoaminen

        // @alku muut
        String reunat = " \u2003väli\u2003 "; // U+2003 on em-väli
        System.out.println("strip: [" + reunat.strip() + "], trim: "
                + reunat.trim().length() + " merkkiä");
        System.out.println("abc".repeat(2) + " " + "Kahvi".indexOf('v')
                + " " + "  ".isBlank());
        String viesti = """
                Hei %s,
                tilauksesi %d on lähetetty.
                """.formatted("Maija", 42);
        System.out.print(viesti);
        // @loppu muut
    }
}
