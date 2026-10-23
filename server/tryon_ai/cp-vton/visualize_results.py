import cv2
import os
import numpy as np

input_path = 'data/test/image/'
cloth_path = 'data/test/cloth/'
result_path = 'result/tom_test/'

output_dir = 'visualization'
os.makedirs(output_dir, exist_ok=True)

for file in os.listdir(result_path):
    if file.endswith('.jpg'):
        im_name = file
        input_img = cv2.imread(os.path.join(input_path, im_name))
        cloth_img = cv2.imread(os.path.join(cloth_path, im_name))
        result_img = cv2.imread(os.path.join(result_path, im_name))

        # Combine them side-by-side
        combined = np.hstack((input_img, cloth_img, result_img))
        cv2.imwrite(os.path.join(output_dir, im_name), combined)
