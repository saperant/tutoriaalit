// Asettaa I2C-laitteen rekisterin käyttäjätilasta laitteen /dev/i2c-N
// kautta. Testeissä sillä kirjoitetaan i2c-stub-laitteen rekistereihin
// arvot, jotka oikea piiri tuottaisi itse.
//
// Käyttö: i2c-aseta /dev/i2c-0 osoite rekisteri arvo
// Kaikki luvut voi antaa myös 0x-muodossa. Arvo on 16-bittinen.
#include <errno.h>
#include <fcntl.h>
#include <linux/i2c-dev.h>
#include <linux/i2c.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

// @alku smbus
static int kirjoita_sana(int fd, unsigned char rekisteri,
                         unsigned short arvo)
{
    union i2c_smbus_data data = {.word = arvo};
    struct i2c_smbus_ioctl_data pyynto = {
        .read_write = I2C_SMBUS_WRITE,
        .command = rekisteri,
        .size = I2C_SMBUS_WORD_DATA,
        .data = &data,
    };
    return ioctl(fd, I2C_SMBUS, &pyynto);
}
// @loppu smbus

int main(int argc, char **argv)
{
    if (argc != 5) {
        fprintf(stderr, "käyttö: %s laite osoite rekisteri arvo\n",
                argv[0]);
        return 2;
    }
    int fd = open(argv[1], O_RDWR);
    long osoite = strtol(argv[2], NULL, 0);
    long rekisteri = strtol(argv[3], NULL, 0);
    long arvo = strtol(argv[4], NULL, 0);
    // I2C_SLAVE_FORCE ohittaa tarkistuksen, onko osoitteella jo ajuri.
    if (fd < 0 || ioctl(fd, I2C_SLAVE_FORCE, osoite) != 0 ||
        kirjoita_sana(fd, (unsigned char)rekisteri,
                      (unsigned short)arvo) != 0) {
        printf("i2c-aseta: %s\n", strerror(errno));
        return 1;
    }
    close(fd);
    return 0;
}
