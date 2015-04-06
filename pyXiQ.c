#include <stdio.h>
#include <m3api/xiApi.h>
#include <memory.h>
#include <Python.h>
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include "numpy/arrayobject.h"

typedef struct {
	PyObject_HEAD
	XI_IMG image;
	HANDLE xiH;
	unsigned char lookup_table[0x1000000];
} Camera;

static int Camera_init(Camera *self, PyObject *args, PyObject *kwargs) {
	self->xiH = NULL;

	// ignore debug messages
	xiSetParamInt(0, XI_PRM_DEBUG_LEVEL, XI_DL_FATAL);

	// image buffer
	memset(&self->image, 0, sizeof(self->image));
	self->image.size = sizeof(XI_IMG);

	// Get number of camera devices
	DWORD dwNumberOfDevices = 0;
	xiGetNumberDevices(&dwNumberOfDevices);
	
	if (!dwNumberOfDevices) {
		PyErr_SetString(PyExc_ValueError, "Camera not found");
		return 0;
	}

        xiOpenDevice(0, &self->xiH);
	xiSetParamInt(self->xiH, XI_PRM_IMAGE_DATA_FORMAT, XI_RGB24);
	xiSetParamInt(self->xiH, XI_PRM_BUFFERS_QUEUE_SIZE, 1);
	xiSetParamInt(self->xiH, XI_PRM_RECENT_FRAME, 1);

	return 0;
}

static PyObject *Camera_opened(Camera *self) {
	return Py_BuildValue("b", !(self->xiH == NULL));
}

static PyObject *Camera_set_table(Camera *self, PyObject *args) {
	PyObject *arg1=NULL;
	PyArrayObject *lookup=NULL;

	if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &arg1)) return NULL;
	lookup = (PyArrayObject*)PyArray_FROM_OTF(arg1, NPY_UINT8, NPY_ARRAY_IN_ARRAY);
	if (lookup == NULL) {
		Py_XDECREF(lookup);
		return NULL;
	}

	//long i;
	//for (i = PyArray_DIM(lookup, 0); i >= 0; i--) {
	//	unsigned char *v = (unsigned char*)PyArray_GETPTR1(lookup, i);
	//	self->lookup_table[i] = *v;
	//}
	
	memcpy(self->lookup_table, (unsigned char*)PyArray_DATA(lookup), 0x1000000);
	Py_DECREF(lookup);
	Py_RETURN_NONE;
}

static void Camera_dealloc(Camera *self) {
	if (self->xiH) {
		xiCloseDevice(self->xiH);
	}
}

static PyObject *Camera_close(Camera *self) {
	if (self->xiH) {
		xiCloseDevice(self->xiH);
	}
	Py_RETURN_NONE;
}

static PyObject *Camera_start(Camera *self) {
	if (self->xiH) {
		xiStartAcquisition(self->xiH);
	}
	Py_RETURN_NONE;
}

static PyObject *Camera_stop(Camera *self) {
	if (self->xiH) {
		xiStopAcquisition(self->xiH);
	}
	Py_RETURN_NONE;
}

static PyObject *Camera_image(Camera *self) {
	if (self->xiH) {
		xiGetImage(self->xiH, 5000, &self->image);
		unsigned char* frame = (unsigned char*)self->image.bp;
		int w = (int)self->image.width;
		int h = (int)self->image.height;
		npy_intp dims[3] = {h, w, 3};
		PyArrayObject *outArray = (PyArrayObject *) PyArray_SimpleNewFromData(3, dims, NPY_UINT8, frame);
		return PyArray_Return(outArray); 
	} else {
		return Py_BuildValue("s", "");
	}
}

static PyObject *Camera_segment(Camera *self, PyObject *args) {
	if (!self->xiH) return NULL;

	PyObject *out1=NULL;
	PyArrayObject *segmented=NULL;
	if (!PyArg_ParseTuple(args, "O!", &PyArray_Type, &out1)) return NULL;
	segmented = (PyArrayObject*)PyArray_FROM_OTF(out1, NPY_UINT8, NPY_ARRAY_INOUT_ARRAY);
	if (segmented == NULL) {
		PyArray_XDECREF_ERR(segmented);
		return NULL;
	}

	xiGetImage(self->xiH, 5000, &self->image);
	unsigned char* frame = (unsigned char*)self->image.bp;
	int w = (int)self->image.width;
	int h = (int)self->image.height;
	
	int i;
	int j;
	//h = 1;
	//printf("test2 %u \n", self->lookup_table[14206550]);
	for (i=0; i<h; i++) {
		for (j=0; j<w; j++) {
			unsigned char r = self->lookup_table[frame[i*w*3+j*3] + (frame[i*w*3+j*3+1] << 8) + (frame[i*w*3+j*3+2] << 16)];
			unsigned char *o = (unsigned char*)PyArray_GETPTR2(segmented, i, j);
			//printf("RGB %d %d %d, val %d, index %d \n", frame[i*w*3+j*3], frame[i*w*3+j*3+1], frame[i*w*3+j*3+2], r, frame[i*w*3+j*3] + (frame[i*w*3+j*3+1] << 8) + (frame[i*w*3+j*3+2] << 16));
			*o = r;
		}
	}
	//printf("test3 %u \n", self->lookup_table[14206550]);
	Py_DECREF(segmented);
	Py_INCREF(Py_None);
	return Py_None;
}


static PyObject *Camera_setParamInt(Camera *self, PyObject *args) {
	if (self->xiH) {
		char *param;
		int val;

		if (!PyArg_ParseTuple(args, "si", &param, &val)) {
			return NULL;
		}	
	
		xiSetParamInt(self->xiH, param, val);
	}
	
	Py_RETURN_NONE;
}

static PyObject *Camera_setParamFloat(Camera *self, PyObject *args) {
	char *param;
	float val;

	if (!PyArg_ParseTuple(args, "sf", &param, &val)) {
		return NULL;
	}	
	
	xiSetParamFloat(self->xiH, param, val);
	
	Py_RETURN_NONE;
}

static PyObject *Camera_setParamString(Camera *self, PyObject *args) {
	if (self->xiH) {
		char *param;
		char *val;
		int size;

		if (!PyArg_ParseTuple(args, "ssi", &param, &val, &size)) {
			return NULL;
		}	
	
		xiSetParamString(self->xiH, param, val, size);
	}
	Py_RETURN_NONE;
}

static PyObject *Camera_getParamInt(Camera *self, PyObject *args) {
	int val = 0;
	if (self->xiH) {
		char *param;

		if (!PyArg_ParseTuple(args, "s", &param)) {
			return NULL;
		}	
	
		xiGetParamInt(self->xiH, param, &val);
	}
	return Py_BuildValue("i", val);
}

static PyObject *Camera_getParamFloat(Camera *self, PyObject *args) {
	float val = 0;
	if (self->xiH) {
		char *param;

		if (!PyArg_ParseTuple(args, "s", &param)) {
			return NULL;
		}	
	
		xiGetParamFloat(self->xiH, param, &val);
	}
	return Py_BuildValue("f", val);
}

static PyObject *Camera_getParamString(Camera *self, PyObject *args) {
	char *val = 0;
	if (self->xiH) {
		char *param;
		int size;

		if (!PyArg_ParseTuple(args, "si", &param, &size)) {
			return NULL;
		}	
	
		xiGetParamString(self->xiH, param, &val, size);
	}
	return Py_BuildValue("s", val);
}

static PyMethodDef Camera_methods[] = {
	{"start", (PyCFunction)Camera_start, METH_NOARGS,
		"start()\n\n"
		"Starts the data acquisition on the camera."},
	{"stop", (PyCFunction)Camera_stop, METH_NOARGS,
		"stop()\n\n"
		"Stops data acquisition and deallocates internal image buffers."},
	{"close", (PyCFunction)Camera_close, METH_NOARGS,
		"close()\n\n"
		"This function will un-initialize the specified device, closes its handle and releases allocated resources."},
	{"opened", (PyCFunction)Camera_opened, METH_NOARGS,
		"opened()\n\n"
		"True if camera is opened."},
	{"image", (PyCFunction)Camera_image, METH_NOARGS,
		"image()\n\n"
		"Capture image."},
	{"setParamInt", (PyCFunction)Camera_setParamInt, METH_VARARGS,
		"setParamInt(param, value)\n\n"
		"Set camera parameters."},
	{"setParamFloat", (PyCFunction)Camera_setParamFloat, METH_VARARGS,
		"setParamInt(param, value)\n\n"
		"Set camera parameters."},
	{"setParamString", (PyCFunction)Camera_setParamString, METH_VARARGS,
		"setParamInt(param, value, size)\n\n"
		"Set camera parameters."},
	{"getParamInt", (PyCFunction)Camera_getParamInt, METH_VARARGS,
		"getParamInt(param)\n\n"
		"get camera parameters."},
	{"getParamFloat", (PyCFunction)Camera_getParamFloat, METH_VARARGS,
		"getParamInt(param)\n\n"
		"get camera parameters."},
	{"getParamString", (PyCFunction)Camera_getParamString, METH_VARARGS,
		"getParamInt(param, size)\n\n"
		"get camera parameters."},
	{"setTable", (PyCFunction)Camera_set_table, METH_VARARGS,
		"setTable(3D pyarr)\n\n"
		"Set color lookup table."},
	{"segment", (PyCFunction)Camera_segment, METH_VARARGS,
		"segment()\n\n"
		"Capture segmented image."},
	{NULL}
};

static PyTypeObject Camera_type = {
	PyObject_HEAD_INIT(NULL) 0,
	"pyXiQ.Camera", sizeof(Camera), 0,
	(destructor)Camera_dealloc, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
	0, Py_TPFLAGS_DEFAULT, "Camera()\n\nOpens the video device.", 0, 0, 0,
	0, 0, 0, Camera_methods, 0, 0, 0, 0, 0, 0, 0,
	(initproc)Camera_init
};

static PyMethodDef module_methods[] = {
	{NULL}
};

PyMODINIT_FUNC initpyXiQ(void) {
	Camera_type.tp_new = PyType_GenericNew;

	if (PyType_Ready(&Camera_type) < 0) {
		return;
	}

	PyObject *module;

	module = Py_InitModule3("pyXiQ", module_methods, "Computer vision: Robotex, Ximea cam");
	if(!module) {
		return;
	}

	Py_INCREF(&Camera_type);
	PyModule_AddObject(module, "Camera", (PyObject *)&Camera_type);
	import_array();
}
