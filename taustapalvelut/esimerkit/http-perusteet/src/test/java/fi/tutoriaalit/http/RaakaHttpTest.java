package fi.tutoriaalit.http;

import static org.assertj.core.api.Assertions.assertThat;

import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;
import java.nio.charset.StandardCharsets;
import org.junit.jupiter.api.Test;

/** HTTP/1.1 on tekstiä: lähetetään pyyntö käsin pistokkeeseen. */
class RaakaHttpTest {

    private static String resurssi(String nimi) throws IOException {
        try (InputStream in = RaakaHttpTest.class.getResourceAsStream(nimi)) {
            return new String(in.readAllBytes(), StandardCharsets.UTF_8);
        }
    }

    private static String keskustele(int portti, String pyynto)
            throws IOException {
        try (var pistoke = new Socket("127.0.0.1", portti)) {
            pistoke.getOutputStream().write(
                    pyynto.replace("\n", "\r\n")
                            .getBytes(StandardCharsets.UTF_8));
            String vastaus = new String(
                    pistoke.getInputStream().readAllBytes(),
                    StandardCharsets.UTF_8);
            // Päiväys vaihtelee; muu vastaus on täsmälleen ennustettava.
            return vastaus.replace("\r\n", "\n")
                    .replaceAll("(?m)^Date: .*\n", "Date: (aika)\n");
        }
    }

    @Test
    void pyyntoJaVastausOvatTekstia() throws IOException {
        try (var palvelin = new MuistioPalvelin(0)) {
            palvelin.kaynnista();
            String vastaus = keskustele(palvelin.portti(),
                    resurssi("/pyynto-post.txt"));
            assertThat(vastaus).isEqualTo(resurssi("/vastaus-post.txt"));
        }
    }
}
