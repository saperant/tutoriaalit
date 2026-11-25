import static java.nio.charset.StandardCharsets.UTF_8;

import java.io.PrintStream;
import java.time.DayOfWeek;
import java.time.Duration;
import java.time.Instant;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.Period;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.time.format.DateTimeFormatter;
import java.time.temporal.ChronoUnit;
import java.time.temporal.TemporalAdjusters;
import java.util.Locale;

/** Aika: java.time-pakkauksen tyypit. */
final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        System.setOut(new PrintStream(System.out, true, UTF_8));
        // @alku hetki
        Instant alku = Instant.parse("2026-03-28T21:30:00Z");
        Instant loppu = alku.plus(Duration.ofMinutes(150));
        Duration kesto = Duration.between(alku, loppu);
        System.out.println(loppu + " " + kesto + " " + kesto.toMinutes());
        // @loppu hetki

        // @alku paiva
        LocalDate erapaiva = LocalDate.of(2026, 1, 31).plusMonths(1);
        LocalDate maanantai = erapaiva.with(
                TemporalAdjusters.next(DayOfWeek.MONDAY));
        Period vali = Period.between(LocalDate.of(2025, 11, 23), erapaiva);
        System.out.println(erapaiva + " " + erapaiva.getDayOfWeek() + " "
                + maanantai + " " + vali + " "
                + ChronoUnit.DAYS.between(erapaiva, maanantai));
        // @loppu paiva

        // @alku vyohyke
        ZoneId helsinki = ZoneId.of("Europe/Helsinki");
        ZonedDateTime lahto = LocalDateTime.of(2026, 3, 28, 23, 30)
                .atZone(helsinki);
        ZonedDateTime perilla = lahto.plusHours(6);
        System.out.println(lahto + " -> " + perilla);
        System.out.println(lahto.toInstant() + " "
                + perilla.withZoneSameInstant(ZoneId.of("Asia/Tokyo"))
                        .toLocalTime());
        // @loppu vyohyke

        // @alku muotoilu
        DateTimeFormatter suomi = DateTimeFormatter.ofPattern(
                "cccc d.M.yyyy 'klo' H.mm", Locale.forLanguageTag("fi"));
        System.out.println(suomi.format(perilla));
        System.out.println(DateTimeFormatter.ISO_OFFSET_DATE_TIME
                .format(perilla));
        System.out.println(LocalDate.parse("23.11.2026",
                DateTimeFormatter.ofPattern("d.M.yyyy")));
        // @loppu muotoilu
    }
}
