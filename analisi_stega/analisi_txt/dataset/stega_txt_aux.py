from PIL import Image
import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

from stega.stega_txt import hide_message_txt
from crypto.crypto_aes import aes_encrypt

def main():
    input_folder = os.path.join(root_path,"analisi_stega" ,"analisi_txt","dataset", "clean")
    output_folder = os.path.join(root_path, "analisi_stega" ,"analisi_txt", "dataset", "stega")

    os.makedirs(output_folder, exist_ok=True)
    
    images = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith((".txt"))
    ]

    print("\n==============================")
    print("      GENERADOR DE DOCUMENTS       ")
    print("==============================\n")

    count = 0
    password = "Password2026!"
    final_message = ""
    # For all images in the input folder, generate a stego image with the hidden message and save it to the output folder
    for i, img_name in enumerate(images[:50]):
        input_path = os.path.join(input_folder, img_name)
        output_path = os.path.join(output_folder, f"stego_{i}.txt")

        try:
            # Depending on the index, decide whether to encrypt the message or not (depends on the different validations)
            if i < 25:
                # final_message = b"missatge ocult de esteganografia per al TFG"
                tipo = "PLA"
                final_message = aes_encrypt("missatge ocult de esteganografia per al TFG", password, 16)
                # tipo = "XIFRAT"
            else:
                # final_message = b"missatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFGmissatge ocult de esteganografia per al TFG"
                # tipo = "PLA"
                # final_message = b"missatge ocult de esteganografia per al TFG"

                final_message = aes_encrypt("missatge ocult de esteganografia per al TFG", password, 16)
                tipo = "XIFRAT"

            # Hide the message in the text file
            hide_message_txt(input_path, output_path, final_message, password)

            print(f"[OK] {img_name} → stego_{i}.txt [{tipo}]")

            count += 1

        except Exception as e:
            print(f"[ERROR] {img_name}: {e}")

    print("\n==============================")
    print(f"Documents generats: {count}")
    print("==============================\n")


if __name__ == "__main__":
    main()