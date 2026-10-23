import os

# Paths
dataroot = "data/train"
input_file = os.path.join("data", "train_pairs.txt")
output_file = os.path.join("data", "train_pairs_cleaned.txt")

# Counter for stats
total = 0
kept = 0
skipped = 0

# Read and validate
with open(input_file, "r") as f_in, open(output_file, "w") as f_out:
    for line in f_in:
        total += 1
        line = line.strip()
        if not line:
            continue
        im_name, c_name = line.split()

        warp_cloth_path = os.path.join(dataroot, "warp-cloth", c_name)
        warp_mask_path = os.path.join(dataroot, "warp-mask", c_name)

        if os.path.exists(warp_cloth_path) and os.path.exists(warp_mask_path):
            f_out.write(f"{im_name} {c_name}\n")
            kept += 1
        else:
            skipped += 1

print(f"✅ Done! Cleaned list written to: {output_file}")
print(f"➡️ Total: {total} | ✅ Kept: {kept} | ❌ Skipped: {skipped}")
