package fi.tutoriaalit.palvelut.kauppa;

import static org.assertj.core.api.Assertions.assertThatThrownBy;

import com.tngtech.archunit.core.domain.JavaClasses;
import com.tngtech.archunit.core.importer.ClassFileImporter;
import com.tngtech.archunit.core.importer.ImportOption;
import com.tngtech.archunit.lang.ArchRule;
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition;
import com.tngtech.archunit.library.dependencies.SlicesRuleDefinition;
import fi.tutoriaalit.palvelut.kauppa.laskutus.Oikopolku;
import fi.tutoriaalit.palvelut.kauppa.varasto.sisainen.SaldoTaulu;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.ValueSource;

/** Moduulirajat ovat testejä: rikkomus kaataa käännöksen. */
class ModuulirajatTest {
    static final String JUURI = "fi.tutoriaalit.palvelut.kauppa";
    static final JavaClasses LUOKAT = new ClassFileImporter()
        .withImportOption(ImportOption.Predefined.DO_NOT_INCLUDE_TESTS)
        .importPackages(JUURI);

    // @alku saannot
    /** Moduulin sisäistä pakettia saa käyttää vain moduuli itse. */
    static ArchRule sisainen(String moduuli) {
        String paketti = JUURI + "." + moduuli;
        return ArchRuleDefinition.noClasses()
            .that().resideOutsideOfPackage(paketti + "..")
            .should().dependOnClassesThat()
            .resideInAPackage(paketti + ".sisainen..")
            .because("moduulin " + moduuli + " sisäosat ovat sen omia");
    }

    @ParameterizedTest
    @ValueSource(strings = {"myynti", "varasto", "laskutus"})
    void sisaosiinEiViitataMuualta(String moduuli) {
        sisainen(moduuli).check(LUOKAT);
    }

    @Test
    void moduulienValillaEiOleSyklejä() {
        SlicesRuleDefinition.slices().matching(JUURI + ".(*)..")
            .should().beFreeOfCycles().check(LUOKAT);
    }

    @Test
    void myyntiEiTunneMuitaModuuleja() {
        ArchRuleDefinition.noClasses()
            .that().resideInAPackage(JUURI + ".myynti..")
            .should().dependOnClassesThat().resideInAnyPackage(
                JUURI + ".varasto..", JUURI + ".laskutus..")
            .check(LUOKAT);
    }
    // @loppu saannot

    // @alku rikkomus
    @Test
    void saantoHuomaaOikopolun() {
        // Testikoodin Oikopolku lukee varaston taulua suoraan.
        JavaClasses rikkova = new ClassFileImporter()
            .importClasses(Oikopolku.class, SaldoTaulu.class);
        assertThatThrownBy(() -> sisainen("varasto").check(rikkova))
            .hasMessageContaining("Oikopolku")
            .hasMessageContaining("SaldoTaulu");
    }
    // @loppu rikkomus
}
