/** Javan merkkijono on UTF-16-koodiyksiköiden jono. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        String s = "Åbo \uD83D\uDE42"; // viimeisenä hymiö U+1F642
        System.out.println("length():         " + s.length());
        System.out.println("codePointCount(): "
                + s.codePointCount(0, s.length()));
        System.out.println("charAt(4):        U+"
                + Integer.toHexString(s.charAt(4)).toUpperCase());
        s.codePoints().forEach(cp -> System.out.printf("U+%04X %s%n",
                cp, Character.getName(cp)));
        // char on 16-bittinen etumerkitön kokonaisluku.
        char c = 'A';
        c += 2;
        System.out.println(c + " " + (int) c);
    }
}
