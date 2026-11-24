"""Säädettävä konsistenssi: kopioita 3, solmuja vain 1."""

from cassandra import ConsistencyLevel, Unavailable
from cassandra.policies import FallthroughRetryPolicy
from cassandra.query import SimpleStatement

from nosql.kontit import Ymparisto, aja


def ajo(ymp: Ymparisto) -> None:
    s = ymp.cassandra()
    s.execute("DROP KEYSPACE IF EXISTS kauppa07k")
    # @alku avaruus
    s.execute("""CREATE KEYSPACE kauppa07k WITH replication =
                 {'class': 'SimpleStrategy', 'replication_factor': 3}""")
    s.execute("""CREATE TABLE kauppa07k.korit (
                     kayttaja text PRIMARY KEY, tuotteet list<text>)""")
    # @loppu avaruus

    # @alku tasot
    for taso in ["ONE", "QUORUM", "ALL"]:
        lause = SimpleStatement(
            "INSERT INTO kauppa07k.korit (kayttaja, tuotteet) "
            "VALUES ('aino', ['keitin'])",
            consistency_level=getattr(ConsistencyLevel, taso),
            retry_policy=FallthroughRetryPolicy())   # ei uusintoja
        try:
            s.execute(lause)
            print(f"{taso}: onnistui")
        except Unavailable as virhe:
            print(f"{taso}: Unavailable, tarvitaan {virhe.required_replicas}"
                  f", elossa {virhe.alive_replicas}")
    # @loppu tasot


if __name__ == "__main__":
    aja(ajo)
