import os
import sys
import io
from PIL import Image
import fitz
from hashlib import sha256
from random import Random

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

from stega.stega_img import hide_message_img, unhide_message_img

MAX_SIZE = 200  # MAX_SIZE of the image that will be inserted
MAX_BLOCKS = 50 # MAX_BLOCK with the message inside the pdf
INDEX_SIZE = 4  # INDEX_SIZE in bytes encode the order the blocks
LENGTH_SIZE = 4  # LENGTH_SIZE in bytes encode the length of the message
HASH_SIZE = 8  # HASH_SIZE in bytes to store the hash of the message and password
HEADER_SIZE = HASH_SIZE + LENGTH_SIZE  # Total header size in bytes

def seed_from_password(password: str) -> int:
    # Pre: A string that represents a password non-empty string
    # Post: A unique int generated based on the password
    hash_bytes = sha256(password.encode()).digest()
    return int.from_bytes(hash_bytes, "big")

def split_message(message: bytes, chunk_size: int) -> list[bytes]:
    # Pre: A sequence of bytes that represent the message and a positive integer that represents the size of the block
    # Post: Returns a list of byte blocks, each of size at most chunk_size
    return [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]

def get_page_sequence(pdf: fitz.Document, password: str, max_blocks: int) -> list[int]:
    # Pre: pdf is an opened pdf, a password and the max of blocks that de pdf can co
    # Post: A list of indices shufflede based on the password and the max blocks of the pdf

    # Generate a pseudo-random sequence of page indices based on the password
    # Get deterministic seed and random generator with that seed
    seed = seed_from_password(password)
    rng = Random(seed)
 
    # Pages indices shuffled 
    num_pages = len(pdf)
    pages = list(range(num_pages))
    rng.shuffle(pages)

    return pages[:max_blocks]

def bytes_to_bits(message: bytes) -> str:
    # Pre: A message in bytes format
    # Post: A string representing the binary encoding of the message
    if not message:
        raise ValueError("There's no message to be encoded")    
    return ''.join(format(b, '08b') for b in message)

def bits_to_bytes(binary: str) -> bytes:
    # Pre: A string containing a binary sequence
    # Post: The decoded bytes corresponding to the binary string
    if not binary:
        raise ValueError("There's no sequence of bytes to be decoded")
    if any(c not in "01" for c in binary):
        raise ValueError("Binary string contains invalid characters")
    if len(binary) % 8 != 0:
        binary += "0" * (8 - len(binary) % 8)
    # The conversion
    return bytes(int(binary[i:i+8], 2) for i in range(0, len(binary), 8))

def compute_max_bytes(rect: fitz.Rect) -> int:
    # Pre: A rectangle representing the area where the image will be inserted
    # Post: The maximum number of bytes that can be hidden in an image of the given rectangle size

    # Limit image size to avoid oversized embedding
    w = min(int(rect.width), MAX_SIZE)
    h = min(int(rect.height), MAX_SIZE)

    # Each pixel stores 3 bits (RGB LSB steganography)
    capacity_bits = w * h * 3

    # Convert to bytes (floor division)
    capacity_bytes = capacity_bits // 8

    # Reserve space for index header
    usable_bytes = capacity_bytes - INDEX_SIZE

    # Safety check
    if usable_bytes <= 0:
        raise ValueError("Not enough capacity in page to store hidden data")

    return usable_bytes

def compute_pdf_capacity(pdf: fitz.Document) -> list[int]:
    # Pre: An opened PDF document
    # Post: A list of maximum byte capacities for each page in the PDF
    capacities = []

    for page in pdf:
        blocks_page = page.get_text("blocks")
        page_rect = page.rect

        max_y = max((b[3] for b in blocks_page if b[4].strip()), default=0)
        margin = 10

        rect = fitz.Rect(margin, max_y + margin,
                         page_rect.width - margin,
                         page_rect.height - margin)

        capacity = compute_max_bytes(rect)
        capacities.append(capacity)

    return capacities


def hide_message_aux(path_in: str, path_out: str, bytes_message: bytes, password: str) -> None:
    # Pre: path_in is a valid path to an existing PDF file path_out is a path that does not already exist message is a string representing a binary sequence password is a string.
    # Post: creates a new PDF at path_out with the hidden message embedded in images.

    # Open PDF and convert the message to bytes
    pdf = fitz.open(path_in)

    # Create a hash to verify integrity and password correctness
    hash_check = sha256(password.encode() + bytes_message).digest()[:HASH_SIZE]
    # Store message length in 4 bytes
    length_prefix = len(bytes_message).to_bytes(LENGTH_SIZE, 'big')
    # Construct full message: hash + length + actual message
    full_message = hash_check + length_prefix + bytes_message

    # Split message into chunks that fit into blocks and add index to each block (first 4 bytes)    
    capacities = compute_pdf_capacity(pdf)
    chunk_size = min(capacities)
    raw_blocks = split_message(full_message, chunk_size)
    blocks = [i.to_bytes(INDEX_SIZE, 'big') + block for i, block in enumerate(raw_blocks)]

    num_pages = len(pdf)
    if len(blocks) > num_pages:
        raise ValueError("Not enough pages to hide all blocks")

    # Get page order based on password
    pages = get_page_sequence(pdf, password, len(blocks))

    # Insert each block into a different page
    for block, page_index in zip(blocks, pages):
        page = pdf[page_index]

        # Get text blocks to find free space
        blocks_page = page.get_text("blocks")
        page_rect = page.rect

        # Find the lowest text position
        max_y = max((b[3] for b in blocks_page if b[4].strip()), default=0)
        margin = 10

        if max_y + margin >= page_rect.height:
            raise ValueError("There's no space in the pdf")

        # Define rectangle where image will be inserted and create a limited white image
        rect = fitz.Rect(margin, max_y + margin, page_rect.width - margin, page_rect.height - margin)
        MAX_BYTES = compute_max_bytes(rect)
        w, h = min(int(rect.width), MAX_SIZE), min(int(rect.height), MAX_SIZE)
        img = Image.new("RGB", (w, h), "white")

        if len(block) > MAX_BYTES:
            raise ValueError("Block too large for image encoding")

        # Hide block inside image and insert to PDF
        img = hide_message_img(img, block, password)
        img_bytes = io.BytesIO()
        img.save(img_bytes, format="PNG")
        page.insert_image(rect, stream=img_bytes.getvalue())

    pdf.save(path_out)
    pdf.close()


def unhide_message_aux(path: str, password: str) -> bytes:
    # Pre: path is a valid path to an existing PDF file password is the correct string used during encoding.
    # Post: Returns the extracted hidden message in the pdf as string.

    # Open PDF and get page sequence based on password
    pdf = fitz.open(path)
    sequence = get_page_sequence(pdf, password, MAX_BLOCKS)

    chunks: dict[int, bytes] = {} # Store extracted blocks
    expected_length = None # Total expected lenght
    message_bytes = None # The message in bytes

    # Insert each block into a different page
    for page_index in sequence:

        # Get images of one page
        page = pdf[page_index]
        images = page.get_images(full=True)

        if not images:
            continue
        
        # Try last image first (most likely inserted)
        candidate_indices = [len(images) - 1]
        candidate_indices += list(reversed(range(len(images) - 1)))

        # For each image in the page
        for img_idx in candidate_indices:

            # Get image information
            xref, width, height = images[img_idx][:3]

             # Skip large images
            if width > MAX_SIZE or height > MAX_SIZE:
                continue
            
            # Extract image
            pix = fitz.Pixmap(pdf, xref)
            if pix.n > 3:
                pix = fitz.Pixmap(fitz.csRGB, pix)

            img_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            try:
                # Try to extract hidden data
                chunk = unhide_message_img(img_pil,password)

                if len(chunk) < INDEX_SIZE:
                    continue

                # Extract index and data
                index = int.from_bytes(chunk[:INDEX_SIZE], 'big')
                data = chunk[INDEX_SIZE:]

                chunks[index] = data
                break

            except Exception:
                continue

    pdf.close()

    # If there aren't chunks
    if 0 not in chunks:
        raise ValueError("No hidden message found or incomplete data")

    # Reorder the chunks 
    ordered_parts = []
    for i in range(len(chunks)):
        if i in chunks:
            ordered_parts.append(chunks[i])
        else:
            raise ValueError("Incomplete data: missing sequence blocks")

    ordered = b''.join(ordered_parts)
    
    # Extract expected total length (after header)
    expected_length = int.from_bytes(ordered[HASH_SIZE:HEADER_SIZE], 'big')
    total_length = HEADER_SIZE + expected_length

    if len(ordered) < total_length:
        raise ValueError("No hidden message found or incomplete data")
    
    hash_stored = ordered[:HASH_SIZE]
    message_bytes = ordered[HEADER_SIZE:total_length]

    hash_calc = sha256(password.encode() + message_bytes).digest()[:HASH_SIZE]
    
    if hash_stored != hash_calc:
        raise ValueError("Invalid password or corrupted PDF")

    return message_bytes


def hide_message_pdf(path_in: str, path_out: str, message: bytes, password: str) -> None:
    # Pre: path_in is the input PDF path, path_out is the output PDF path, message is the binary string to hide
    # Post: A new PDF is created with the hidden message embedded

    if not os.path.exists(path_in):
        raise FileNotFoundError(f"Input file {path_in} does not exist")
    if os.path.exists(path_out):
        raise FileExistsError("Output file already exists")
    if message == None:
        raise ValueError("There's no message")

    try:
        # Encode and hide the message inside the PDF
        hide_message_aux(path_in, path_out, message, password)

    except OSError as e:
        raise ValueError(f"Encode error: {e}")
    
    return 

def unhide_message_pdf(path: str, password: str) -> str:
    # Pre: Path to the PDF file
    # Post: The extracted hidden message in binary string format
    
    if not os.path.exists(path):
        raise FileNotFoundError(f"Input file {path} does not exist")

    try:
        # Decode and extract the hidden message from the PDF
        return unhide_message_aux(path, password)

    except OSError as e:
        raise ValueError(f"Decode error: {e}")
    
    return
