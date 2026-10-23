import os
import torch
import torch.nn.functional as F
from torchvision.utils import save_image
from torchvision import transforms
from PIL import Image
import numpy as np

import mediapipe as mp
import cv2
from networks import GMM, UnetGenerator, load_checkpoint

def extract_pose_tensor(image_path, image_size=(192, 256)):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    image = cv2.imread(image_path)
    image = cv2.resize(image, image_size)
    results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    pose_map = torch.zeros((17, image_size[1], image_size[0]))
    if results.pose_landmarks:
        for i, landmark in enumerate(results.pose_landmarks.landmark[:17]):

            x = int(landmark.x * image_size[0])
            y = int(landmark.y * image_size[1])
            if x > 1 and y > 1:
                pose_map[i, max(0, y - 4):y + 5, max(0, x - 4):x + 5] = 1.0
    return pose_map.unsqueeze(0)  # (1, 18, H, W)

def extract_shape_head(parsing_path, image_size=(192, 256)):
    parsing = Image.open(parsing_path).resize(image_size, Image.NEAREST)
    parsing_np = np.array(parsing)

    shape = (parsing_np > 0).astype(np.float32)
    head = ((parsing_np == 1) | (parsing_np == 2) | (parsing_np == 13)).astype(np.float32)

    shape = torch.from_numpy(shape).unsqueeze(0).unsqueeze(0)
    head = torch.from_numpy(head).unsqueeze(0).unsqueeze(0)
    return shape, head

def preprocess_image(image_path, size=(192, 256)):
    image = Image.open(image_path).convert("RGB")
    image = image.resize(size, Image.BILINEAR)
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))
    ])
    return transform(image).unsqueeze(0)  # (1, 3, H, W)

def run_tryon(user_img_path, product_img_path):
    try:
        device = torch.device("cpu")

        os.system(
            "python Self-Correction-Human-Parsing/simple_extractor.py "
            "--dataset lip "
            "--model-restore Self-Correction-Human-Parsing/checkpoints/exp-schp-201908261155-lip.pth "
            "--input-dir tryon_ai/uploads "
            "--output-dir tryon_ai/parsing"
        )

        print("[INFO] Preprocessing images...")
        person = preprocess_image(user_img_path).to(device)
        cloth = preprocess_image(product_img_path).to(device)
        mask = torch.ones_like(cloth[:, 0:1, :, :])

        pose = extract_pose_tensor(user_img_path).to(device)
        shape, head = extract_shape_head("tryon_ai/parsing/user_image.png")
        
        agnostic = torch.cat([
            shape,                    
            head,                   
            person[:, :1, :, :] * head, 
            pose,                   
            torch.zeros_like(person[:, :2, :, :])  
        ], 1).to(device)

        print("[DEBUG] agnostic shape:", agnostic.shape)

        print("[INFO] Running GMM...")
        class DummyOpt:
            def __init__(self):
                self.grid_size = 5
                self.radius = 5
                self.fine_height = 256
                self.fine_width = 192

        opt = DummyOpt()
        gmm = GMM(opt)

        load_checkpoint(gmm, "checkpoints/gmm_train/gmm_final.pth")
        gmm.eval().to(device)

        grid, _ = gmm(agnostic, cloth)
        warped_cloth = F.grid_sample(cloth, grid, padding_mode='border')
        warped_mask = F.grid_sample(mask, grid, padding_mode='zeros')

        print("[DEBUG] warped_cloth shape:", warped_cloth.shape)

        print("[INFO] Running TOM...")
        
        additional_channels = torch.cat([
            warped_mask,                     
            person[:, 1:2, :, :] * head,      
            person[:, 2:3, :, :] * head       
        ], 1)
        
        tom_input = torch.cat([
            agnostic,        
            warped_cloth,    
            additional_channels  
        ], 1)                

        print("[DEBUG] tom_input shape:", tom_input.shape)

        tom = UnetGenerator(28, 3 + 1, 6, ngf=64, norm_layer=torch.nn.InstanceNorm2d)
        load_checkpoint(tom, "checkpoints/tom_train/tom_final.pth")
        tom.eval().to(device)

        output = tom(tom_input)
        p_rendered, m_composite = torch.split(output, 3, 1)
        p_rendered = torch.tanh(p_rendered)
        m_composite = torch.sigmoid(m_composite)

        p_tryon = warped_cloth * m_composite + p_rendered * (1 - m_composite)

        print("[DEBUG] p_tryon min/max:", p_tryon.min().item(), p_tryon.max().item())

        save_dir = "cp-vton/result/Tryon results"
        os.makedirs(save_dir, exist_ok=True)
        save_image(p_tryon, os.path.join(save_dir, "tryon_result.jpg"), normalize=True)

        print("[INFO] Try-on result saved.")
        return os.path.join(save_dir, "tryon_result.jpg")

    except Exception as e:
        print("[ERROR] Try-on failed:", str(e))
        raise e