from ipykernel.kernelapp import IPKernelApp
from . import KotlinKernel

IPKernelApp.launch_instance(kernel_class=KotlinKernel)
