import os
import hashlib
import random

# Control bytes
BIT_0 = "\u200B"   # Zero Width Space
BIT_1 = "\u200C"   # Zero Width Non-Joiner

#Sense seed es podria amagar miss al inici o final
# Amb seed bit entre paraules
    # Si fem servir password per generar seed hem de saber com recuperar les posicions on realment hi ha el missatge
    # Per tant fem un hash de la password de forma que sempre sigui la mateixa seed tant per emisor com receptor
    # random no es segur, com no hi ha markers necesitem saber la mida del missatge el codifiquem en els primers 32bits 

def bytes_to_bits(message: bytes) -> str:
    # Pre: A text in utf-8 format contained in a string
    # Post: The binary encoding of the original text
    if not message:
        raise ValueError("There's no message to be encoded")    
    return ''.join(format(b, '08b') for b in message)

def bits_to_bytes(binary: str) -> bytes:
    # Pre: A binary string representing one byte
    # Post: The decoded character corresponding to the binary byte
    if not binary:
        raise ValueError("There's no sequence of bytes to be decoded")
    if any(c not in "01" for c in binary):
        raise ValueError("Binary string contains invalid characters")
    if len(binary) % 8 != 0:
        binary += "0" * (8 - len(binary) % 8)
    # The conversion
    return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))

def seed_from_password(password: str) -> int:
    # Pre: A string that represents a password
    # Post: A unique int generated based on the password
    hash_bytes = hashlib.sha256(password.encode()).digest()
    return int.from_bytes(hash_bytes, "big")

def unhide_message_aux(txt_file: str, password: str) -> bytes:
    # Pre: A text where a message is hidden and the password to obtain positions on where to look at the file
    # Post: The message decoded in bytes from the txt_file
    words = txt_file.split(" ")
    seed = seed_from_password(password)
    rng = random.Random(seed)

    # Positions from lenght of message
    positions = rng.sample(range(len(words) - 1), len(words) - 1)
    
    #First obtain the length of the message from each position
    length_bits = []
    for i in range(32):
        pos = positions[i]
        if words[pos].endswith(BIT_0):
            length_bits.append("0")
        elif words[pos].endswith(BIT_1):
            length_bits.append("1")
        else:
            raise ValueError(f"No bit found at position {pos}")
    
    # Obtain length message
    message_length = int(''.join(length_bits), 2)
    total_bits = 32 + message_length
    
    message_bits = []
    # For the next positions_full-32 positions we obtain the bits of the message 
    for pos in positions[32:total_bits]:
        if words[pos].endswith(BIT_0):
            message_bits.append("0")
        elif words[pos].endswith(BIT_1):
            message_bits.append("1")
        else:
            raise ValueError(f"No bit found at position {pos}")

    return bits_to_bytes(''.join(message_bits))

def hide_message_aux(txt_inicial: str, message: bytes, password: str) -> str:
    # Pre: The text where the message will be hiden and the password that will give us the positions
    # Post: The initial text with the message hidden in it

    # Get words
    words = txt_inicial.split(" ")
    message_bits = bytes_to_bits(message)

    # Add the mesure of text for it to be known when unhide
    length_bits = format(len(message_bits), '032b')
    full_bits = length_bits + message_bits

    # Generate seed from, password
    seed = seed_from_password(password)
    rng = random.Random(seed)

    if len(full_bits) > len(words) - 1:
        raise ValueError("Text is too small to hide the message")

    # Ensure we don't put two bits in the same word
    positions = rng.sample(range(len(words) - 1), len(full_bits))

    # In each position the correspondant bit it's added
    for bit, pos in zip(full_bits, positions):
        if bit == "0":
            words[pos] += BIT_0
        else:
            words[pos] += BIT_1

    return " ".join(words) 
    
def hide_message_txt(path_in: str, path_out: str, message: bytes, password: str) -> None:
    # Pre: The path_in is the path to the source image, path_out is the path for the new image, message the text to hide
    # Post: A new image is created in path_out containing the hidden message
    if not os.path.exists(path_in):
        raise FileNotFoundError(f"Input file {path_in} does not exist")
    if os.path.exists(path_out):
        raise FileExistsError("Output file already exists")
    
    try:
        # Open file
        with open(path_in, "r", encoding="utf-8") as f:
            txt_inicial = f.read()

        # Encode message
        txt_inicial_missatge = hide_message_aux(txt_inicial, message, password)

        # Save new file
        with open(path_out, "w", encoding="utf-8") as f:
            f.write(txt_inicial_missatge)

    except OSError as e:
        raise ValueError(f"File error: {e}")
    
    return

def unhide_message_txt(path: str, password: str) -> bytes:
    # Pre: A path to the source image
    # Post: The extracted hidden message
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file {path} does not exist")
    
    # Open file
    with open(path, "r", encoding="utf-8") as f:
        txt_file = f.read()

    # Encode message
    message = unhide_message_aux(txt_file, password)

    #If the end marker it is found we have a message
    if message is None:
        raise ValueError("There's no message")
    else:
        return message
