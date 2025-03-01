""" 
Holds various variables and functions that details the sepcifications of QR code versions and Error-Correction Level 
"""

# Example nested dictionary with QR code capacities for each version.
# Outer keys: QR versions
# Second-level keys: error correction levels ('L', 'M', 'Q', 'H')
# Third-level keys: encoding modes (e.g., 'numeric', 'alphanumeric', 'byte', 'kanji')
qr_capacities = {
    1: {
        'L': {'numeric': 41, 'alphanumeric': 25, 'byte': 17, 'kanji': 10},
        'M': {'numeric': 34, 'alphanumeric': 20, 'byte': 14, 'kanji': 8},
        'Q': {'numeric': 27, 'alphanumeric': 16, 'byte': 11, 'kanji': 7},
        'H': {'numeric': 17, 'alphanumeric': 10, 'byte': 7, 'kanji': 4}
    },
    2: {
        'L': {'numeric': 77, 'alphanumeric': 47, 'byte': 32, 'kanji': 20},
        'M': {'numeric': 63, 'alphanumeric': 38, 'byte': 26, 'kanji': 16},
        'Q': {'numeric': 48, 'alphanumeric': 29, 'byte': 20, 'kanji': 12},
        'H': {'numeric': 34, 'alphanumeric': 20, 'byte': 14, 'kanji': 8}
    },
    3: {
        'L': {'numeric': 127, 'alphanumeric': 77, 'byte': 53, 'kanji': 32},
        'M': {'numeric': 101, 'alphanumeric': 61, 'byte': 42, 'kanji': 26},
        'Q': {'numeric': 77, 'alphanumeric': 47, 'byte': 32, 'kanji': 20},
        'H': {'numeric': 58, 'alphanumeric': 35, 'byte': 24, 'kanji': 15}
    },
    4: {
        'L': {'numeric': 187, 'alphanumeric': 114, 'byte': 78, 'kanji': 48},
        'M': {'numeric': 149, 'alphanumeric': 90, 'byte': 62, 'kanji': 38},
        'Q': {'numeric': 111, 'alphanumeric': 67, 'byte': 46, 'kanji': 28},
        'H': {'numeric': 82, 'alphanumeric': 50, 'byte': 34, 'kanji': 21}
    },
    5: {
        'L': {'numeric': 255, 'alphanumeric': 154, 'byte': 106, 'kanji': 65},
        'M': {'numeric': 202, 'alphanumeric': 122, 'byte': 84, 'kanji': 52},
        'Q': {'numeric': 144, 'alphanumeric': 87, 'byte': 60, 'kanji': 37},
        'H': {'numeric': 106, 'alphanumeric': 64, 'byte': 44, 'kanji': 27}
    },
    6: {
        'L': {'numeric': 322, 'alphanumeric': 195, 'byte': 134, 'kanji': 82},
        'M': {'numeric': 255, 'alphanumeric': 154, 'byte': 106, 'kanji': 65},
        'Q': {'numeric': 178, 'alphanumeric': 108, 'byte': 74, 'kanji': 45},
        'H': {'numeric': 139, 'alphanumeric': 84, 'byte': 58, 'kanji': 36}
    },
    7: {
        'L': {'numeric': 370, 'alphanumeric': 224, 'byte': 154, 'kanji': 95},
        'M': {'numeric': 293, 'alphanumeric': 178, 'byte': 122, 'kanji': 75},
        'Q': {'numeric': 207, 'alphanumeric': 125, 'byte': 86, 'kanji': 53},
        'H': {'numeric': 154, 'alphanumeric': 93, 'byte': 64, 'kanji': 39}
    },
}

def smallest_version(input_string: str, error_correction: str, mode: str):
    """ Determine the smallest version of QR code based on error-correction level and character capacity.
    Capacity of QR code is determined by how many characters it can hold at max.
    It is different for different modes for each QR code version and error-correction level.  \n
    For example, the phrase HELLO WORLD has 11 characters. 
    If encoding it with level Q error correction, the character capacities table says that a version 1 code 
    using level Q error correction can contain 16 characters in **alphanumeric mode**, 
    so version 1 is the smallest version that can contain this number of characters.

    If the phrase were longer than 16 characters, such as HELLO THERE WORLD (which is 17 characters)
    version 2 would be the smallest version."""
    

    # The string we want to encode
    # data_str = "Hello, world!"

    # For byte mode, each character is considered 1 byte (if in ASCII).
    required_length = len(input_string)

    # Specify the error correction level and mode you are using.
    # error_correction = 'M'
    # mode = 'byte'

    # Initialize a variable to store the selected QR version.
    selected_version = None

    # Iterate through the QR versions in order (from smallest to largest).
    for version in sorted(qr_capacities.keys()):
        # Get the capacity for the given error correction level and mode.
        capacity = qr_capacities[version][error_correction][mode]
        # Debug print to see what capacity we're checking (optional)
        # print(f"Version {version} capacity for {mode} mode at {error_correction} is: {capacity}")
        
        # Check if the required length of our data fits in the current version.
        if required_length <= capacity:
            selected_version = version  # Found the smallest version that fits
            break  # No need to check higher versions

    if selected_version is not None:
        print("Smallest QR version that can encode the data is:", selected_version)
        return selected_version
    else:
        print("No suitable QR version found for the given data.")

def error_correction_table() -> dict:
    """ Dictionary of Error-correction codewords needed and number of Groups and Blocks to split data (as Integer) into.\n
    At this point, the original string to be encoded should have gone through the following process:  
    Original -> 8-bit binary -> Add mode and len(original) -> Add 0 and pad bytes until len(string) % 8 == 0 
      -> Group into 8-bit binary -> Integer (NOTE: these are the **Data codewords**!)
    """
    # ECC means Error-Correction Codewords
    ver_and_ec_level = {
        1: {
            "L": {
                    "ECC per block": 7, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 19, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "M": {
                    "ECC per block": 10, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 16, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "Q": {
                    "ECC per block": 13, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 13, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "H": {
                    "ECC per block": 17, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 9, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0}
        },
        2: {
            "L": {
                    "ECC per block": 10, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 34, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "M": {
                    "ECC per block": 16, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 28, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "Q": {
                    "ECC per block": 22, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 22, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "H": {
                    "ECC per block": 28, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 16, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0}
        },
        3: {
            "L": {
                    "ECC per block": 15, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 55, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "M": {
                    "ECC per block": 26, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 44, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "Q": {
                    "ECC per block": 18, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 17, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "H": {
                    "ECC per block": 22, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 13, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0}
        },
        4: {
            "L": {
                    "ECC per block": 20, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 80, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "M": {
                    "ECC per block": 18, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 32, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "Q": {
                    "ECC per block": 26, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 24, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "H": {
                    "ECC per block": 16, "Blocks in Group 1": 4, "Data codewords per Block in Group 1": 9, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0}
        },
        5: {
            "L": {
                    "ECC per block": 26, "Blocks in Group 1": 1, "Data codewords per Block in Group 1": 108, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "M": {
                    "ECC per block": 24, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 43, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "Q": {
                    "ECC per block": 18, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 15, 
                    "Blocks in Group 2": 2, "Data codewords per Block in Group 2": 16},
            "H": {
                    "ECC per block": 22, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 11, 
                    "Blocks in Group 2": 2, "Data codewords per Block in Group 2": 12}
        },
        6: {
            "L": {
                    "ECC per block": 18, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 68, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "M": {
                    "ECC per block": 16, "Blocks in Group 1": 4, "Data codewords per Block in Group 1": 27, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "Q": {
                    "ECC per block": 24, "Blocks in Group 1": 4, "Data codewords per Block in Group 1": 19, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "H": {
                    "ECC per block": 28, "Blocks in Group 1": 4, "Data codewords per Block in Group 1": 15, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0}
        },
        7: {
            "L": {
                    "ECC per block": 20, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 78, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "M": {
                    "ECC per block": 18, "Blocks in Group 1": 4, "Data codewords per Block in Group 1": 31, 
                    "Blocks in Group 2": 0, "Data codewords per Block in Group 2": 0},
            "Q": {
                    "ECC per block": 18, "Blocks in Group 1": 2, "Data codewords per Block in Group 1": 14, 
                    "Blocks in Group 2": 4, "Data codewords per Block in Group 2": 15},
            "H": {
                    "ECC per block": 26, "Blocks in Group 1": 4, "Data codewords per Block in Group 1": 13, 
                    "Blocks in Group 2": 1, "Data codewords per Block in Group 2": 14}
        }, 
        # NOTE: To be continued...
    }

    return ver_and_ec_level


alignment_coordinates = {
    2: (6, 18),
    3: (6, 22),
    4: (6, 26),
    5: (6, 30),
    6: (6, 34),
    7: (6, 22, 38),
    8: (6, 24, 42),
    9: (6, 26, 46),
    10: (6, 28, 50),
    11: (6, 30, 54),
    12: (6, 32, 58),
    13: (6, 34, 62),
    14: (6, 26, 46, 66),
    15: (6, 26, 48, 70),
    16: (6, 26, 50, 74),
    17: (6, 30, 54, 78),
    18: (6, 30, 56, 82),
    19: (6, 30, 58, 86),
    20: (6, 34, 62, 90),
    21: (6, 28, 50, 72),
    22: (6, 26, 50, 74),
    23: (6, 30, 54, 78, 102),
    24: (6, 28, 54, 80, 106),
    25: (6, 32, 58, 84, 110),
    26: (6, 30, 58, 86, 114),
    27: (6, 34, 62, 90, 118),
    28: (6, 26, 50, 74, 98, 122),
    29: (6, 30, 54, 78, 102, 126),
    30: (6, 26, 52, 78, 104, 130),
    31: (6, 30, 56, 82, 108, 134),
    32: (6, 34, 60, 86, 112, 138),
    33: (6, 30, 58, 86, 114, 142),
    34: (6, 34, 62, 90, 118, 146),
    35: (6, 30, 54, 78, 102, 126, 150),
    36: (6, 24, 50, 76, 102, 128, 154),
    37: (6, 28, 54, 80, 106, 132, 158),
    38: (6, 32, 58, 84, 110, 136, 162),
    39: (6, 26, 54, 82, 110, 138, 166),
    40: (6, 30, 58, 86, 114, 142, 170),
}

format_string_dict = {
    "L": {
        0: "111011111000100",
        1: "111001011110011",
        2: "111110110101010",
        3: "111100010011101",
        4: "110011000101111",
        5: "110001100011000",
        6: "110110001000001",
        7: "110100101110110"},
    "M": {
            0: "101010000010010",
            1: "101000100100101",
            2: "101111001111100",
            3: "101101101001011",
            4: "100010111111001",
            5: "100000011001110",
            6: "100111110010111",
            7: "100101010100000"
        },
    "Q": {
            0: "011010101011111",
            1: "011000001101000",
            2: "011111100110001",
            3: "011101000000110",
            4: "010010010110100",
            5: "010000110000011",
            6: "010111011011010",
            7: "010101111101101"
        },
    "H": {
            0: "001011010001001",
            1: "001001110111110",
            2: "001110011100111",
            3: "001100111010000",
            4: "000011101100010",
            5: "000001001010101",
            6: "000110100001100",
            7: "000100000111011"
        }
}

version_information_string = {
    7: "000111110010010100", 
    8: "001000010110111100", 
    9: "001001101010011001", 
    10: "001010010011010011", 
    11: "001011101111110110", 
    12: "001100011101100010", 
    13: "001101100001000111", 
    14: "001110011000001101", 
    15: "001111100100101000", 
    16: "010000101101111000", 
    17: "010001010001011101", 
    18: "010010101000010111", 
    19: "010011010100110010", 
    20: "010100100110100110", 
    21: "010101011010000011", 
    22: "010110100011001001", 
    23: "010111011111101100", 
    24: "011000111011000100", 
    25: "011001000111100001", 
    26: "011010111110101011", 
    27: "011011000010001110", 
    28: "011100110000011010", 
    29: "011101001100111111", 
    30: "011110110101110101", 
    31: "011111001001010000", 
    32: "100000100111010101", 
    33: "100001011011110000", 
    34: "100010100010111010", 
    35: "100011011110011111", 
    36: "100100101100001011", 
    37: "100101010000101110", 
    38: "100110101001100100", 
    39: "100111010101000001", 
    40: "101000110001101001",
}