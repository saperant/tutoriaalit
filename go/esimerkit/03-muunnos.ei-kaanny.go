package main

import (
	"fmt"
	"time"
)

func main() {
	yritykset := 3
	viive := 250 * time.Millisecond
	fmt.Println(viive * yritykset) // @virhe: int ja Duration sekaisin
	fmt.Println(viive * time.Duration(yritykset))
}
