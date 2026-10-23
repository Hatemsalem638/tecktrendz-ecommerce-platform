import mediapipe as mp
import cv2
import numpy as np
from PIL import Image, ImageDraw
import torch
import torchvision.transforms as transforms
import os

POSE_CHANNELS = 18
IMAGE_SIZE = (192, 256)
RADIUS = 5

transform_gray = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.5,), (0.5,))
])

def generate_pose_tensor(image_path, save_debug_path=None):
    image = cv2.imread(image_path)
    image = cv2.resize(image, IMAGE_SIZE)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    results = pose.process(image_rgb)

    pose_tensor = torch.zeros((POSE_CHANNELS, IMAGE_SIZE[1], IMAGE_SIZE[0]))

    if results.pose_landmarks:
        for idx, lm in enumerate(results.pose_landmarks.landmark[:POSE_CHANNELS]):
            x = int(lm.x * IMAGE_SIZE[0])
            y = int(lm.y * IMAGE_SIZE[1])
            if 0 <= x < IMAGE_SIZE[0] and 0 <= y < IMAGE_SIZE[1]:
                one_map = Image.new('L', IMAGE_SIZE, 0)
                draw = ImageDraw.Draw(one_map)
                draw.rectangle((x - RADIUS, y - RADIUS, x + RADIUS, y + RADIUS), fill=255)
                one_tensor = transform_gray(one_map)[0]
                pose_tensor[idx] = one_tensor

    if save_debug_path:
        debug_img = image.copy()
        for idx, lm in enumerate(results.pose_landmarks.landmark[:POSE_CHANNELS]):
            x = int(lm.x * IMAGE_SIZE[0])
            y = int(lm.y * IMAGE_SIZE[1])
            if 0 <= x < IMAGE_SIZE[0] and 0 <= y < IMAGE_SIZE[1]:
                cv2.circle(debug_img, (x, y), 4, (0, 255, 0), -1)
        cv2.imwrite(save_debug_path, debug_img)

    return pose_tensor
