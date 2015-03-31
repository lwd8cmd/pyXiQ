#include <stdio.h>
#include <m3api/xiApi.h>
#include <memory.h>
#include <Python.h>

typedef struct {
	PyObject_HEAD
	XI_IMG image;
	HANDLE xiH;
} Camera;

static int Camera_init(Camera *self, PyObject *args, PyObject *kwargs) {
	// ignore debuf messages
	xiSetParamInt(0, XI_PRM_DEBUG_LEVEL, XI_DL_FATAL);

	// image buffer
	memset(&self->image,0,sizeof(self->image));
	self->image.size = sizeof(XI_IMG);

	// Sample for XIMEA API V2.10
	self->xiH = NULL;

	// Get number of camera devices
	DWORD dwNumberOfDevices = 0;
	xiGetNumberDevices(&dwNumberOfDevices);
	
	if (!dwNumberOfDevices) {
		PyErr_SetString(PyExc_ValueError, "Camera not found");
		return 0;
	}

        xiOpenDevice(0, &self->xiH);
	xiSetParamInt(self->xiH, XI_PRM_IMAGE_DATA_FORMAT, XI_RGB24);
	xiSetParamInt(self->xiH, XI_PRM_FRAMERATE, 5);
	xiSetParamInt(self->xiH, XI_PRM_BUFFERS_QUEUE_SIZE, 1);
	xiSetParamInt(self->xiH, XI_PRM_RECENT_FRAME, 1);

	return 0;
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
	xiStartAcquisition(self->xiH);
	Py_RETURN_NONE;
}

static PyObject *Camera_stop(Camera *self) {
	xiStopAcquisition(self->xiH);
	Py_RETURN_NONE;
}

static PyObject *Camera_image(Camera *self) {
	xiGetImage(self->xiH, 5000, &self->image);
	unsigned char* frame = (unsigned char*)self->image.bp;
	return Py_BuildValue("s", frame);
}

static PyObject *Camera_setParamInt(Camera *self, PyObject *args) {
	char *param;
	int val;

	if (!PyArg_ParseTuple(args, "si", &param, &val)) {
		return NULL;
	}	
	
	xiSetParamInt(self->xiH, param, val);
	
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
	char *param;
	char *val;
	int size;

	if (!PyArg_ParseTuple(args, "ssi", &param, &val, &size)) {
		return NULL;
	}	
	
	xiSetParamString(self->xiH, param, val, size);
	
	Py_RETURN_NONE;
}

static PyObject *Camera_getParamInt(Camera *self, PyObject *args) {
	char *param;
	int val = 0;

	if (!PyArg_ParseTuple(args, "s", &param)) {
		return NULL;
	}	
	
	xiGetParamInt(self->xiH, param, &val);
	return Py_BuildValue("i", val);
}

static PyObject *Camera_getParamFloat(Camera *self, PyObject *args) {
	char *param;
	float val = 0;

	if (!PyArg_ParseTuple(args, "s", &param)) {
		return NULL;
	}	
	
	xiGetParamFloat(self->xiH, param, &val);
	return Py_BuildValue("f", val);
}

static PyObject *Camera_getParamString(Camera *self, PyObject *args) {
	char *param;
	char *val = 0;
	int size;

	if (!PyArg_ParseTuple(args, "si", &param, &size)) {
		return NULL;
	}	
	
	xiGetParamString(self->xiH, param, &val, size);
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
}
