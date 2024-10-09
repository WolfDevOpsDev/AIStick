import torch

cuda_available = torch.cuda.is_available()
cuda_version = torch.version.cuda
pytorch_version = torch.__version__

print(cuda_available, cuda_version, pytorch_version)
