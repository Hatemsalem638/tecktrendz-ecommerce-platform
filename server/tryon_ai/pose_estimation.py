# pose_estimation.py
import cv2
import numpy as np
import mediapipe as mp
import torch

def get_pose_map(image_path, image_size=(192, 256), num_keypoints=18):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True)
    image = cv2.imread(image_path)
    image = cv2.resize(image, image_size)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    pose_map = torch.zeros(num_keypoints, image_size[1], image_size[0])
    if results.pose_landmarks:
        for i, lm in enumerate(results.pose_landmarks.landmark):
            x, y = int(lm.x * image_size[0]), int(lm.y * image_size[1])
            if 0 <= x < image_size[0] and 0 <= y < image_size[1] and i < num_keypoints:
                pose_map[i, y, x] = 1.0
                # expand the point into a small square for visibility
                pose_map[i, max(0, y-3):y+3, max(0, x-3):x+3] = 1.0

    return pose_map
