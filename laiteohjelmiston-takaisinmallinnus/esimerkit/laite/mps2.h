/* Cortex-M3 ja QEMU:n mps2-an385-kortti: laitteen tarvitsemat
 * rekisterit. Sama kortti kuin taidossa Mikrokontrollerit. */
#ifndef MPS2_H
#define MPS2_H

#include <stddef.h>
#include <stdint.h>

#define KELLO_HZ 25000000u

/* CMSDK APB UART (ARM DDI 0479). */
typedef struct {
    volatile uint32_t DATA;      /* 0x00 lähetettävä / vastaanotettu */
    volatile uint32_t STATE;     /* 0x04 puskurien tila */
    volatile uint32_t CTRL;      /* 0x08 käyttöönotto, keskeytykset */
    volatile uint32_t INTSTATUS; /* 0x0C luku: tila, kirjoitus: kuittaus */
    volatile uint32_t BAUDDIV;   /* 0x10 kellon jakaja */
} uart_t;

_Static_assert(offsetof(uart_t, BAUDDIV) == 0x10, "UART-kartta");

#define UART0 ((uart_t *)0x40004000u)

#define UART_STATE_TXFULL (1u << 0)
#define UART_STATE_RXFULL (1u << 1)
#define UART_CTRL_TXEN    (1u << 0)
#define UART_CTRL_RXEN    (1u << 1)

/* FPGA:n I/O-lohko: käyttäjän LEDit. */
#define FPGAIO_LED (*(volatile uint32_t *)0x40028000u)

/* System Control Block: vektoritaulun osoite. */
#define SCB_VTOR (*(volatile uint32_t *)0xE000ED08u)

#endif
