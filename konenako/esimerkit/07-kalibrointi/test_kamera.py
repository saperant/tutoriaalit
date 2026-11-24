"""Synteettisen kameran testit: renderöijä vastaa projectPoints-mallia."""

import cv2
import numpy as np

from kamera import Kamera, Lauta, asennot, renderoi


# @alku testit
def test_vaaristyma_kumoutuu() -> None:
    """undistortPoints ja projectPoints ovat toistensa käänteiset."""
    kamera = Kamera()
    pikselit = np.array([[[10.0, 10.0]], [[630.0, 470.0]], [[320, 240]]])
    suunta = cv2.undistortPoints(
        pikselit, kamera.K(), kamera.vaaristyma(),
        criteria=(cv2.TERM_CRITERIA_COUNT + cv2.TERM_CRITERIA_EPS,
                  50, 1e-12))
    pisteet = np.hstack([suunta.reshape(-1, 2), np.ones((3, 1))])
    takaisin, _ = cv2.projectPoints(pisteet, np.zeros(3), np.zeros(3),
                                    kamera.K(), kamera.vaaristyma())
    assert np.abs(takaisin - pikselit).max() < 1e-6


def test_kulmat_osuvat_projektioon() -> None:
    """Kuvasta löydetyt kulmat ovat siellä, minne malli ne projisoi."""
    kamera, lauta = Kamera(), Lauta()
    rvec, tvec = asennot()[0]
    kuva = renderoi(kamera, lauta, rvec, tvec)
    loytyi, kulmat = cv2.findChessboardCorners(
        kuva, (lauta.sarakkeet, lauta.rivit))
    assert loytyi
    ehto = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 50, 1e-4)
    kulmat = cv2.cornerSubPix(kuva, kulmat, (7, 7), (-1, -1), ehto)
    odotetut, _ = cv2.projectPoints(lauta.kulmat(), rvec, tvec,
                                    kamera.K(), kamera.vaaristyma())
    ero = kulmat.reshape(-1, 2) - odotetut.reshape(-1, 2)
    assert np.abs(ero).max() < 0.25
# @loppu testit
