from PIL import Image, UnidentifiedImageError
import os
import hashlib
import random

def bytes_to_binary(text: bytes) -> str:
    # Pre: A text in utf-8 format contained in a string
    # Post: The binary encoding of the original text
    if not text:
        raise ValueError("There's no text to be encoded")    
    return ''.join(format(byte, '08b') for byte in text)

def seed_from_password(password: str) -> int:
    # Pre: A string that represents a password
    # Post: A unique int generated based on the password
    hash_bytes = hashlib.sha256(password.encode()).digest()
    return int.from_bytes(hash_bytes, "big")

def binary_to_bytes(binary: str) -> bytes:
    # Pre: A binary string representing one byte
    # Post: The decoded character corresponding to the binary byte
    if not binary:
        raise ValueError("There's no sequence of bytes to be decoded")
    if len(binary) != 8:
        raise ValueError("Binary length must be 8")
    if any(c not in "01" for c in binary):
        raise ValueError("Binary string contains invalid characters")
    # The conversion
    return bytes(
        int(binary[i:i+8], 2)
        for i in range(0, len(binary), 8)
    )

def get_dynamic_marker(password: str) -> bytes:
    # Pre: The password introduced by the user
    # Post: A piece of the hashed password
    return hashlib.sha256(password.encode()).digest()[:8]

def enough_capacity(binary_message: str, width: int, height: int) -> bool:
    # Pre: The binary_message is the message that will be hidden, width and height are the measures of the image the message will be hidden in
    # Post: True, If the message can fit in the image, otherwise it returns False
    if not binary_message:
        raise ValueError("There's no sequence of bytes")
    if not width:
        raise ValueError("There's no width defined")
    if not height:
        raise ValueError("There's no height defined")

    capacity = width * height * 3 # For each pixel we can modify the bits of r g b
    # The length of the binary message does not exceed the capacity
    return len(binary_message) <= capacity

def obtain_message(width: int, height: int, pixels, password: str) -> bytes:
    # Pre: The size of the image (width and height) and its pixels
    # Post: The decoded hidden message
    if not pixels:
        raise ValueError("There's no image to extract a message")
    if not width:
        raise ValueError("There's no width defined")
    if not height:
        raise ValueError("There's no height defined")

    # Getting positions from password
    num_pixels = width * height
    seed = seed_from_password(password)
    end_marker = get_dynamic_marker(password)
    rng = random.Random(seed)
    positions = rng.sample(range(num_pixels), num_pixels)

    message = b""
    current_byte = ""
    # Go through all the pixels
    for idx in positions:
        x = idx % width
        y = idx // width
        # Split the pixel into its RGB components
        r, g, b = pixels[x, y]
        # Extract the least significant bit from each component
        for bit in (r & 1, g & 1, b & 1):
                current_byte += str(bit)
                # Every 8 bits (1 char), decode and append to the message
                if len(current_byte) == 8:
                    char = binary_to_bytes(current_byte)
                    message += char
                    current_byte = ""
                    # If the message ends with the marker we return the message without the marker
                    if message.endswith(end_marker):
                        return message[:-len(end_marker)]
    return None

def adding_bits(width: int, height: int, image: Image, binary_message: str, password: str) -> Image:
    # Pre: The size of the image (width and height) and the image where the binary_message will be hidden
    # Post: The image with the hidden binary_message
    if not width:
        raise ValueError("There's no width defined")
    if not height:
        raise ValueError("There's no height defined")
    if not image:
        raise ValueError("There's no image to add the message")
    if not binary_message:
        raise ValueError("There's no message to be hidden")
    
    # Getting positions from password
    num_pixels = width * height
    seed = seed_from_password(password)
    rng = random.Random(seed)
    pixels_needed = (len(binary_message) + 2) // 3
    positions = rng.sample(range(num_pixels), num_pixels)[:pixels_needed]


    image = image.convert("RGB")
    pixels = image.load()
    bit_index = 0
    message_length = len(binary_message)
    # Go through all the pixels
    for idx in positions:
        # Stop immediately if the entire message has already been embedded
        if bit_index >= message_length:
            break
        
        # Obtain the column based on the idx
        x = idx % width
        # Obtain the row based on the idx
        y = idx // width

        # Unpack the current RGB components of the selected pixel
        r, g, b = pixels[x, y]
        
        # Modify the Least Significant Bit (LSB) of the Red channel if bits remain
        if bit_index < message_length:
            # (r & ~1) clears the last bit, then | int(...) injects the secret bit
            r = (r & ~1) | int(binary_message[bit_index])
            bit_index += 1
        # Modify the Least Significant Bit (LSB) of the Green channel if bits remain
        if bit_index < message_length:
            g = (g & ~1) | int(binary_message[bit_index])
            bit_index += 1
        # Modify the Least Significant Bit (LSB) of the Blue channel if bits remain
        if bit_index < message_length:
            b = (b & ~1) | int(binary_message[bit_index])
            bit_index += 1
        # Save the modified RGB values back into the image pixel map
        pixels[x, y] = (r, g, b)
        
    return image
    
def hide_message_aux(message: bytes, image: Image, password: str) -> Image:
    end_marker = get_dynamic_marker(password)
    # Append the end_marker
    binary_message = bytes_to_binary(message) + bytes_to_binary(end_marker)
    # Obtain the binary coded sequence from the text
    width, height = image.size

    if not enough_capacity(binary_message, width, height):
        raise ValueError("The image can't contain the message")

    # Hide bits into less significant bit of each pixel
    image = adding_bits(width, height, image, binary_message, password)

    return image

def hide_message_img_save(path_in: str, path_out: str, message: bytes, password: str) -> None:
    # Pre: The path_in is the path to the source image, path_out is the path for the new image, message the text to hide
    # Post: A new image is created in path_out containing the hidden message
    end_marker = get_dynamic_marker(password)
    if not os.path.exists(path_in):
        raise FileNotFoundError(f"Input file {path_in} does not exist")
    if os.path.exists(path_out):
        raise FileExistsError("Output file already exists")
    if end_marker in message:
        raise ValueError("Invalid message")

    # Open image
    try:
        image = Image.open(path_in)
    except UnidentifiedImageError:
        raise ValueError("The file is not a valid image")

    image = hide_message_aux(message, image, password)
    image.save(path_out)
    return

def hide_message_img(img: Image, message: bytes, password: str) -> Image:
    # Pre: The path_in is the path to the source image, path_out is the path for the new image, message the text to hide
    # Post: A new image is created in path_out containing the hidden message
    if img is None or not isinstance(img, Image.Image):
        raise TypeError("Input is not a valid PIL Image")
    if message is None:
        raise ValueError("There's no message")
    end_marker = get_dynamic_marker(password)
    if end_marker in message:
        raise ValueError("Invalid message")

    # Open image
    image = hide_message_aux(message, img, password)
    return image

def unhide_message_img_save(path: str, password: str) -> bytes:
    # Pre: A path to the source image
    # Post: The extracted hidden message
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file {path} does not exist")
    
    # Open image
    try:
        image = Image.open(path)
    except UnidentifiedImageError:
        raise ValueError("The file is not a valid image")
    
    image = image.convert("RGB")
    pixels = image.load()

    width, height = image.size
     
    # Extract the hidden message
    message = obtain_message(width, height, pixels, password)

    #If the end marker it is found we have a message
    if message is None:
        raise ValueError("There's no message")
    else:
        return message


def unhide_message_img(img: Image, password: str) -> bytes:
    # Pre: A path to the source image
    # Post: The extracted hidden message

    pixels = img.load()

    width, height = img.size
     
    # Extract the hidden message
    message = obtain_message(width, height, pixels, password)

    #If the end marker it is found we have a message
    if message is None:
        raise ValueError("There's no message")
    else:
        return message
