package fi.tutoriaalit.palvelut.etakutsut.rpc;

/** Etäpään toteutus heitti poikkeuksen. */
public class RpcVirhe extends RuntimeException {
    public RpcVirhe(String viesti) {
        super(viesti);
    }
}
