import torch
import torch.nn as nn
import torch.nn.functional as F

# Activation constants
ACT_RELU = "relu"
ACT_LEAKY_RELU = "leaky_relu"
ACT_ELU = "elu"
ACT_NONE = "none"

class DummyInPlaceABNFunction(torch.autograd.Function):
    @staticmethod
    def forward(ctx, x, weight, bias, running_mean, running_var, training, momentum, eps, activation, slope=0.01):
        if x.size(0) == 1:
            return F.batch_norm(x, running_mean, running_var, weight, bias, False, momentum, eps), None, None

        # Initialize BatchNorm
        bn = nn.BatchNorm2d(x.size(1), eps=eps, momentum=momentum, affine=True).to(x.device)

        # Load weights & running stats
        with torch.no_grad():
            bn.weight.copy_(weight)
            bn.bias.copy_(bias)
            bn.running_mean.copy_(running_mean)
            bn.running_var.copy_(running_var)

        x = bn(x)

        # Apply activation function
        if activation == ACT_LEAKY_RELU:
            x = F.leaky_relu(x, negative_slope=slope, inplace=True)
        elif activation == ACT_RELU:
            x = F.relu(x, inplace=True)
        elif activation == ACT_ELU:
            x = F.elu(x, inplace=True)
        # ACT_NONE means no activation applied

        return x, running_mean, running_var

# Function hooks
inplace_abn = DummyInPlaceABNFunction.apply
inplace_abn_sync = inplace_abn

# Exported symbols
__all__ = ["inplace_abn", "inplace_abn_sync", "ACT_RELU", "ACT_LEAKY_RELU", "ACT_ELU", "ACT_NONE"]
