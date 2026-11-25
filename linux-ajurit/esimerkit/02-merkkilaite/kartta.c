// SPDX-License-Identifier: GPL-2.0
// Merkkilaite, jonka yhden sivun puskurin voi kuvata käyttäjän
// osoiteavaruuteen mmap-kutsulla. Sama sivu luetaan myös read-kutsulla.

#define pr_fmt(fmt) KBUILD_MODNAME ": " fmt

#include <linux/fs.h>
#include <linux/gfp.h>
#include <linux/miscdevice.h>
#include <linux/mm.h>
#include <linux/module.h>

static void *sivu;  // yksi nollattu sivu, yhteinen kaikille avaajille

// @alku mmap
static int kartta_mmap(struct file *tiedosto, struct vm_area_struct *vma)
{
    unsigned long koko = vma->vm_end - vma->vm_start;

    // Kuvattavaa on yksi sivu tiedoston alusta.
    if (vma->vm_pgoff != 0 || koko > PAGE_SIZE)
        return -EINVAL;
    // vm_insert_page lisää sivun prosessin sivutauluun ja ottaa siihen
    // viittauksen, joka vapautuu, kun kuvaus puretaan.
    return vm_insert_page(vma, vma->vm_start, virt_to_page(sivu));
}
// @loppu mmap

static ssize_t kartta_read(struct file *tiedosto, char __user *puskuri,
                           size_t pituus, loff_t *kohta)
{
    return simple_read_from_buffer(puskuri, pituus, kohta, sivu,
                                   PAGE_SIZE);
}

// @alku fops
static const struct file_operations kartta_fops = {
    .owner = THIS_MODULE,
    .read = kartta_read,
    .mmap = kartta_mmap,
    .llseek = default_llseek,
};

static struct miscdevice kartta_laite = {
    .minor = MISC_DYNAMIC_MINOR,
    .name = "kartta",
    .fops = &kartta_fops,
    .mode = 0600,
};
// @loppu fops

static int __init kartta_alku(void)
{
    int virhe;

    sivu = (void *)get_zeroed_page(GFP_KERNEL);
    if (!sivu)
        return -ENOMEM;
    virhe = misc_register(&kartta_laite);
    if (virhe)
        free_page((unsigned long)sivu);
    return virhe;
}

static void __exit kartta_loppu(void)
{
    misc_deregister(&kartta_laite);
    free_page((unsigned long)sivu);
}

module_init(kartta_alku);
module_exit(kartta_loppu);

MODULE_LICENSE("GPL");
MODULE_DESCRIPTION("mmap-esimerkki: yksi sivu kayttajan osoiteavaruuteen");
