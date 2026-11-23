use std::future::Future;
use std::pin::{pin, Pin};
use std::sync::Arc;
use std::task::{Context, Poll, Wake, Waker};
use std::thread::{self, Thread};

// @alku tulevaisuus
/// Future, joka palauttaa Pending annetun määrän kertoja. Oikeassa
/// ajoympäristössä Pending tarkoittaa "odotan I/O:ta"; herättäjä
/// (Waker) kertoo suorittajalle, milloin kannattaa kysyä uudelleen.
struct Vuoro {
    jaljella: u32,
}

impl Future for Vuoro {
    type Output = ();
    fn poll(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<()> {
        if self.jaljella == 0 {
            return Poll::Ready(());
        }
        self.jaljella -= 1;
        cx.waker().wake_by_ref(); // valmis jatkamaan heti
        Poll::Pending
    }
}

/// async fn käännetään tilakoneeksi, joka toteuttaa Futuren. Mitään
/// ei tapahdu ennen kuin joku kutsuu poll-metodia.
async fn lataa(nimi: &str, vaiheita: u32) -> String {
    Vuoro { jaljella: vaiheita }.await;
    format!("{nimi} valmis")
}
// @loppu tulevaisuus

// @alku suorittaja
/// Minimaalinen suorittaja: pollaa futurea, ja jos se ei ole valmis,
/// nukkuu kunnes herättäjä herättää säikeen. Tokio ja async-std
/// tekevät saman tehokkaasti tuhansille tehtäville ja I/O-tapahtumille.
struct SaikeenHerattaja(Thread);

impl Wake for SaikeenHerattaja {
    fn wake(self: Arc<Self>) {
        self.0.unpark();
    }
}

fn suorita<F: Future>(future: F) -> (F::Output, u32) {
    let mut future = pin!(future);
    let waker = Waker::from(Arc::new(SaikeenHerattaja(thread::current())));
    let mut cx = Context::from_waker(&waker);
    let mut kierrokset = 1;
    loop {
        match future.as_mut().poll(&mut cx) {
            Poll::Ready(arvo) => return (arvo, kierrokset),
            Poll::Pending => {
                thread::park();
                kierrokset += 1;
            }
        }
    }
}
// @loppu suorittaja

fn main() {
    // @alku kaytto
    let tehtava = async {
        let a = lataa("kuvat", 2).await;
        let b = lataa("tekstit", 3).await;
        format!("{a}, {b}")
    };
    let (tulos, kierrokset) = suorita(tehtava);
    println!("{tulos} ({kierrokset} pollausta)");
    // @loppu kaytto
}
