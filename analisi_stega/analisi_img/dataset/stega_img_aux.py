from PIL import Image
import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

from stega.stega_img import hide_message_img
from crypto.crypto_aes import aes_encrypt

def main():
    # Define the input and output folders
    input_folder = os.path.join(root_path,"analisi_stega" ,"analisi_img","dataset", "clean_reduced")
    output_folder = os.path.join(root_path, "analisi_stega" ,"analisi_img", "dataset", "stega")

    os.makedirs(output_folder, exist_ok=True)
    
    images = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith((".png"))
    ]

    print("\n==============================")
    print("      GENERADOR D'IMATGES       ")
    print("==============================\n")

    count = 0
    password = "Password2026!"
    final_message = ""
    # For all images in the input folder, generate a stego image with the hidden message and save it to the output folder
    for i, img_name in enumerate(images[:50]):
        input_path = os.path.join(input_folder, img_name)
        output_path = os.path.join(output_folder, f"stego_{i}.png")

        try:
            # Load the image
            img = Image.open(input_path).convert("RGB")

            # Depending on the index, decide whether to encrypt the message or not (depends on the different validations)
            if i < 25:


                #final_message = b"missatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFG"
                tipo = "PLA"
                final_message = aes_encrypt("mist de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFG", password, 16)
                # tipo = "XIFRAT"
            else:
                #final_message = b"missatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFG"
                # tipo = "PLA"
                final_message = aes_encrypt("mist de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFG", password, 16)


                #final_message = b"missatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFG"
                tipo = "XIFRAT"

            # Hide the message in the image
            stego_img = hide_message_img(img, final_message,password)

            # Save the stego image to the output folder
            stego_img.save(output_path)

            print(f"[OK] {img_name} → stego_{i}.png [{tipo}]")

            count += 1

        except Exception as e:
            print(f"[ERROR] {img_name}: {e}")

    print("\n==============================")
    print(f"Imatges generades: {count}")
    print("==============================\n")


if __name__ == "__main__":
    main()