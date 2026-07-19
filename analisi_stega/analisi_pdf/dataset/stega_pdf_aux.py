import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

from stega.stega_pdf import hide_message_pdf
from crypto.crypto_aes import aes_encrypt

def main():
    # Input and output folders for the PDF files
    input_folder = os.path.join(root_path,"analisi_stega","analisi_pdf","dataset","clean")
    output_folder = os.path.join(root_path,"analisi_stega","analisi_pdf","dataset","stega")

    os.makedirs(output_folder, exist_ok=True)

    pdfs = [
        f for f in os.listdir(input_folder)
        if f.lower().endswith(".pdf")
    ]

    print("\n==============================")
    print("      GENERADOR DE PDFS       ")
    print("==============================\n")

    password = "Password2026!"
    count = 0

    message = (
        "missatge ocult de esteganografia per al TFG"
        "missatge ocult de esteganografia per al TFG"
        "missatge ocult de esteganografia per al TFG"
        "missatge ocult de esteganografia per al TFG"
        "missatge ocult de esteganografia per al TFG"
    )

    for i, pdf_name in enumerate(pdfs[:50]):
        # Input and output paths for the current PDF file
        input_path = os.path.join(input_folder, pdf_name)
        output_path = os.path.join(output_folder, f"stego_{i}.pdf")

        try:

            # First 25 PDFs
            if i < 25:

                # Chiprtext message
                final_message = aes_encrypt(message, password, 16)
                tipo = "XIFRAT"
            # Last 25 PDFs
            else:
                # Plaintext message
                final_message = message
                tipo = "PLA"

            hide_message_pdf(input_path,output_path,final_message,password)

            print(f"[OK] {pdf_name} -> stego_{i}.pdf [{tipo}]")
            count += 1

        except Exception as e:
            print(f"[ERROR] {pdf_name}: {e}")

    print("\n==============================")
    print(f"PDFs generats: {count}")
    print("==============================\n")


if __name__ == "__main__":
    main()