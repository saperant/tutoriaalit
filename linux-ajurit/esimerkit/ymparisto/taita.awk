# Taittaa yli 78 merkin rivit välilyönnin kohdalta PDF:n leveyteen.
# Jatkorivit sisennetään neljällä välilyönnillä enemmän kuin alkurivi.
{
    sub(/ +$/, "")
    rivi = $0
    match(rivi, /^ */)
    sisennys = substr(rivi, 1, RLENGTH) "    "
    while (length(rivi) > 78) {
        katko = 0
        for (i = 78; i > length(sisennys); i--)
            if (substr(rivi, i, 1) == " ") { katko = i; break }
        if (katko == 0) katko = 78
        print substr(rivi, 1, katko - 1)
        rivi = sisennys substr(rivi, katko + 1)
    }
    print rivi
}
