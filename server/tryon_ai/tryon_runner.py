# tryon_runner.py

from tryon_model import run_tryon
import sys
import os

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("[ERROR] Please provide paths for user image and product image.")
        sys.exit(1)

    user_img_path = sys.argv[1]
    product_img_path = sys.argv[2]

    if not os.path.exists(user_img_path):
        print(f"[ERROR] User image not found at: {user_img_path}")
        sys.exit(1)

    if not os.path.exists(product_img_path):
        print(f"[ERROR] Product image not found at: {product_img_path}")
        sys.exit(1)

    try:
        result_path = run_tryon(user_img_path, product_img_path)
        print(f"[SUCCESS] Try-on result saved at: {result_path}")
    except Exception as e:
        print(f"[ERROR] Try-on pipeline failed: {str(e)}")
