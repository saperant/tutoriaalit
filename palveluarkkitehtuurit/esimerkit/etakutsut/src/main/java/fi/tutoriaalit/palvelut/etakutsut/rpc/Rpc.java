package fi.tutoriaalit.palvelut.etakutsut.rpc;

import fi.tutoriaalit.palvelut.etakutsut.Palvelin;
import java.io.IOException;
import java.io.UncheckedIOException;
import java.lang.reflect.InvocationTargetException;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.Arrays;
import tools.jackson.databind.JsonNode;
import tools.jackson.databind.json.JsonMapper;

/**
 * Etäproseduurikutsu (RPC) pienimmillään: rajapinnan toteutus julkaistaan
 * HTTP:n yli, ja asiakas saa saman rajapinnan dynaamisena välittäjänä.
 * Kutsu näyttää paikalliselta, mutta ei ole sitä.
 */
public final class Rpc {
    private static final JsonMapper JSON = new JsonMapper();

    private Rpc() {
    }

    // @alku palvelin
    /** POST /{metodi}, runkona argumentit JSON-taulukkona. */
    public static <T> Palvelin julkaise(Class<T> rajapinta, T toteutus) {
        return Palvelin.kaynnista(vaihto -> {
            String nimi = vaihto.getRequestURI().getPath().substring(1);
            Method metodi = metodi(rajapinta, nimi);
            JsonNode argumentit = JSON.readTree(Palvelin.runko(vaihto));
            Object[] arvot = new Object[metodi.getParameterCount()];
            for (int i = 0; i < arvot.length; i++) {
                arvot[i] = JSON.treeToValue(argumentit.get(i),
                        metodi.getParameterTypes()[i]);
            }
            try {
                Object tulos = metodi.invoke(toteutus, arvot);
                Palvelin.vastaa(vaihto, 200, JSON.writeValueAsString(tulos));
            } catch (InvocationTargetException e) {
                Palvelin.vastaa(vaihto, 500, JSON.writeValueAsString(
                        e.getCause().getMessage()));
            } catch (IllegalAccessException e) {
                throw new IllegalStateException(e);
            }
        });
    }
    // @loppu palvelin

    // @alku asiakas
    @SuppressWarnings("unchecked")
    public static <T> T asiakas(Class<T> rajapinta, URI osoite,
                                Duration aikaraja) {
        HttpClient http = HttpClient.newHttpClient();
        return (T) Proxy.newProxyInstance(rajapinta.getClassLoader(),
                new Class<?>[] {rajapinta}, (proxy, metodi, arvot) -> {
            String runko = JSON.writeValueAsString(
                    arvot == null ? new Object[0] : arvot);
            var pyynto = HttpRequest.newBuilder(
                        osoite.resolve("/" + metodi.getName()))
                    .timeout(aikaraja)
                    .POST(HttpRequest.BodyPublishers.ofString(runko))
                    .build();
            HttpResponse<String> vastaus;
            try {
                vastaus = http.send(pyynto,
                        HttpResponse.BodyHandlers.ofString());
            } catch (IOException e) {
                // Paikallinen kutsu ei koskaan heitä tätä.
                throw new UncheckedIOException(e);
            }
            if (vastaus.statusCode() != 200) {
                throw new RpcVirhe(JSON.readValue(vastaus.body(),
                        String.class));
            }
            return JSON.readValue(vastaus.body(), JSON.constructType(
                    metodi.getGenericReturnType()));
        });
    }
    // @loppu asiakas

    private static Method metodi(Class<?> rajapinta, String nimi) {
        return Arrays.stream(rajapinta.getMethods())
            .filter(m -> m.getName().equals(nimi)).findFirst()
            .orElseThrow();
    }
}
