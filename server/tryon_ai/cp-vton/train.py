# coding=utf-8
import os
import time
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.utils as vutils
from tensorboardX import SummaryWriter
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from networks import GMM, UnetGenerator, load_checkpoint, save_checkpoint
from cp_dataset import CPDataset, CPDataLoader

class GMMTrainer(nn.Module):
    def __init__(self, opt):
        super(GMMTrainer, self).__init__()
        self.opt = opt
        self.model = GMM(opt)
        self.l1loss = nn.L1Loss()

    def forward(self, inputs):
        agnostic = inputs['agnostic'].to(self.opt.device)
        cloth = inputs['cloth'].to(self.opt.device)
        target = inputs['cloth_mask'].to(self.opt.device)

        grid, theta = self.model(agnostic, cloth)
        warped_cloth = nn.functional.grid_sample(cloth, grid, padding_mode='border', align_corners=True)
        warped_mask = nn.functional.grid_sample(target, grid, padding_mode='zeros', align_corners=True)

        loss = self.l1loss(warped_mask, target)
        return loss, warped_cloth, warped_mask, grid

class TOMTrainer(nn.Module):
    def __init__(self, opt):
        super(TOMTrainer, self).__init__()
        self.opt = opt
        self.model = UnetGenerator(25 + 0, 4, 6, ngf=64, norm_layer=nn.InstanceNorm2d)
        self.l1loss = nn.L1Loss()
        self.vggloss = nn.L1Loss()  # Replace with VGG perceptual loss if desired

    def forward(self, inputs):
        agnostic = inputs['agnostic'].to(self.opt.device)
        cloth = inputs['cloth'].to(self.opt.device)
        parse_cloth = inputs['parse_cloth'].to(self.opt.device)

        input_tensor = torch.cat([agnostic, cloth], 1)
        output = self.model(input_tensor)
        rendered, mask = torch.split(output, 3, 1)
        rendered = torch.tanh(rendered)
        mask = torch.sigmoid(mask)

        p_tryon = cloth * mask + rendered * (1 - mask)
        loss = self.l1loss(p_tryon, parse_cloth)
        return loss, p_tryon, mask

def train_gmm(opt):
    dataset = CPDataset(opt)
    loader = CPDataLoader(opt, dataset).data_loader

    trainer = GMMTrainer(opt).to(opt.device)
    optimizer = torch.optim.Adam(trainer.parameters(), lr=opt.lr, betas=(0.5, 0.999))

    for step in range(opt.steps):
        for batch in loader:
            optimizer.zero_grad()
            loss, warped_cloth, warped_mask, grid = trainer(batch)
            loss.backward()
            optimizer.step()
            print(f"[GMM] Step {step}, Loss: {loss.item():.4f}")

            # ✅ Save warped outputs for TOM
            save_path_cloth = os.path.join("cp-vton", "result", opt.datamode, "warp-cloth")
            save_path_mask = os.path.join("cp-vton", "result", opt.datamode, "warp-mask")
            os.makedirs(save_path_cloth, exist_ok=True)
            os.makedirs(save_path_mask, exist_ok=True)

            for i in range(warped_cloth.size(0)):
                name = batch['c_name'][i]
                vutils.save_image(warped_cloth[i], os.path.join(save_path_cloth, name), normalize=True)
                vutils.save_image(warped_mask[i], os.path.join(save_path_mask, name), normalize=True)

        if step % opt.save_interval == 0:
            save_checkpoint(trainer.model, os.path.join(opt.checkpoint_dir, f"gmm_step{step}.pth"))

def train_tom(opt):
    dataset = CPDataset(opt)
    loader = CPDataLoader(opt, dataset).data_loader

    trainer = TOMTrainer(opt).to(opt.device)
    optimizer = torch.optim.Adam(trainer.parameters(), lr=opt.lr, betas=(0.5, 0.999))

    for step in range(opt.steps):
        for batch in loader:
            optimizer.zero_grad()
            loss, p_tryon, mask = trainer(batch)
            loss.backward()
            optimizer.step()
            print(f"[TOM] Step {step}, Loss: {loss.item():.4f}")

        if step % opt.save_interval == 0:
            save_checkpoint(trainer.model, os.path.join(opt.checkpoint_dir, f"tom_step{step}.pth"))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', default='cuda' if torch.cuda.is_available() else 'cpu')
    parser.add_argument('--dataroot', default='data')
    parser.add_argument('--datamode', default='train')
    parser.add_argument('--data_list', default='train_pairs.txt')
    parser.add_argument('--fine_width', type=int, default=192)
    parser.add_argument('--fine_height', type=int, default=256)
    parser.add_argument('--radius', type=int, default=5)
    parser.add_argument('--batch-size', type=int, default=4)
    parser.add_argument('--workers', type=int, default=2)
    parser.add_argument('--shuffle', action='store_true')
    parser.add_argument('--stage', choices=['GMM', 'TOM'], default='GMM')
    parser.add_argument('--lr', type=float, default=0.0001)
    parser.add_argument('--steps', type=int, default=1000)
    parser.add_argument('--save_interval', type=int, default=200)
    parser.add_argument('--checkpoint_dir', default='checkpoints')
    parser.add_argument('--grid_size', type=int, default=5)

    opt = parser.parse_args()

    if opt.stage == 'GMM':
        train_gmm(opt)
    else:
        train_tom(opt)