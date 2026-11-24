// JDBC-tason DAO: Javan vastine Pythonin DB-API:lle (esimerkki 15-dao.py).
// Käännetään testissä javacilla; ajoon tarvittaisiin JDBC-ajuri.
import java.sql.Connection;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.Optional;

public final class TuoteDao {
    public record Tuote(String koodi, String nimi, int hinta) {}

    private final Connection yhteys;

    public TuoteDao(Connection yhteys) {
        this.yhteys = yhteys;
    }

    // @alku hae
    public Optional<Tuote> hae(String koodi) throws SQLException {
        String sql = "SELECT koodi, nimi, hinta FROM tuote WHERE koodi = ?";
        try (PreparedStatement lause = yhteys.prepareStatement(sql)) {
            lause.setString(1, koodi);                 // parametri, ei
            try (ResultSet rivit = lause.executeQuery()) {  // liitosta
                if (!rivit.next()) {
                    return Optional.empty();
                }
                return Optional.of(new Tuote(rivit.getString("koodi"),
                        rivit.getString("nimi"), rivit.getInt("hinta")));
            }
        }
    }
    // @loppu hae
}
