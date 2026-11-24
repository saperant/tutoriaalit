package fi.tutoriaalit.kauppa.raportti;

import java.lang.reflect.Proxy;
import java.sql.Connection;
import java.util.concurrent.atomic.AtomicInteger;
import javax.sql.DataSource;
import org.springframework.beans.factory.config.BeanPostProcessor;

/**
 * Testiapuri: kääri DataSource ja laske, montako SQL-lausetta
 * valmistellaan. Tuotannossa samaan käytetään esim. datasource-proxy-
 * kirjastoa tai tietokannan omaa kyselytilastoa.
 */
public class KyselyLaskuri implements BeanPostProcessor {

    private final AtomicInteger lauseet = new AtomicInteger();

    public int lauseet() {
        return lauseet.get();
    }

    public void nollaa() {
        lauseet.set(0);
    }

    @Override
    public Object postProcessAfterInitialization(Object papu, String nimi) {
        if (!(papu instanceof DataSource lahde)) {
            return papu;
        }
        return Proxy.newProxyInstance(getClass().getClassLoader(),
                new Class<?>[] {DataSource.class}, (p, metodi, arg) -> {
                    Object tulos = metodi.invoke(lahde, arg);
                    return tulos instanceof Connection c ? kaari(c) : tulos;
                });
    }

    private Connection kaari(Connection yhteys) {
        return (Connection) Proxy.newProxyInstance(
                getClass().getClassLoader(),
                new Class<?>[] {Connection.class}, (p, metodi, arg) -> {
                    if (metodi.getName().equals("prepareStatement")) {
                        lauseet.incrementAndGet();
                    }
                    return metodi.invoke(yhteys, arg);
                });
    }
}
