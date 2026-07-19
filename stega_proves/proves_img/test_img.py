import os 
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

from stega.stega_img import hide_message_img_save, unhide_message_img_save
from crypto.crypto_aes import aes_encrypt, aes_decrypt

def controller_hide_message(path: str, encrypt: int, message: str, password: str):
    # Pre: Requierd parameters path file, key_size (16, 32), message and the password. All the needed parameter for the algorithm to work correctly.
    # Post: The message hidden in the document path+_hidden
    encrypted_message = aes_encrypt(message, password, int(encrypt))
    name, ext = os.path.splitext(path_in)
    
    path_out = name + "_hidden" + ext
    hide_message_img_save(path, path_out, encrypted_message, password)

def controller_unhide_message(path: str, password: str) -> str:
    # Pre: Requierd parameters path file and the password. All the needed parameter for the algorithm to work correctly.
    # Post: The message that was hidden in the path
    name, ext = os.path.splitext(path)
    path_out = name + "_hidden" + ext

    ciphertext = unhide_message_img_save(path_out, password)
    return aes_decrypt(ciphertext, password)

if __name__ == '__main__':
    base_dir = os.path.dirname(__file__)

    try:

        print("------------------ Prova 1 ------------------")
        print("------------ Amaguem el missatge ------------")
        message = "Missatge a amagar 1"
        print("Missatge a amagar: " + message)

        path_in = os.path.join(base_dir, "prova1.png")
        print("Introdueix el path fitxer de text: " + path_in )

        password = "Password2026!"
        print("Introduim password: " + password)

        controller_hide_message(path_in, 32, message, password)


        print("------------ Obtenim el missatge ------------")
        path_in = os.path.join(base_dir, "prova1.png")
        print("Obrim fitxer: " + path_in)

        password = "Password2026!"
        print("Introduim password: " + password)

        messDec = controller_unhide_message(path_in, password)

        print("El missatge obtingut és: " + messDec)

    except Exception as e:
       print(f"Error Prova 1: {e}")

    try:

        print("------------------ Prova 2 ------------------")
        print("------------ Amaguem el missatge ------------")
        message = "Missatge a amagar 2 molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt molt llarg"
        print("Missatge a amagar: " + message)

        path_in = os.path.join(base_dir, "prova2.png")
        print("Introdueix el path fitxer de text: " + path_in )

        password = "Password2026!"
        print("Introduim password: " + password)

        controller_hide_message(path_in, 32, message, password)

        print("------------ Obtenim el missatge ------------")
        path_in = os.path.join(base_dir, "prova2.png")
        print("Obrim fitxer: " + path_in)

        password = "Password2026!"
        print("Introduim password: " + password)

        messDec = controller_unhide_message(path_in, password)

        print("El missatge obtingut és: " + messDec)

    except Exception as e:
        print(f"Error Prova 2: {e}")

    
    try:
        print("------------------ Prova 3 ------------------")
        print("------------ Amaguem el missatge ------------")
        message = "Missatge a amagar 3"
        print("Missatge a amagar: " + message)

        path_in = os.path.join(base_dir, "prova3.png")
        print("Introdueix el path fitxer de text: " + path_in )

        password = "Password2026!"
        print("Introduim password: " + password)

        controller_hide_message(path_in, 32, message, password)

        print("------------ Obtenim el missatge ------------")
        path_in = os.path.join(base_dir, "prova3.png")
        print("Obrim fitxer: " + path_in)

        password = "Password2025!"
        print("Introduim password erronea: " + password)

        messDec = controller_unhide_message(path_in, password)

        print("El missatge obtingut és: " + messDec)

        password = "Password2026!"
        print("Probem ara amb la contrasenya: " + password)

        messDec = controller_unhide_message(path_in, password)

        print("El missatge obtingut és: " + messDec)
    
    except Exception as e:
        print(f"Error Prova 3: {e}")

    try:

        password = "Password2026!"
        print("Probem ara amb la contrasenya: " + password)

        messDec = controller_unhide_message(path_in, password)

        print("El missatge obtingut és: " + messDec)
    
    except Exception as e:
        print(f"Error Prova 3: {e}")
