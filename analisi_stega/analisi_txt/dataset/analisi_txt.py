from collections import Counter
import statistics
from math import log2

import os
import sys

root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(root_path)

# Most common invisible characters and their descriptions
INVISIBLE_CHARS = {
    "\u200b": "ZERO WIDTH SPACE",
    "\u200c": "ZERO WIDTH NON-JOINER",
    "\u200d": "ZERO WIDTH JOINER",
    "\u2060": "WORD JOINER",
    "\ufeff": "ZERO WIDTH NO-BREAK SPACE",
    "\u180e": "MONGOLIAN VOWEL SEPARATOR",
    "\u00ad": "SOFT HYPHEN"
}

def invisible_char_detection(text):
    # Pre: text is a string
    # Post: returns a list of positions of invisible characters in the text and a list of the found invisible characters
    positions = []
    found = []

    for i, c in enumerate(text):
        # Check if the character is in the set of invisible characters
        if c in INVISIBLE_CHARS:
            positions.append(i)
            found.append(c)

    return positions, found

def normalize_density(d):
    # Pre: d is a float representing the density of invisible characters
    # Post: returns a normalized score between 0 and 1 based on the density
    return min(d / 0.01, 1)

def evaluate_entropy(text):
    # Pre: text is a string
    # Post: returns the entropy of the text based on the frequency of characters
    frec = Counter(text)
    total = len(text)

    entropy = 0
    # Calculate the entropy using the formula: -sum(p * log2(p)) for each character's probability p
    for c in frec.values():
        p = c / total
        entropy -= p * log2(p)

    return entropy

def normalize_entropy(h):
    # Pre: h is a float representing the entropy of the text
    # Post: returns a normalized score between 0 and 1 based on the entropy
    return min(max((h - 3.5) / (5.0 - 3.5), 0), 1)

def analize_periodicity(positions):
    # Pre: positions is a list of integers representing the positions of invisible characters
    # Post: returns a score between 0 and 1 based on the periodicity of
    if len(positions) < 2:
        return 0
    # Calculate the distances between consecutive positions of invisible characters
    dist = [positions[i+1] - positions[i] for i in range(len(positions)-1)]
    m = statistics.mean(dist)
    # Calculate the standard deviation of the distances and normalize it to get a periodicity score
    desv = statistics.pstdev(dist)
    # Ensure the periodicity score is between 0 and 1
    return max(0, min(1, 1 - (desv / m)))


def evaluate_consistency(features):
    # Pre: features is a list of floats representing different feature scores
    # Post: returns a consistency score between 0 and 1 based on the standard deviation
    mean = sum(features) / len(features)
    std = statistics.pstdev(features)

    epsilon = 1e-6
    # Calculate the consistency score as 1 minus the normalized standard deviation
    consistency = 1 - (std / (mean + epsilon))
    # Ensure the consistency score is between 0 and 1
    return max(0, min(1, consistency))

def analize_file(text):
    # Pre: text is a string representing the content of a text file
    # Post: returns a tuple containing the final score, consistency, and individual feature scores

    total_chars = len(text)
    # Detect invisible characters in the text and get their positions and the characters themselves
    positions, invisibles = invisible_char_detection(text)
    # Calculate the entropy of the text
    entropy = evaluate_entropy(text)
    # Calculate the density of invisible characters in the text
    densidad = len(invisibles) / total_chars if total_chars > 0 else 0
    # Normalize the density, entropy, and periodicity scores
    invisibles_score = normalize_density(densidad)
    # Calculate the periodicity score based on the positions of invisible characters
    entropy_score = normalize_entropy(entropy)
    # Calculate the periodicity score based on the positions of invisible characters
    periodicity_score = analize_periodicity(positions)

    # Calculate the final score as a weighted sum of the individual scores
    score = (
        0.5 * invisibles_score +
        0.2 * entropy_score +
        0.3 * periodicity_score
    )
    # Calculate the contributions of each feature to the final score
    contributions = [
        0.5 * invisibles_score,
        0.2 * entropy_score,
        0.3 * periodicity_score
    ]
    # Calculate the consistency of the contributions to the final score
    consistency = evaluate_consistency(contributions)

    return score *100, consistency, invisibles_score, entropy_score, periodicity_score

def process_folder(folder):
    # Pre: folder is a string representing the path to a folder containing text files
    # Post: returns a list of dictionaries containing the analysis results for each text file in the folder

    results = []

    for file in os.listdir(folder):
        path = os.path.join(folder, file)

        if not os.path.isfile(path):
            continue

        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        
        r = analize_file(text)
        # Unpack the results from the analysis
        score = r[0]
        consistency = r[1]
        invisibles = r[2]
        entropy = r[3]
        periodicity = r[4]
        # Append the scores into results
        results.append({
            "score": score,
            "consistency": consistency,
            "invisibles": invisibles,
            "entropy": entropy,
            "periodicity": periodicity
        })

    return results

def median(values, key):
    return statistics.median([v[key] for v in values])

def esteganalisysis_txt(text: str) -> tuple:

    return analize_file(text)

def main():

    clean_folder = os.path.join(root_path,"analisi_stega" ,"analisi_txt","dataset", "clean")
    stega_folder = os.path.join(root_path, "analisi_stega" ,"analisi_txt", "dataset", "stega")

    stega_results = []
    clean_results = []

    stega_results = process_folder(stega_folder)
    clean_results = process_folder(clean_folder)

    print("================== STEGA ==================")
    print(f"Score: {median(stega_results, 'score'):.2f}")
    print(f"Consistencia: {median(stega_results, 'consistency'):.4f}")
    print(f"Invisibles: {median(stega_results, 'invisibles'):.6f}")
    print(f"Entropia: {median(stega_results, 'entropy'):.4f}")
    print(f"Periodicidad: {median(stega_results, 'periodicity'):.4f}")

    print("\n================== CLEAN ==================")
    print(f"Score: {median(clean_results, 'score'):.2f}")
    print(f"Consistencia: {median(clean_results, 'consistency'):.4f}")
    print(f"Invisibles: {median(clean_results, 'invisibles'):.6f}")
    print(f"Entropia: {median(clean_results, 'entropy'):.4f}")
    print(f"Periodicidad: {median(clean_results, 'periodicity'):.4f}")

    print("\n========== (STEGA - CLEAN) ==========")
    print(f"Delta score: {median(stega_results,'score') - median(clean_results,'score'):.2f}")

if __name__ == "__main__":
    main()