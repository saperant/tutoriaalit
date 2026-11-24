// Emuloitu verkkokortti vai virtio? Sama 100 paketin lähetys kolmella
// tavalla. Jokainen vieraan I/O-rekisterin käyttö tai ilmoitus
// laitteelle on VM exit, joka maksaa mikrosekunteja.
//
// Virtio-jono (split virtqueue) on toteutettu virtio 1.x -määrittelyn
// rakenteilla: kuvaajataulu, saatavilla-rengas ja käytetty-rengas
// sijaitsevat vieraan muistissa, jonka laite (hypervisor) näkee.
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum { PAKETTEJA = 100, KOKO = 64, JONO = 32 };

static unsigned long exitit;
static uint32_t laite_summa;    // laitteen lähettämien tavujen summa

// @alku emuloitu
// Vanhan mallin verkkokortti: tavu kerrallaan datarekisteriin, sitten
// lähetyskomento ja tilarekisterin luku. Jokainen on VM exit.
static void emuloitu_outb(uint16_t portti, uint8_t arvo)
{
    exitit++;
    if (portti == 0x300)
        laite_summa += arvo;
}

static void laheta_emuloitu(const uint8_t *paketti)
{
    for (int i = 0; i < KOKO; i++)
        emuloitu_outb(0x300, paketti[i]);   // datarekisteri
    emuloitu_outb(0x301, 1);                // komento: lähetä
    exitit++;                               // inb: valmis?
}
// @loppu emuloitu

// @alku rakenteet
struct vring_desc {            // yksi puskuri vieraan muistissa
    uint64_t addr;
    uint32_t len;
    uint16_t flags;
    uint16_t next;
};

struct vring_avail {           // ajuri -> laite
    uint16_t flags;
    uint16_t idx;              // kasvaa aina, kiertää 16 bitissä
    uint16_t ring[JONO];
};

struct vring_used_elem {
    uint32_t id;
    uint32_t len;
};

struct vring_used {            // laite -> ajuri
    uint16_t flags;
    uint16_t idx;
    struct vring_used_elem ring[JONO];
};

enum { VRING_USED_F_NO_NOTIFY = 1 };
// @loppu rakenteet

static struct vring_desc desc[JONO];
static struct vring_avail avail;
static struct vring_used used;
static uint8_t puskurit[JONO][KOKO];
static uint16_t laite_viimeisin;    // laitteen seuraava avail-paikka
static uint16_t ajuri_viimeisin;    // ajurin seuraava used-paikka
static uint16_t vapaita = JONO;

// @alku laite
// Laite (hypervisor) käsittelee kaikki saatavilla olevat puskurit yhdellä
// kertaa ja palauttaa ne käytetty-renkaaseen.
static void laite_kasittele(void)
{
    while (laite_viimeisin != avail.idx) {
        uint16_t id = avail.ring[laite_viimeisin % JONO];
        const uint8_t *data = puskurit[desc[id].addr];
        for (uint32_t i = 0; i < desc[id].len; i++)
            laite_summa += data[i];
        used.ring[used.idx % JONO] = (struct vring_used_elem){id, 0};
        used.idx++;
        laite_viimeisin++;
    }
}

static void ilmoita(void)          // ajurin "kick": yksi VM exit
{
    exitit++;
    laite_kasittele();
}
// @loppu laite

// @alku ajuri
static void kerays(void)           // ajuri vapauttaa käytetyt puskurit
{
    while (ajuri_viimeisin != used.idx) {
        ajuri_viimeisin++;
        vapaita++;
    }
}

// Lisää paketin jonoon. Ilmoitus annetaan vain, kun erä on täynnä tai
// paketit loppuvat, eikä silloinkaan, jos laite on pyytänyt olemaan
// ilmoittamatta (se käsittelee jonoa jo).
static void laheta_virtio(const uint8_t *paketti, int era, int viimeinen)
{
    if (vapaita == 0)
        kerays();
    uint16_t id = avail.idx % JONO;
    memcpy(puskurit[id], paketti, KOKO);
    desc[id] = (struct vring_desc){.addr = id, .len = KOKO};
    avail.ring[avail.idx % JONO] = id;
    avail.idx++;                 // oikeassa ajurissa ennen tätä muistiaita
    vapaita--;
    int odottavia = (uint16_t)(avail.idx - laite_viimeisin);
    if ((odottavia >= era || viimeinen) &&
        !(used.flags & VRING_USED_F_NO_NOTIFY))
        ilmoita();
}
// @loppu ajuri

static void nollaa(void)
{
    exitit = 0;
    laite_summa = 0;
    memset(&avail, 0, sizeof avail);
    memset(&used, 0, sizeof used);
    laite_viimeisin = ajuri_viimeisin = 0;
    vapaita = JONO;
}

int main(void)
{
    uint8_t paketti[KOKO];
    uint32_t odotettu = 0;
    for (int i = 0; i < KOKO; i++) {
        paketti[i] = (uint8_t)(i * 7);
        odotettu += paketti[i];
    }
    odotettu *= PAKETTEJA;

    nollaa();
    for (int p = 0; p < PAKETTEJA; p++)
        laheta_emuloitu(paketti);
    printf("emuloitu laite:      %5lu VM exitiä, summa %s\n", exitit,
           laite_summa == odotettu ? "oikein" : "VÄÄRIN");

    const int erat[] = {1, JONO};
    for (int e = 0; e < 2; e++) {
        nollaa();
        for (int p = 0; p < PAKETTEJA; p++)
            laheta_virtio(paketti, erat[e], p == PAKETTEJA - 1);
        printf("virtio, erä %2d:      %5lu VM exitiä, summa %s\n",
               erat[e], exitit,
               laite_summa == odotettu ? "oikein" : "VÄÄRIN");
    }
    return 0;
}
