/* Laajennusmoduuli suoraan Pythonin C-rajapinnalla: viitelaskenta ja
   virheet näkyvät sellaisinaan. pybind11 ja nanobind tekevät tämän
   kaiken käyttäjän puolesta. */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* @alku summa */
static PyObject *summa(PyObject *self, PyObject *arvot)
{
    (void)self;
    PyObject *iteraattori = PyObject_GetIter(arvot);    /* uusi viite */
    if (iteraattori == NULL)
        return NULL;                                     /* TypeError */
    double s = 0.0;
    PyObject *alkio;
    while ((alkio = PyIter_Next(iteraattori)) != NULL) { /* uusi viite */
        double x = PyFloat_AsDouble(alkio);
        Py_DECREF(alkio);
        if (x == -1.0 && PyErr_Occurred()) {
            Py_DECREF(iteraattori);
            return NULL;                       /* virhe jo asetettu */
        }
        s += x;
    }
    Py_DECREF(iteraattori);
    if (PyErr_Occurred())                      /* iteraattorin virhe */
        return NULL;
    return PyFloat_FromDouble(s);              /* uusi viite kutsujalle */
}
/* @loppu summa */

/* @alku ensimmainen */
static PyObject *ensimmainen(PyObject *self, PyObject *lista)
{
    (void)self;
    if (!PyList_Check(lista)) {
        PyErr_SetString(PyExc_TypeError, "odotettiin lista");
        return NULL;
    }
    if (PyList_GET_SIZE(lista) == 0) {
        PyErr_SetString(PyExc_IndexError, "tyhjä lista");
        return NULL;
    }
    PyObject *eka = PyList_GET_ITEM(lista, 0);   /* lainattu viite */
    return Py_NewRef(eka);       /* palautettava arvo on oltava oma */
}
/* @loppu ensimmainen */

/* @alku moduuli */
static PyMethodDef funktiot[] = {
    {"summa", summa, METH_O, "Lukujen summa iteroitavasta."},
    {"ensimmainen", ensimmainen, METH_O, "Listan ensimmäinen alkio."},
    {NULL, NULL, 0, NULL},
};

static struct PyModuleDef moduuli = {
    PyModuleDef_HEAD_INIT, "raaka", "Esimerkki C-rajapinnasta.", -1,
    funktiot, NULL, NULL, NULL, NULL,
};

PyMODINIT_FUNC PyInit_raaka(void)
{
    return PyModule_Create(&moduuli);
}
/* @loppu moduuli */
