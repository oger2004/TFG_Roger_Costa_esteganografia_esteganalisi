from PIL import Image
import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

input_folder = os.path.join(root_path,"analisi_stega" ,"analisi_img","dataset", "clean")
output_folder = os.path.join(root_path, "analisi_stega" ,"analisi_img", "dataset", "clean_reduced")

os.makedirs(output_folder, exist_ok=True)

MAX_SIZE = (64, 64) # Define the maximum size for the reduced images

def main():
    # For each file in the input folder
    for file in os.listdir(input_folder):
        # check if it's an image
        if not file.lower().endswith((".png")):
            continue

        path_in = os.path.join(input_folder, file)
        path_out = os.path.join(output_folder, file)

        try:
            img = Image.open(path_in).convert("RGB")
            # resize it while maintaining aspect ratio
            img.thumbnail(MAX_SIZE)
            # save it to the output folder with compression
            img.save(path_out, optimize=True, quality=70)

            print(f"[OK] {file}")

        except Exception as e:
            print(f"[ERROR] {file}: {e}")

if __name__ == "__main__":
    main()
