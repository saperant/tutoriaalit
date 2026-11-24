"""Laajennusmoduulin käännös; muut tiedot ovat pyproject.toml:ssa."""

# @alku setup
from pybind11.setup_helpers import Pybind11Extension
from setuptools import setup

setup(
    ext_modules=[
        Pybind11Extension(
            "nopeatarkiste._ydin",
            ["src/ydin.cpp"],
            cxx_std=20,
        ),
    ],
)
# @loppu setup
