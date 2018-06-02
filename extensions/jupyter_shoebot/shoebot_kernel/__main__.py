from ipykernel.kernelapp import IPKernelApp
from .kernel import ShoebotKernel
IPKernelApp.launch_instance(kernel_class=ShoebotKernel)
