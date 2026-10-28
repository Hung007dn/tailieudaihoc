import string
import random
import math

# --- Frequency Data from Provided Sources ---

# Bigram frequency data (as decimals)
bigram_data = {
    "TH": 0.0356,
    "HE": 0.0307,
    "IN": 0.0243,
    "ER": 0.0205,
    "AN": 0.0199,
    "RE": 0.0185,
    "ON": 0.0176,
    "AT": 0.0149,
    "EN": 0.0145,
    "ND": 0.0135,
    "TI": 0.0134,
    "ES": 0.0134,
    "OR": 0.0128,
    "TE": 0.0120,
    "OF": 0.0117,  # from "of 1.17%"
    "ED": 0.0117,
    "IS": 0.0113,
    "IT": 0.0112,
    "AL": 0.0109,
    "AR": 0.0107,
    "ST": 0.0105,
    "TO": 0.0105,
    "NT": 0.0104,
    "NG": 0.0095,
    "SE": 0.0093,
    "HA": 0.0093,
    "OU": 0.0087,
}

# Trigram frequency data (only those with provided percentages)
trigram_data = {
    "THE": 0.0181,
    "AND": 0.0073,
    "THA": 0.0033,
    "ENT": 0.0042,
    "ING": 0.0072,
    "ION": 0.0042,
    "TIO": 0.0031,
    "FOR": 0.0034,
    "OFT": 0.0022,
    "STH": 0.0021,
}

# --- Scorer Classes ---

class UnigramScorer:
    def __init__(self):
        self.freq = {
            "A": 8.17/100, "B": 1.49/100, "C": 2.78/100, "D": 4.25/100,
            "E": 12.70/100, "F": 2.23/100, "G": 2.02/100, "H": 6.09/100,
            "I": 6.97/100, "K": 0.77/100, "L": 4.03/100, "M": 2.41/100,
            "N": 6.75/100, "O": 7.51/100, "P": 1.93/100, "Q": 0.10/100,
            "R": 5.99/100, "S": 6.33/100, "T": 9.06/100, "U": 2.76/100,
            "V": 0.98/100, "W": 2.36/100, "X": 0.15/100, "Y": 1.97/100,
            "Z": 0.07/100
        }
        self.log_probs = {letter: math.log10(self.freq[letter]) for letter in self.freq}
    
    def score(self, text):
        score = 0
        text = text.upper()
        for char in text:
            if char in self.log_probs:
                score += self.log_probs[char]
            else:
                score += math.log10(0.01)  # penalty for unknown
        return score

class BigramScorer:
    def __init__(self, data):
        self.bigrams = data
        total = sum(data.values())
        self.total = total
        self.log_probs = {bg: math.log10(freq/total) for bg, freq in data.items()}
        self.floor = math.log10(0.01/total)
    
    def score(self, text):
        score = 0
        text = text.upper()
        for i in range(len(text)-1):
            bg = text[i:i+2]
            score += self.log_probs.get(bg, self.floor)
        return score

class TrigramScorer:
    def __init__(self, data):
        self.trigrams = data
        total = sum(data.values())
        self.total = total
        self.log_probs = {tg: math.log10(freq/total) for tg, freq in data.items()}
        self.floor = math.log10(0.01/total)
    
    def score(self, text):
        score = 0
        text = text.upper()
        for i in range(len(text)-2):
            tg = text[i:i+3]
            score += self.log_probs.get(tg, self.floor)
        return score

class CombinedScorer:
    def __init__(self, alpha=1.0, beta=0.5, gamma=0.5):
        """
        alpha: weight for trigram score.
        beta: weight for bigram score.
        gamma: weight for unigram score.
        """
        self.uni = UnigramScorer()
        self.bi = BigramScorer(bigram_data)
        self.tri = TrigramScorer(trigram_data)
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
    
    def score(self, text):
        return (self.alpha * self.tri.score(text) +
                self.beta * self.bi.score(text) +
                self.gamma * self.uni.score(text))

# --- Playfair Decryption & Key Handling ---

def key_to_square(key_str):
    """
    Converts a 25-letter key string (with J omitted) into a 5x5 matrix.
    """
    return [list(key_str[i*5:(i+1)*5]) for i in range(5)]

def print_key_matrix(matrix):
    """
    Prints the 5x5 key matrix in a formatted manner.
    """
    for row in matrix:
        print(" ".join(row))

def playfair_decrypt(ciphertext, key_square):
    """
    Decrypts ciphertext using the Playfair cipher with the given key square.
    Assumes ciphertext is a continuous string of uppercase letters (no spaces).
    """
    pos = {}
    for r in range(5):
        for c in range(5):
            pos[key_square[r][c]] = (r, c)
    digraphs = [ciphertext[i:i+2] for i in range(0, len(ciphertext), 2)]
    plaintext = ""
    for pair in digraphs:
        a, b = pair[0], pair[1]
        row1, col1 = pos[a]
        row2, col2 = pos[b]
        if row1 == row2:
            plaintext += key_square[row1][(col1-1)%5]
            plaintext += key_square[row2][(col2-1)%5]
        elif col1 == col2:
            plaintext += key_square[(row1-1)%5][col1]
            plaintext += key_square[(row2-1)%5][col2]
        else:
            plaintext += key_square[row1][col2]
            plaintext += key_square[row2][col1]
    return plaintext

def random_key_string():
    """
    Returns a random 25-letter key string (with J omitted) for Playfair.
    """
    letters = list("ABCDEFGHIKLMNOPQRSTUVWXYZ")
    random.shuffle(letters)
    return "".join(letters)

def swap_two_letters(key_str):
    """
    Returns a new key string by swapping two random letters.
    """
    lst = list(key_str)
    i, j = random.sample(range(len(lst)), 2)
    lst[i], lst[j] = lst[j], lst[i]
    return "".join(lst)

# --- Hill Climbing for Playfair Cryptanalysis Using a Keyword-Style Key ---

def build_key(keyword_candidate):
    """
    Given a candidate keyword (e.g., 8 letters), builds the full 25-letter key.
    The candidate keyword is processed by removing duplicates (preserving order),
    then the remaining letters (in alphabetical order) are appended.
    """
    keyword_candidate = "".join(dict.fromkeys(keyword_candidate.upper()))
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # J omitted
    remainder = "".join(sorted(set(alphabet) - set(keyword_candidate)))
    return keyword_candidate + remainder

def hill_climb(ciphertext, scorer, iterations=20000, keyword_length=7):
    """
    Uses hill climbing to search for the best candidate keyword (of fixed length)
    that, when used to build the full key, maximizes the combined fitness score.
    """
    alphabet = "ABCDEFGHIKLMNOPQRSTUVWXYZ"
    candidate_keyword = "".join(random.sample(alphabet, keyword_length))
    best_candidate = candidate_keyword
    best_full_key = build_key(candidate_keyword)
    best_square = key_to_square(best_full_key)
    best_decryption = playfair_decrypt(ciphertext, best_square)
    best_score = scorer.score(best_decryption)
    current_candidate = candidate_keyword
    current_score = best_score
    
    for _ in range(iterations):
        candidate_modified = swap_two_letters(current_candidate)
        candidate_full = build_key(candidate_modified)
        candidate_square = key_to_square(candidate_full)
        candidate_decryption = playfair_decrypt(ciphertext, candidate_square)
        candidate_score = scorer.score(candidate_decryption)
        if candidate_score > current_score:
            current_candidate = candidate_modified
            current_score = candidate_score
            if candidate_score > best_score:
                best_candidate = candidate_modified
                best_score = candidate_score
    best_full_key = build_key(best_candidate)
    best_square = key_to_square(best_full_key)
    best_decryption = playfair_decrypt(ciphertext, best_square)
    return best_candidate, best_full_key, best_score, best_decryption

def playfair_cryptanalysis(ciphertext):
    scorer = CombinedScorer(alpha=1.0, beta=0.5, gamma=0.5)
    best_candidate, best_full_key, best_score, best_decryption = hill_climb(ciphertext, scorer, iterations=200000, keyword_length=7)
    return best_candidate, best_full_key, best_score, best_decryption

# --- Main Function ---

def main():
    print("Playfair Cryptanalysis with Combined Unigram, Bigram, and Trigram Scoring")
    print("Note: Ciphertext should be a continuous string of uppercase letters (no spaces).")
    ciphertext = input("Enter the ciphertext: ").strip()
    best_candidate, best_full_key, best_score, best_decryption = playfair_cryptanalysis(ciphertext)
    
    print("\nBest Candidate Keyword (the keyword portion):")
    print(best_candidate)
    print("\nFull Key (25-letter string, built from the candidate keyword):")
    print(best_full_key)
    print("\nFull Key as 5x5 Matrix:")
    best_key_square = key_to_square(best_full_key)
    print_key_matrix(best_key_square)
    print("\nDecrypted Text:")
    print(best_decryption)
    print("\nScore:", best_score)

if __name__ == "__main__":
    main()
