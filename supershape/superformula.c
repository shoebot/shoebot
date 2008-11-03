#include <Python.h>
#include <math.h>
//#include <stdio.h>

void _eval(double m,double n1,double n2,double n3,double phi,double *x,double *y)
{
    double r;
    double t1,t2;
    double a=1,b=1;

    t1 = cos(m * phi / 4.0) / a;
    t1 = fabs(t1);
    t1 = pow(t1,n2);

    t2 = sin(m * phi / 4.0) / b;
    t2 = fabs(t2);
    t2 = pow(t2,n3);

    r = pow(t1+t2,1.0/n1);
    if (fabs(r) == 0) {
        *x = 0;
        *y = 0;
    } else {
        r = 1.0 / r;
        *x = r * cos(phi);
        *y = r * sin(phi);
    }
}

static PyObject *
cSuperformula_supercalc(PyObject *self, PyObject *args)
{
    double m, n1, n2, n3, phi;
    double x, y;    
    
    if (!PyArg_ParseTuple(args, "ddddd", &m, &n1, &n2, &n3, &phi))
        return NULL;
        
    _eval(m, n1, n2, n3, phi, &x, &y);
    return Py_BuildValue("dd", x, y);
}

static PyObject *SuperformulaError;

static PyMethodDef SuperformulaMethods[] = {
    {"supercalc",  cSuperformula_supercalc, METH_VARARGS,
    "Supercalc."},
    {NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initcSuperformula(void)
{
    PyObject *m;
    
    m = Py_InitModule("cSuperformula", SuperformulaMethods);
    
    SuperformulaError = PyErr_NewException("cSuperformula.error", NULL, NULL);
    Py_INCREF(SuperformulaError);
    PyModule_AddObject(m, "error", SuperformulaError);
}

int
main(int argc, char *argv[])
{
    /* Pass argv[0] to the Python interpreter */
    Py_SetProgramName(argv[0]);

    /* Initialize the Python interpreter.  Required. */
    Py_Initialize();

    /* Add a static module */
    initcSuperformula();
    
    return 0;
}