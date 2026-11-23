package main

import "fmt"

func main() {
	tulokset := make(chan int)
	tulokset <- 1 // kukaan ei vastaanota: pääohjelma jää odottamaan
	fmt.Println(<-tulokset)
}
