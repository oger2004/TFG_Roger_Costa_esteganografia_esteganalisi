import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(root_path)

from collections import Counter
import statistics
import numpy as np
from PIL import Image
import io
import fitz
import imagehash
import itertools
from analisi_img.analisi_img import esteganalisysis_img
from analisi_txt.analisi_txt import esteganalisysis_txt

PAGE_MEDIA = (0, 0, 595.28, 841.89)  # A4 size

def intersection_area(a, b):
    # Pre: a and b are tuples of the form (x0, y0, x1, y1)
    # Post: returns the area of intersection of the two rectangles defined by a and b
    x0 = max(a[0], b[0])
    y0 = max(a[1], b[1])
    x1 = min(a[2], b[2])
    y1 = min(a[3], b[3])

    if x1 <= x0 or y1 <= y0:
        return 0

    return (x1 - x0) * (y1 - y0)


def outside_score_aux(img_area, visible_area):
    # Pre: img_area and visible_area are positive numbers
    # Post: returns a score between 0 and 1, where 0 means the image is fully visible and 1 means the image is fully outside the page
    visible_ratio = visible_area / img_area

    score = 1.0 - visible_ratio

    return max(0.0, min(score, 1.0))

def outside_score(images, positions):
    # Pre: images is a list of PIL Images, positions is a list of tuples of the form (x0, y0, x1, y1)
    # Post: returns a score between 0 and 1, where 0 means all images are fully visible and 1 means all images are fully outside the page
    if not images:
        return 1.0

    scores = []
    for img, pos in zip(images, positions):
        # Compute the area of the image
        img_area = (pos[2] - pos[0]) * (pos[3] - pos[1])
        # Compute the intersection area between the image position and the page media box
        visible_area = intersection_area(
            pos,
            PAGE_MEDIA
        )

        score = outside_score_aux(img_area, visible_area)
        scores.append(score)

    return np.mean(scores)

def duplicate_score_aux(distance, max_distance=64):
    # Pre: distance is a non-negative number, max_distance is a positive number
    # Post: returns a score between 0 and 1, where 0 means the images are identical and 1 means the images are completely different
    similarity = 1 - (distance / max_distance)
    return max(0.0, min(similarity, 1.0))


def duplicate_score(images):
    # Pre: images is a list of PIL Images
    # Post: returns a score between 0 and 1, where 0 means all images are identical and 1 means all images are completely different

    if len(images) <= 1:
        return 0.0
    # Compute the perceptual hash for each image
    hashes = [
        # Compute the average hash for each image
        imagehash.average_hash(img.convert("L"))
        for img in images
    ]

    scores = []
    # Compute the pairwise distances between the hashes and compute the duplicate score for each pair
    for h1, h2 in itertools.combinations(hashes, 2):
        distance = h1 - h2
        scores.append(duplicate_score_aux(distance))

    return np.max(scores)

def color_score_aux(img):
    # Pre: img is a PIL Image
    # Post: returns a score between 0 and 1, where 0 means the image has a lot of color variability and 1 means the image is almost a single color

    rgb = np.asarray(img.convert("RGB"), dtype=np.float32)

    std = np.std(rgb.reshape(-1, 3), axis=0)

    mean_std = np.mean(std)
    # The maximum standard deviation 
    score = 1 - min(mean_std / 80.0, 1.0)

    return score

def color_score(images):
    # Pre: images is a list of PIL Images
    # Post: returns a score between 0 and 1, where 0 means the
    if not images:
        return 0

    scores = [color_score_aux(img) for img in images]

    # Las imágenes artificiales interesan más que la media
    return max(scores)

def invisibles_score_aux(image):
    # Pre: image is a PIL Image
    # Post: returns a score between 0 and 1, where 0 means the
    alpha = np.array(image.split()[-1])
    invisible_pixels = np.sum(alpha <= 3)
    total_pixels = alpha.size

    if total_pixels == 0:
        return 1.0

    density_invisible = invisible_pixels / total_pixels

    return density_invisible

def invisibles_score(images):
    # Pre: images is a list of PIL Images
    # Post: returns a score between 0 and 1, where 0 means the
    
    if not images:
        return 0

    scores = []
    # Compute the invisibles score for each image and return the mean
    for img in images:
        # Compute the invisibles score for each image
        score = invisibles_score_aux(img)
        if score > 0.95:
            return score
        scores.append(score)

    return np.mean(scores)

def extract_images(page):
    # Pre: page is a fitz.Page object
    # Post: returns a tuple of two lists: the first list contains the positions of the images in the page, and the second list contains the PIL Images
    images = []
    positions = []
    # Iterate over the images in the page and extract their positions and PIL Images
    for img in page.get_images(full=True):
        xref = img[0]
        # Extract the image bytes and convert them to a PIL Image
        base_image = page.parent.extract_image(xref)
        img_bytes = base_image["image"]
        # Convert the image bytes to a PIL Image and convert it to RGBA mode
        image = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
        images.append(image)

        bbox = page.get_image_bbox(img)
        positions.append((bbox.x0, bbox.y0, bbox.x1, bbox.y1))

    return positions, images


def image_esteganalisy_score(images):
    # Pre: images is a list of PIL Images
    # Post: returns a score between 0 and 1, where 0 means the images are not steganographic and 1 means the images are steganographic

    if not images:
        return 0

    scores = []
    # Compute the esteganalisy score for each image and return the mean
    for img in images:
        conf, _, _ = esteganalisysis_img(img)
        scores.append(conf)
        

    return np.mean(scores)

def text_esteganalisy_score(texts):
    # Pre: texts is a list of strings
    # Post: returns a score between 0 and 1, where 0 means the
    if not texts:
        return 0

    scores = []
    # Compute the esteganalisy score for each text and return the mean
    for text in texts:
        score, *_ = esteganalisysis_txt(text)
        scores.append(
            score
        )

    return np.mean(scores)

def consensus_bonus(values, base_score, threshold=0.75, bonus=0.10):
    # Pre: values is a list of floats, base_score is a float, threshold is a float, bonus is a float
    # Post: returns a float between 0 and 1, where 0 means the
    positives = sum(v >= threshold for v in values)

    if positives >= 2:
        return min(base_score + bonus, 1.0)

    return base_score

def analize_file(path):
    # Pre: path is a string representing the path to a PDF file
    # Post: returns a tuple of seven floats: the first float is the overall score, the second float is the outside score, the third float is the duplicate score, the fourth float is the color score, the fifth float is the invisibles score, the sixth float is the image esteganalisy score, and the seventh float is the text esteganalisy score
    doc = fitz.open(path)

    images = []
    positions = []
    texts = []

    # Iterate over the pages in the PDF and extract the images, positions, and texts
    for page in doc:
        p, i = extract_images(page)
        e = page.get_text("text")
        positions.extend(p)
        texts.append(e)
        images.extend(i)

    if not images and not positions and not texts:
        return 0,0,0,0,0,0
    # Compute the scores for the images and texts
    outside = outside_score(images, positions)
    duplicate = duplicate_score(images)
    color = color_score(images)
    invisibles = invisibles_score(images)

    image_esteganalisy = image_esteganalisy_score(images)
    text_esteganalisy = text_esteganalisy_score(texts) / 100
    # Compute the overall score as a weighted sum of the individual scores
    image_score = (
        0.50 * duplicate +
        0.30 * color +
        0.20 * image_esteganalisy
    )
    # Compute the overall score as a weighted sum of the individual scores
    pdf_score = (
        0.50 * outside +
        0.50 * invisibles
    )
    # Compute the overall score as a weighted sum of the individual scores
    text_score = text_esteganalisy
    
    scores = []
    # Compute the overall score as a weighted sum of the individual scores
    scores.append(image_score)
    scores.append(pdf_score)
    scores.append(text_score)

    score = np.max(scores)
    # Apply a consensus bonus if at least two of the scores are above the threshold
    return (
        score,
        outside,
        duplicate,
        color,
        invisibles,
        image_esteganalisy,
        text_esteganalisy
    )

def process_folder(folder):
    results = []
    # Iterate over the files in the folder and analyze each PDF file
    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        if not os.path.isfile(path):
            continue

        r = analize_file(path)
        # Unpack the results of the analysis into individual variables
        score = r[0]
        outside = r[1]
        duplicate = r[2]
        color = r[3]
        invisibles = r[4]
        image_esteganalisy = r[5]
        text_esteganalisy = r[6]
        # Append the results to the list
        results.append({
            "score": score,
            "outside": outside,
            "duplicate": duplicate,
            "color": color,
            "invisibles": invisibles,
            "image_esteganalisy": image_esteganalisy,
            "text_esteganalisy": text_esteganalisy
        })

    return results

def median(values, key):
    return statistics.median([v[key] for v in values])


def main():

    clean_folder = os.path.join(root_path,"analisi_pdf","dataset", "clean")
    stega_folder = os.path.join(root_path, "analisi_pdf", "dataset", "stega")

    stega_results = []
    clean_results = []
    # Process the stega and clean folders and compute the median scores for each metric
    stega_results = process_folder(stega_folder)
    clean_results = process_folder(clean_folder)

    print("================== STEGA ==================")
    print(f"Score: {median(stega_results,'score'):.2f}")
    print(f"Outside: {median(stega_results,'outside'):.4f}")
    print(f"Duplicate: {median(stega_results,'duplicate'):.4f}")
    print(f"Color: {median(stega_results,'color'):.4f}")
    print(f"Invisibles: {median(stega_results,'invisibles'):.4f}")
    print(f"Image Esteganalisy: {median(stega_results,'image_esteganalisy'):.4f}")
    print(f"Text Esteganalisy: {median(stega_results,'text_esteganalisy'):.4f}")

    print()

    print("================== CLEAN ==================")
    print(f"Score: {median(clean_results,'score'):.2f}")
    print(f"Outside: {median(clean_results,'outside'):.4f}")
    print(f"Duplicate: {median(clean_results,'duplicate'):.4f}")
    print(f"Color: {median(clean_results,'color'):.4f}")
    print(f"Invisibles: {median(clean_results,'invisibles'):.4f}")
    print(f"Image Esteganalisy: {median(clean_results,'image_esteganalisy'):.4f}")
    print(f"Text Esteganalisy: {median(clean_results,'text_esteganalisy'):.4f}")

    print("\n========== (STEGA - CLEAN) ==========")
    print(f"Delta score: {median(stega_results,'score') - median(clean_results,'score'):.2f}")


main()