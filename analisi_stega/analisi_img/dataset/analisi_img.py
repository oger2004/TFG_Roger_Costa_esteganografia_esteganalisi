from PIL import Image, UnidentifiedImageError
import os
from math import log2
import sys
from collections import Counter
from zlib import compress
from statistics import variance

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

DICC_ES = ["el", "la", "de","que","y","a","en","un","ser","se","no","haber","por","con","su","para","como","estar","tener","le","lo","todo","pero","más","hacer","o","poder","decir","este","ir","otro","ese","si","me","ya","ver","porque","dar","cuando","él","muy","sin","vez","mucho","saber","qué","sobre", "mi","alguno","mismo","yo","también","hasta","año","dos","querer","entre","así","primero","desde","grande","eso","ni","nos","propio","e","tarde","mientras","además","cada","menos","oso","ahora","ejemplo","cual","solo","otras","parte","caso","nada","casa","antes","bien","forma","mundo","aún","nuevo","mil","lugar","ciudad","social","hecho","tiempo","misma","ella","sí","estos","tanto","cuanto","vida"]
DICC_EN = ["the", "the", "of", "that", "and", "to", "in", "a", "to be", "oneself", "not", "to have", "for", "with", "his", "for", "like", "to be", "to have", "him", "it", "all", "but", "more", "to do", "or", "can", "to say", "this", "to go", "other", "that", "if", "me", "already", "to see", "because", "to give", "when", "he", "very", "without", "time", "much", "to know", "what", "about", "my", "some", "same", "I", "also", "until", "year", "two", "to want", "between", "thus", "first", "from", "big", "that", "nor", "us", "own", "and", "afternoon", "while", "besides", "each", "less", "bear", "now", "example", "which", "only", "others", "part", "case", "nothing", "house", "before", "well", "form", "world", "still", "new", "thousand", "place", "city", "social", "fact", "time", "same", "she", "yes", "these", "so much", "how much", "life"]
COMMON = ["de", "la", "qu", "th", "he", "in", "er", "an", "re", "on", "at", "en", "es", "st", "nt", "to", "or", "al", "it", "as", "is", "hi", "be", "by", "ar", "te", "le", "se", "ou", "ve", "ra", "hi", "me", "ri", "ro", "co"]

def normalized_entropy_bytes(data: bytes) -> float:
    # Pre: A byte sequence
    # Post: Normalized entropy between 0 and 1 based on actual bytes.

    if not data:
        return 0.0
    # Count the frequency of each byte in the data
    freq = Counter(data)
    total = len(data)
    n_symbols = len(freq)

    if n_symbols == 1:
        return 0.0

    entropy = 0.0
    # Calculate the entropy using the formula: -sum(p * log2(p)) for each unique byte
    for count in freq.values():
        p = count / total
        entropy -= p * log2(p)

    max_entropy = log2(min(256, n_symbols))

    return entropy / max_entropy


def entropy_from_bitstring(seq: str) -> float:
    # Pre: A string of bits (e.g., "010101")
    # Post: Normalized entropy between 0 and 1 based on the byte representation of the bit string.
    data = bits_to_bytes(seq)
    return normalized_entropy_bytes(data)


def bytes_to_binary(text: bytes) -> str:
    # Pre: A byte sequence
    # Post: A string of bits representing the binary encoding of the byte sequence
    if not text:
        raise ValueError("There's no text to be encoded")    
    return ''.join(format(byte, '08b') for byte in text)

def bytes_to_text(data: bytes) -> str:
    # Pre: A byte sequence
    # Post: A UTF-8 decoded string, ignoring errors
    if not data:
        return ""

    try:
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""

def bits_to_bytes(seq: str) -> bytes:
    # Pre: A string of bits (e.g., "01010101")
    # Post: The byte sequence represented by the binary string
    data = bytearray()

    for i in range(0, len(seq) - 7, 8):
        byte = seq[i:i+8]
        data.append(int(byte, 2))

    return bytes(data)

def printable_ratio(text: str) -> float:
    # Pre: A string of text
    # Post: The ratio of printable characters to total characters, between 0 and 1
    if not text:
        return 0.0

    printable = sum(1 for c in text if c.isprintable())
    return printable / len(text)

def utf8_score(data: bytes) -> float:
    # Pre: A byte sequence
    # Post: 1.0 if the data can be decoded as UTF-8, otherwise 0.0
    try:
        data.decode("utf-8")
        return 1.0
    except:
        return 0.0

def dictionary_score(text: str) -> float:
    # Pre: A string of text
    # Post: A score between 0 and 1 based on the presence of common words in English and Spanish
    words = text.lower().split()

    if not words:
        return 0.0
    # Count the number of words that are in the English and Spanish dictionaries
    hits_es = sum(1 for w in words if w in DICC_ES)
    hits_en = sum(1 for w in words if w in DICC_EN)

    return (hits_en + hits_es) / len(words)

def ngram_score(text: str) -> float:
    # Pre: A string of text
    # Post: A score between 0 and 1 based on the presence of common bigrams in English and Spanish
    text = text.lower()
    # Count the number of common bigrams in the text
    hits = sum(text.count(g) for g in COMMON)

    return min(1.0, hits / 10)

def pipeline_medium(data: str) -> float:
    # Pre: A string of bits (e.g., "01010101")
    # Post: A confidence score between 0 and 1 based on a combination of heuristics

    raw = bits_to_bytes(data)
    text = bytes_to_text(raw)
    # Calculate the scores for each heuristic
    ratio_printable = printable_ratio(text)
    ratio_utf8 = utf8_score(raw)
    ratio_dicc = dictionary_score(text)
    ratio_ngram = ngram_score(text)

    confidence = (
        ratio_printable * 0.35 + 
        ratio_utf8 * 0.20 + 
        ratio_dicc * 0.25 +
        ratio_ngram * 0.20
    )

    return round(confidence,3)

def block_score(data: bytes) -> float:
    # Pre: A byte sequence
    # Post: A score between 0 and 1 based on the presence of block-like patterns (e.g., multiples of 8 or 16 bytes)
    if len(data) == 0:
        return 0.0

    if len(data) % 16 == 0:
        return 1.0
    elif len(data) % 8 == 0:
        return 0.5
    return 0.0

def uniformity_score(data: bytes) -> float:
    # Pre: A byte sequence
    # Post: A score between 0 and 1 based on the uniformity of byte
    if not data:
        return 0.0

    freq = Counter(data)
    total = len(data)
    # Calculate the maximum frequency ratio of any byte in the data
    max_ratio = max(v / total for v in freq.values())

    return max(0.0, 1.0 - max_ratio * 5)

def pipeline_high(data: str) -> float:
    # Pre: The width, height, and pixel data of an image
    # Post: A confidence score between 0 and 1 based on a combination of heuristics
    bytes = bits_to_bytes(data)

    ratio_block = block_score(bytes)
    ratio_uniformity = uniformity_score(bytes)
    # Calculate the final confidence score as a weighted average of the block and uniformity scores
    confidence = (
        ratio_block * 0.5 +
        ratio_uniformity * 0.5
    )

    return round(confidence, 3)

def get_message_sequence(reds: list, greens: list, blues: list) -> tuple:
    # Pre: Three lists of bits (0s and 1s) representing the least significant bits of the red, green, and blue channels of an image
    # Post: A tuple containing a global confidence score and a list of results for each channel
    n_pix = min(len(reds), len(greens), len(blues))

    seq_rgb = ""
    seq_bgr = ""
    seq_r = ""
    seq_g = ""
    seq_b = ""

    for i in range(n_pix):
        # Build the sequences for each channel and the combined RGB and BGR sequences
        seq_r += str(reds[i])
        seq_g += str(greens[i])
        seq_b += str(blues[i])

        seq_rgb += str(reds[i]) + str(greens[i]) + str(blues[i])
        seq_bgr += str(blues[i]) + str(greens[i]) + str(reds[i])

    ll_seq = [{"seq_r": seq_r}, {"seq_g": seq_g}, {"seq_b": seq_b}, {"seq_rgb": seq_rgb}, {"seq_bgr": seq_bgr}]
    results = []

    for item in ll_seq:
        name = list(item.keys())[0]
        seq = item[name]
        entropy = entropy_from_bitstring(seq)    
        confidence = 0
        # Depending on the entropy, choose the appropriate pipeline for confidence scoring
        if entropy <= 0.6:
            confidence = pipeline_medium(seq)
        else:
            confidence = pipeline_high(seq)

        results.append({
            "dataset": name,
            "entropy": entropy,
            "confidence": confidence
        })

    results.sort(key=lambda x: x["confidence"], reverse=True)
    # Select the best result based on confidence
    best = results[0]
    # Calculate the consensus score based on how many results have a confidence greater than 0.70
    consensus = sum(1 for r in results if r["confidence"] > 0.70)
    # Calculate the global confidence score as a weighted average of the best confidence and the consensus score
    global_conf = min(1.0, best["confidence"] + consensus * 0.05)

    return global_conf, results

def rs_score(width: int, height: int, pixels, group_size: int = 16) -> float:
    # Pre: The width, height, and pixel data of an image
    # Post: A tuple containing the RS score and the counts of regular, singular, and unusable groups
    def discrimination(group):
        return sum(
            abs(group[i] - group[i + 1])
            for i in range(len(group) - 1)
        )

    def flip_lsb(v):
        return v ^ 1

    # Initialize counters for regular, singular, and unusable groups
    regular = 0
    singular = 0
    unusable = 0

    # Iterate over each color channel (red, green, blue)
    for channel in range(3):

        values = []
        # Extract the pixel values for the current channel and store them in a list
        for y in range(height):
            for x in range(width):
                values.append(pixels[x, y][channel])

        # Dividir en grups de 4
        for i in range(0, len(values) - group_size + 1, group_size):

            group = values[i:i + group_size]

            if len(group) != group_size:
                continue
            # Calculate the discrimination value for the original group and the flipped group
            f = discrimination(group)

            flipped = [flip_lsb(v) for v in group]
            # Calculate the discrimination value for the flipped group
            fp = discrimination(flipped)

            if fp < f:
                regular += 1

            elif fp > f:
                singular += 1

            else:
                unusable += 1
    # Calculate the total number of groups and the RS score based on the counts of regular, singular, and unusable groups
    total = regular + singular + unusable

    if total == 0:
        return 0.0, 0, 0, 0

    # Calculate the ratios of regular and singular groups to the total number of groups
    r_ratio = regular / total
    s_ratio = singular / total

    # Com més semblants siguin R i S, més sospitosa és la imatge
    score = 1 - abs(r_ratio - s_ratio)

    return round(score, 3), regular, singular, unusable

def bit_length_variance_score(values: list) -> float:
    # Pre: A list of bits (0s and 1s)
    # Post: A score between 0 and 1 based on the variance of run lengths of bits in the list
    if len(values) < 2:
        return 0.0

    run_lengths = []

    current = values[0]
    length = 1
    # Iterate through the list of bits and calculate the run lengths of consecutive bits
    for bit in values[1:]:

        if bit == current:
            length += 1
        else:
            # Store the run length and reset for the next bit
            run_lengths.append(length)
            current = bit
            length = 1

    run_lengths.append(length)

    if len(run_lengths) < 2:
        return 0.0
    # Calculate the variance of the run lengths and compare it to an expected variance value for natural data
    var = variance(run_lengths)

    # EXPECTED_VARIANCE is a heuristic value that represents the expected variance of run lengths in natural data. A lower variance indicates more uniformity, which may suggest the presence of hidden data. The score is calculated as the absolute difference between the actual variance and the expected variance, normalized to a range of 0 to 1. 
    EXPECTED_VARIANCE = 1.9754
    # The score is capped at 1.0 to ensure it remains within the range of 0 to 1, and it is rounded to three decimal places for precision.
    score = min(1.0, abs(var - EXPECTED_VARIANCE) / EXPECTED_VARIANCE)

    return round(score, 3)

def detect_hidden_data(width: int, height: int, pixels) -> tuple:
    # Pre: The width, height, and pixel data of an image
    # Post: A tuple containing a global confidence score, results for row-wise and column-wise analysis, and the global chi-square score
    if not pixels:
        raise ValueError("There's no image to extract a message")
    if not width:
        raise ValueError("There's no width defined")
    if not height:
        raise ValueError("There's no height defined")
    
    # Initialize lists to store the least significant bits of each color channel for row-wise and column-wise analysis
    reds_row = []
    greens_row = []
    blues_row = []

    reds_col = []
    greens_col = []
    blues_col = []

    # Go through all the pixels
    for y in range(height):
        for x in range(width):
        # Split the pixel into its RGB components
        # Extract the least significant bit from each component
            r, g, b = pixels[x, y]
            reds_row.append(r & 1)
            greens_row.append(g & 1)
            blues_row.append(b & 1)

    for x in range(width):
        for y in range(height):
            # Split the pixel into its RGB components
            r, g, b = pixels[x, y]
            # Extract the least significant bit from each component
            reds_col.append(r & 1)
            greens_col.append(g & 1)
            blues_col.append(b & 1)

    # Analyze the sequences of least significant bits for both row-wise and column-wise data to detect potential hidden messages. The analysis involves calculating confidence scores based on various heuristics, including entropy, RS score, and bit length variance. The results are then combined to produce a global confidence score indicating the likelihood of hidden data in the image.
    conf_row, results_row = get_message_sequence(reds_row, greens_row, blues_row)
    conf_col, reuslts_col = get_message_sequence(reds_col, greens_col, blues_col)

    # Calculate the RS score and bit length variance for both row-wise and column-wise data to further assess the presence of hidden data. The RS score evaluates the regularity and singularity of pixel groups, while the bit length variance measures the variability in run lengths of bits. These metrics contribute to a comprehensive analysis of the image's potential steganographic content.
    rs_conf, r, s, u = rs_score(width, height, pixels)
    variance_r = bit_length_variance_score(reds_row)
    variance_g = bit_length_variance_score(greens_row)
    variance_b = bit_length_variance_score(blues_row)

    variance_score = round(
        (variance_r + variance_g + variance_b) / 3,
        3
    )

    payload_conf = max(conf_row, conf_col)
    # Combine the confidence scores from the payload analysis, RS score, and variance score to compute a global confidence score. The weights assigned to each component reflect their relative importance in determining the likelihood of hidden data. The final global confidence score is rounded to three decimal places for precision and returned along with the detailed results for row-wise and column-wise analysis.   
    global_conf = round(
        payload_conf * 0.1 +
        rs_conf * 0.6 +
        variance_score * 0.3,
        3
    )

    return global_conf, results_row, reuslts_col

def esteganalisysis_img(image: Image) -> tuple:
    # Pre: A PIL Image object
    # Post: A tuple containing a global confidence score, results for row-wise and column-wise analysis, and the global chi-square score
    if not image:
        raise ValueError(f"Image does not exist")

    try:
        img = image.convert("RGB")
    except UnidentifiedImageError:
        raise ValueError(f"Image is not a valid image")

    return analize_img(img)

def analize_img(img: Image) -> tuple:
    # Pre: A PIL Image object
    # Post: A tuple containing a global confidence score, results for row-wise and column-wise
    pixels = img.load()
    width, height = img.size

    global_conf, results_row, results_col = detect_hidden_data(
        width,
        height,
        pixels
    )

    return global_conf, results_row, results_col

def compute_stats(results):
    # Pre: A list of results, each containing a "confidence" key with a float value
    # Post: A tuple containing the average confidence and the number of results
    if not results:
        return 0, 0

    avg = sum(r["confidence"] for r in results) / len(results)
    return round(avg, 4), len(results)

def evaluate_folder(folder_path, label):
    # Pre: A folder path and a label (0 for clean, 1 for stego)
    # Post: A list of results for each image in the folder, including the file name
    results = []

    for file in os.listdir(folder_path):
        if not file.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            continue

        path = os.path.join(folder_path, file)
        print(f"Evaluating {file}...")
        try:
            # Load the image and convert it to RGB format for analysis
            img = Image.open(path).convert("RGB")

            global_conf, results_row, results_col = analize_img(img)
            # Append the results for the current image to the overall results list, including the file name, label, global confidence score, and detailed results for row-wise and column-wise analysis
            results.append({
                "file": file,
                "label": label,
                "confidence": global_conf,
                "row_results": results_row,
                "col_results": results_col
            })

        except Exception as e:
            print(f"[ERROR] {file}: {e}")

    return results

def main():
    clean_folder = os.path.join(root_path,"analisi_stega" ,"analisi_img","dataset", "clean_reduced")
    stego_folder = os.path.join(root_path, "analisi_stega" ,"analisi_img", "dataset", "stega")

    print("\n==============================")
    print("        Evaluar el model        ")
    print("==============================\n")

    # Evaluate the images in the clean and stego folders to obtain confidence scores and other relevant metrics for each image. The results are then combined to compute average confidence scores for both clean and stego images, allowing for a comparison of the model's performance in distinguishing between the two types of images.
    clean_results = evaluate_folder(clean_folder, 0)
    stego_results = evaluate_folder(stego_folder, 1)

    all_results = clean_results + stego_results

    # Compute average confidence scores and the number of images for both clean and stego images, providing insights into the model's ability to differentiate between the two categories based on the analysis of least significant bits, RS score, and bit length variance. The results are printed to the console for review.
    clean_avg, clean_n = compute_stats(clean_results)
    stego_avg, stego_n = compute_stats(stego_results)

    print(f"Imatges netes: {clean_n}")
    print(f"Imatges stego: {stego_n}\n")

    print(f"Confiança mitja (clean): {clean_avg}")
    print(f"Confiança mitja (stego): {stego_avg}\n")

    print("DIFERENCIA:")
    print(round(stego_avg - clean_avg, 4))

    print("\n==============================\n")

    if stego_avg > clean_avg:
        print("El model distingeix entre imatges netes i stego")
    else:
        print("No hi ha separació clara entre imatges netes i stego")

if __name__ == "__main__":
    main()
