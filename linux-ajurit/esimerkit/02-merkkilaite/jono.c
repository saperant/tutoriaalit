// Viestijono merkkilaitteena: /dev/jonoN on tavujono, johon yksi
// prosessi kirjoittaa ja toinen lukee. Lukija odottaa, kunnes jonossa on
// dataa, ja kirjoittaja, kunnes jonossa on tilaa. Tukee poll()-kutsua,
// ei-estävää tilaa ja kahta ioctl-komentoa.
#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/cdev.h>
#include <linux/device.h>
#include <linux/fs.h>
#include <linux/kfifo.h>
#include <linux/module.h>
#include <linux/mutex.h>
#include <linux/poll.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/wait.h>

#include "jono.h"

static unsigned int maara = 2;
module_param(maara, uint, 0444);
MODULE_PARM_DESC(maara, "laitteiden määrä (1-8)");
static unsigned int koko = 64;
module_param(koko, uint, 0444);
MODULE_PARM_DESC(koko, "jonon koko tavuina, kahden potenssi");

// @alku rakenne
struct jono {
    struct cdev cdev;
    struct mutex lukko;           // suojaa fifoa
    DECLARE_KFIFO_PTR(fifo, u8);
    wait_queue_head_t lukijat;    // odottavat dataa
    wait_queue_head_t kirjoittajat; // odottavat tilaa
};

static dev_t ensimmainen;         // ensimmäinen laitenumero (major, minor)
static struct class *luokka;
static struct jono *jonot;
// @loppu rakenne

// @alku avaa
static int jono_avaa(struct inode *inode, struct file *tiedosto)
{
    // inode->i_cdev osoittaa rakenteen jäseneen; container_of palauttaa
    // koko rakenteen. Tallennetaan se tiedoston yksityiseksi dataksi.
    tiedosto->private_data = container_of(inode->i_cdev, struct jono,
                                          cdev);
    return 0;
}
// @loppu avaa

// @alku lue
static ssize_t jono_lue(struct file *tiedosto, char __user *puskuri,
                        size_t pituus, loff_t *sijainti)
{
    struct jono *j = tiedosto->private_data;
    unsigned int kopioitu;
    int virhe;

    for (;;) {
        if (mutex_lock_interruptible(&j->lukko))
            return -ERESTARTSYS;
        if (!kfifo_is_empty(&j->fifo))
            break;
        mutex_unlock(&j->lukko);
        if (tiedosto->f_flags & O_NONBLOCK)
            return -EAGAIN;
        // Nukutaan lukon ulkopuolella, kunnes jonossa on dataa tai
        // prosessi saa signaalin.
        if (wait_event_interruptible(j->lukijat,
                                     !kfifo_is_empty(&j->fifo)))
            return -ERESTARTSYS;
    }
    virhe = kfifo_to_user(&j->fifo, puskuri, pituus, &kopioitu);
    mutex_unlock(&j->lukko);
    if (virhe)
        return virhe;  // -EFAULT: puskuri ei ole käyttäjän muistia
    wake_up_interruptible(&j->kirjoittajat);
    return kopioitu;
}
// @loppu lue

static ssize_t jono_kirjoita(struct file *tiedosto,
                             const char __user *puskuri, size_t pituus,
                             loff_t *sijainti)
{
    struct jono *j = tiedosto->private_data;
    unsigned int kopioitu;
    int virhe;

    for (;;) {
        if (mutex_lock_interruptible(&j->lukko))
            return -ERESTARTSYS;
        if (!kfifo_is_full(&j->fifo))
            break;
        mutex_unlock(&j->lukko);
        if (tiedosto->f_flags & O_NONBLOCK)
            return -EAGAIN;
        if (wait_event_interruptible(j->kirjoittajat,
                                     !kfifo_is_full(&j->fifo)))
            return -ERESTARTSYS;
    }
    virhe = kfifo_from_user(&j->fifo, puskuri, pituus, &kopioitu);
    mutex_unlock(&j->lukko);
    if (virhe)
        return virhe;
    wake_up_interruptible(&j->lukijat);
    return kopioitu;
}

// @alku poll
static __poll_t jono_poll(struct file *tiedosto, poll_table *taulu)
{
    struct jono *j = tiedosto->private_data;
    __poll_t maski = 0;

    // poll_wait ei nuku: se rekisteröi jonot, joiden herätys saa ytimen
    // kysymään tilaa uudelleen.
    poll_wait(tiedosto, &j->lukijat, taulu);
    poll_wait(tiedosto, &j->kirjoittajat, taulu);
    mutex_lock(&j->lukko);
    if (!kfifo_is_empty(&j->fifo))
        maski |= EPOLLIN | EPOLLRDNORM;
    if (!kfifo_is_full(&j->fifo))
        maski |= EPOLLOUT | EPOLLWRNORM;
    mutex_unlock(&j->lukko);
    return maski;
}
// @loppu poll

// @alku ioctl
static long jono_ioctl(struct file *tiedosto, unsigned int komento,
                       unsigned long argumentti)
{
    struct jono *j = tiedosto->private_data;
    struct jono_tila tila;

    switch (komento) {
    case JONO_TILA:
        mutex_lock(&j->lukko);
        tila.koko = kfifo_size(&j->fifo);
        tila.kaytetty = kfifo_len(&j->fifo);
        mutex_unlock(&j->lukko);
        if (copy_to_user((void __user *)argumentti, &tila,
                         sizeof(tila)))
            return -EFAULT;
        return 0;
    case JONO_TYHJENNA:
        mutex_lock(&j->lukko);
        kfifo_reset(&j->fifo);
        mutex_unlock(&j->lukko);
        wake_up_interruptible(&j->kirjoittajat);
        return 0;
    default:
        return -ENOTTY;  // tuntematon komento
    }
}
// @loppu ioctl

// @alku fops
static const struct file_operations jono_fops = {
    .owner = THIS_MODULE,  // moduulia ei voi poistaa, kun laite on auki
    .open = jono_avaa,
    .read = jono_lue,
    .write = jono_kirjoita,
    .poll = jono_poll,
    .unlocked_ioctl = jono_ioctl,
    .llseek = no_llseek,
};
// @loppu fops

static void jono_siivoa(unsigned int luotu)
{
    while (luotu-- > 0) {
        device_destroy(luokka, MKDEV(MAJOR(ensimmainen), luotu));
        cdev_del(&jonot[luotu].cdev);
        kfifo_free(&jonot[luotu].fifo);
    }
}

// @alku alku
static int __init jono_alku(void)
{
    unsigned int i;
    int virhe;

    if (maara < 1 || maara > 8 || !is_power_of_2(koko))
        return -EINVAL;
    // 1. Laitenumerot: ydin valitsee vapaan pääluvun (major).
    virhe = alloc_chrdev_region(&ensimmainen, 0, maara, "jono");
    if (virhe)
        return virhe;
    // 2. Laiteluokka: /sys/class/jono, josta devtmpfs ja udev luovat
    //    laitetiedostot.
    luokka = class_create("jono");
    if (IS_ERR(luokka)) {
        virhe = PTR_ERR(luokka);
        goto vapauta_numerot;
    }
    jonot = kcalloc(maara, sizeof(*jonot), GFP_KERNEL);
    if (!jonot) {
        virhe = -ENOMEM;
        goto tuhoa_luokka;
    }
    for (i = 0; i < maara; i++) {
        struct jono *j = &jonot[i];
        struct device *laite;

        mutex_init(&j->lukko);
        init_waitqueue_head(&j->lukijat);
        init_waitqueue_head(&j->kirjoittajat);
        virhe = kfifo_alloc(&j->fifo, koko, GFP_KERNEL);
        if (virhe)
            goto siivoa;
        // 3. cdev yhdistää laitenumeron file_operations-tauluun.
        cdev_init(&j->cdev, &jono_fops);
        virhe = cdev_add(&j->cdev, MKDEV(MAJOR(ensimmainen), i), 1);
        if (virhe) {
            kfifo_free(&j->fifo);
            goto siivoa;
        }
        // 4. Laite näkyy sysfsissä ja tiedostona /dev/jonoN.
        laite = device_create(luokka, NULL,
                              MKDEV(MAJOR(ensimmainen), i), NULL,
                              "jono%u", i);
        if (IS_ERR(laite)) {
            virhe = PTR_ERR(laite);
            cdev_del(&j->cdev);
            kfifo_free(&j->fifo);
            goto siivoa;
        }
    }
    pr_info("%u laitetta, %u tavua kukin\n", maara, koko);
    return 0;

siivoa:
    jono_siivoa(i);
    kfree(jonot);
tuhoa_luokka:
    class_destroy(luokka);
vapauta_numerot:
    unregister_chrdev_region(ensimmainen, maara);
    return virhe;
}
// @loppu alku

static void __exit jono_loppu(void)
{
    jono_siivoa(maara);
    kfree(jonot);
    class_destroy(luokka);
    unregister_chrdev_region(ensimmainen, maara);
    pr_info("poistettu\n");
}

module_init(jono_alku);
module_exit(jono_loppu);
MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("Viestijono merkkilaitteena");
