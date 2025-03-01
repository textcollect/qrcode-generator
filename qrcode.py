from credentials import resume_link
import specifications


# link = resume_link
# link = "HELLO WORLD"
# link = input("Link to encode: ")
# text = "hello world"
# print("No. of characters:", len(link))

# error_correction_level = input("Choose error correction level (H - 30%, Q - 25%, M - 15%, L - 7%): ").upper()
# error_correction_level = "H"

# Choose the Most Efficient Mode
def is_kanji(c: str) -> bool:
    """
    Check if character c can be encoded in QR Code Kanji mode.
    According to the QR Code spec, only double-byte characters whose
    Shift JIS encoding falls in one of these two ranges are allowed:
      - 0x8140 to 0x9FFC
      - 0xE040 to 0xEBBF
    """
    try:
        sjis_bytes = c.encode('shift_jis')  # Attempt to encode in Shift JIS
    except UnicodeEncodeError:
        return False  # Not encodable in Shift JIS at all
    if len(sjis_bytes) != 2:
        return False  # Kanji mode requires a 2-byte representation
    # Combine the two bytes into a single integer
    code = (sjis_bytes[0] << 8) | sjis_bytes[1]
    # Return True if code falls within one of the allowed ranges
    return (0x8140 <= code <= 0x9FFC) or (0xE040 <= code <= 0xEBBF)

def best_mode(input_string: str):
    """
    Determines the best QR Code encoding mode for the input string.

    1. Numeric mode: if the string contains only the digits 0-9.
    2. Alphanumeric mode: if every character is one of:
         0-9, A-Z, space, $, %, *, +, -, ., /, :
       (Note that lowercase letters are not allowed.)
    3. Kanji mode: if every character is a valid Kanji character for QR Codes,
       meaning its Shift JIS encoded value is in an allowed range.
    4. Byte mode: if the string can be encoded in ISO-8859-1.
    If none of these conditions hold, an error is returned.

    Example usage:
    print(best_mode("1234567890"))         # numeric
    print(best_mode("HELLO WORLD"))        # alphanumeric
    print(best_mode("漢字"))                # kanji (if the characters are in allowed Shift JIS range)
    print(best_mode("Hello, 世界"))         # likely Error (mixed content)
    """
    # Check for numeric mode (only digits 0-9 allowed)
    if all(c in "0123456789" for c in input_string):
        return "numeric"
    
    # Define the allowed characters for alphanumeric mode
    allowed_alphanumeric = set("0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ $%*+-./:")
    # Check for alphanumeric mode
    if all(c in allowed_alphanumeric for c in input_string):
        return "alphanumeric"
    
    # Check for Kanji mode: all characters must be valid for Kanji encoding.
    if input_string and all(is_kanji(c) for c in input_string):
        return "kanji"
    
    # Check for byte/binary mode: see if the string can be encoded in ISO-8859-1.
    try:
        input_string.encode('iso-8859-1')
        return "byte"
    except UnicodeEncodeError:
        print("Error: cannot be encoded in ISO-8859-1")
        return 0

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
    # Example nested dictionary with QR code capacities for each version.
    # Outer keys: QR versions
    # Second-level keys: error correction levels ('L', 'M', 'Q', 'H')
    # Third-level keys: encoding modes (e.g., 'numeric', 'alphanumeric', 'byte', 'kanji')

    # The string we want to encode
    # data_str = "Hello, world!"

    # For byte mode, each character is considered 1 byte (if in ASCII).
    required_length = len(input_string)

    # Specify the error correction level and mode you are using.
    # error_correction = 'M'
    # mode = 'byte'

    # Initialize a variable to store the selected QR version.
    selected_version = None

    qr_capacities = specifications.qr_capacities

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
        return 0

def str_to_bin(text: str):
    """ Converts input string into 8-bit binary representation. """
    # return "".join(format(t, 'b') for t in text)
    # Convert to integer representation with ord(), then format it in base 2 (binary mode)
    # binary_repr = [format(ord(i), 'b') for i in text]

    # If binary string is not length 8, pad with 0
    return [format(ord(t), 'b').zfill(8) for t in text]

# Mode indicator and char count
# We're going to use binary or byte-encoding to write our link text with ASCII characters, and hence choose the 0100 Mode Indicator.
def add_mode_n_char_count(input_string: list, data_mode: str) -> str:
    """ Adds encoding mode and number of characters in input string to beginning of the input string (in 8-bit binary).  
    Example: Add 0100 as the information for binary encoding and number of characters to the list holding the binary representation of the string."""
    bit_string = ""

    match data_mode:
        case "numeric":
            bit_string = "0001"
        case "alphnumeric":
            bit_string = "0010"
        case "byte":
            bit_string = "0100"
        case "kanji":
            bit_string = "1000"
        case _:
            raise ValueError

    # Add info on data mode and char count to the string
    input_string = bit_string + format(len(input_string), 'b').zfill(8) + "".join(input_string)
    return input_string

# Refer to an Error Correction Table that lists number of ECC needed based on QR version and EC level
# ECC: For version 6, H level of error correction, we need 28 Error Correction Codewords per block, 4 blocks in total, 15 Data Codewords each block
# Split data into 4 blocks, 15 data elements each
# Generate 28 EC Codewords from the 15 in each block

# Process until now:
# Original -> 8-bit binary -> Add mode and len(original) -> Add 0 and pad bytes until len(string) % 8 == 0 
# -> Group into 8-bit binary -> Integer (Data codewords)

def split_data_into_blocks(data: str, qr_ver: int, ec_level: str, ec_table: dict):
    """ Splits data codewords (in Integer) into groups and blocks based on QR code version and EC Level.
    There are at most 2 Groups. Within each group, data codewords (in Integer) are further split into Blocks 
    
    Args:
        ec_table: From error_correction_table function. Dictionary with info about no. of EC codewords, Groups, Blocks and Data codewords per Block.
    
    Returns:
        data_codewords: Dictionary in the form: {  
                                                "Group 1": {"Block 1": [...], "Block 2": [...], ...},  
                                                "Group 2": {"Block 1": [...], "Block 2": [...], ...} } 
                        if there is a Group 2.  \n
                        Otherwise, just: {"Group 1": {"Block 1": [...], "Block 2": [...], ...}}
        
        **ec_table[qr_ver][ec_level]["ECC per block"]**: EC Codewords Per Block
    """
    # Separate the encoded data string into 8-bit binary set
    data_as_integers = []
    for i in range(len(data) // 8):
        data_as_integers.append(data[(8 * i) : 8 + (8 * i)])
    
    # Convert back into integer representations
    data_as_integers = [int(i, base=2) for i in data_as_integers]

    # Using ec_table, find: 
    # number of ECC required per block (needed as nsym parameter later), total data codewords in Group 1, total data codewords in Group 2,
    # split data into a dictionary: {group 1: {block 1: data[:15], block 2: data[0 + 15 : 15 + 15], ...}, group 2: {block 1: ...}, ...}
    blocks_g1 = ec_table[qr_ver][ec_level]["Blocks in Group 1"]
    data_per_block_g1 = ec_table[qr_ver][ec_level]["Data codewords per Block in Group 1"]
    total_codewords_g1 = blocks_g1 * data_per_block_g1
    
    blocks_g2 = ec_table[qr_ver][ec_level]["Blocks in Group 2"]
    data_per_block_g2 = ec_table[qr_ver][ec_level]["Data codewords per Block in Group 2"]

    data_g1 = data_as_integers[:total_codewords_g1] # Data codewords in Group 1
    
    # If there are more than 2 Groups,
    if blocks_g2 > 0:
        data_g2 = data_as_integers[total_codewords_g1:] # Data codewords in Group 2
        data_codewords = {
            "Group 1": {f"Block{i+1}": data_g1[data_per_block_g1 * i : data_per_block_g1 + data_per_block_g1 * i] for i in range(blocks_g1)},
            "Group 2": {f"Block{i+1}": data_g2[data_per_block_g2 * i : data_per_block_g2 + data_per_block_g2 * i] for i in range(blocks_g2)}
        }
    else:
        data_codewords = {"Group 1": {f"Block{i+1}": data_g1[data_per_block_g1 * i : data_per_block_g1 + data_per_block_g1 * i] for i in range(blocks_g1)}}
    # Return the Data codewords separated into Groups and Blocks, and number of EC Codewords needed Per Block
    return data_codewords, ec_table[qr_ver][ec_level]["ECC per block"]

# To generate the EC Codewords, perform division steps n times, where n is the number of data codewords (i.e. 15 times)
# Get generator polynomial -> based on number of ECC needed (Ver 6 QR: 28 Error Correction Codewords per block, 4 blocks in total)
# Get message polynomial -> coefficients are simply the data in decimal integer format 
# (e.g. 67x^14 + 70x^13 + 135x^12 + 71x^11, 71x^10, 7x^9, 51x^8, 162x^7, 242x^6, 246x^5, 71x^4, 38x^3, 151x^2, 102x^1, 82)

# Code for generating ECC
# Credits to https://en.wikiversity.org/wiki/Reed%E2%80%93Solomon_codes_for_coders
def gf_mult_noLUT(x, y, prim=0):
    '''Multiplication in Galois Fields without using a precomputed look-up table (and thus it's slower)
    by using the standard carry-less multiplication + modular reduction using an irreducible prime polynomial'''

    ### Define bitwise carry-less operations as inner functions ###
    def cl_mult(x,y):
        '''Bitwise carry-less multiplication on integers'''
        z = 0
        i = 0
        while (y>>i) > 0:
            if y & (1<<i):
                z ^= x<<i
            i += 1
        return z

    def bit_length(n):
        '''Compute the position of the most significant bit (1) of an integer. Equivalent to int.bit_length()'''
        bits = 0
        while n >> bits: bits += 1
        return bits

    def cl_div(dividend, divisor=None):
        '''Bitwise carry-less long division on integers and returns the remainder'''
        # Compute the position of the most significant bit for each integers
        dl1 = bit_length(dividend)
        dl2 = bit_length(divisor)
        # If the dividend is smaller than the divisor, just exit
        if dl1 < dl2:
            return dividend
        # Else, align the most significant 1 of the divisor to the most significant 1 of the dividend (by shifting the divisor)
        for i in range(dl1-dl2,-1,-1):
            # Check that the dividend is divisible (useless for the first iteration but important for the next ones)
            if dividend & (1 << i+dl2-1):
                # If divisible, then shift the divisor to align the most significant bits and XOR (carry-less subtraction)
                dividend ^= divisor << i
        return dividend
    
    ### Main GF multiplication routine ###

    # Multiply the gf numbers
    result = cl_mult(x,y)
    # Then do a modular reduction (ie, remainder from the division) with an irreducible primitive polynomial so that it stays inside GF bounds
    if prim > 0:
        result = cl_div(result, prim)

    return result

def init_tables(prim=0x11d):
    '''Precompute the logarithm and anti-log tables for faster computation later, using the provided primitive polynomial.'''
    # prim is the primitive (binary) polynomial. Since it's a polynomial in the binary sense,
    # it's only in fact a single galois field value between 0 and 255, and not a list of gf values.
    global gf_exp, gf_log
    gf_exp = [0] * 512 # anti-log (exponential) table
    gf_log = [0] * 256 # log table
    # For each possible value in the galois field 2^8, we will pre-compute the logarithm and anti-logarithm (exponential) of this value
    x = 1
    for i in range(0, 255):
        gf_exp[i] = x # compute anti-log for this value and store it in a table
        gf_log[x] = i # compute log at the same time
        x = gf_mult_noLUT(x, 2, prim)

        # If you use only generator==2 or a power of 2, you can use the following which is faster than gf_mult_noLUT():
        #x <<= 1 # multiply by 2 (change 1 by another number y to multiply by a power of 2^y)
        #if x & 0x100: # similar to x >= 256, but a lot faster (because 0x100 == 256)
            #x ^= prim # subtract the primary polynomial to the current value (instead of 255, so that we get a unique set made of coprime numbers), this is the core of the tables generation

    # Optimization: double the size of the anti-log table so that we don't need to mod 255 to
    # stay inside the bounds (because we will mainly use this table for the multiplication of two GF numbers, no more).
    for i in range(255, 512):
        gf_exp[i] = gf_exp[i - 255]
    return [gf_log, gf_exp]

def gf_mul(x,y):
    if x==0 or y==0:
        return 0
    return gf_exp[gf_log[x] + gf_log[y]] # should be gf_exp[(gf_log[x]+gf_log[y])%255] if gf_exp wasn't oversized

def gf_pow(x, power):
    return gf_exp[(gf_log[x] * power) % 255]

def gf_poly_mul(p,q):
    '''Multiply two polynomials, inside Galois Field'''
    # Pre-allocate the result array
    r = [0] * (len(p)+len(q)-1)
    # Compute the polynomial multiplication (just like the outer product of two vectors,
    # we multiply each coefficients of p with all coefficients of q)
    for j in range(0, len(q)):
        for i in range(0, len(p)):
            r[i+j] ^= gf_mul(p[i], q[j]) # equivalent to: r[i + j] = gf_add(r[i+j], gf_mul(p[i], q[j]))
                                                         # -- you can see it's your usual polynomial multiplication
    return r

def rs_generator_poly(nsym):
    '''Generate an irreducible generator polynomial (necessary to encode a message into Reed-Solomon)\n
    Computes the generator polynomial for a given number of error correction symbols.'''
    g = [1]
    for i in range(0, nsym):
        g = gf_poly_mul(g, [1, gf_pow(2, i)])
    return g

def gf_poly_div(dividend, divisor):
    '''Fast polynomial division by using Extended Synthetic Division and optimized for GF(2^p) computations
    (doesn't work with standard polynomials outside of this galois field, see the Wikipedia article for generic algorithm).'''
    # CAUTION: this function expects polynomials to follow the opposite convention at decoding:
    # the terms must go from the biggest to lowest degree (while most other functions here expect
    # a list from lowest to biggest degree). eg: 1 + 2x + 5x^2 = [5, 2, 1], NOT [1, 2, 5]

    msg_out = list(dividend) # Copy the dividend
    #normalizer = divisor[0] # precomputing for performance
    for i in range(0, len(dividend) - (len(divisor)-1)):
        #msg_out[i] /= normalizer # for general polynomial division (when polynomials are non-monic), the usual way of using
                                  # synthetic division is to divide the divisor g(x) with its leading coefficient, but not needed here.
        coef = msg_out[i] # precaching
        if coef != 0: # log(0) is undefined, so we need to avoid that case explicitly (and it's also a good optimization).
            for j in range(1, len(divisor)): # in synthetic division, we always skip the first coefficient of the divisior,
                                              # because it's only used to normalize the dividend coefficient
                if divisor[j] != 0: # log(0) is undefined
                    msg_out[i + j] ^= gf_mul(divisor[j], coef) # equivalent to the more mathematically correct
                                                               # (but xoring directly is faster): msg_out[i + j] += -divisor[j] * coef

    # The resulting msg_out contains both the quotient and the remainder, the remainder being the size of the divisor
    # (the remainder has necessarily the same degree as the divisor -- not length but degree == length-1 -- since it's
    # what we couldn't divide from the dividend), so we compute the index where this separation is, and return the quotient and remainder.
    separator = -(len(divisor)-1)
    return msg_out[:separator], msg_out[separator:] # return quotient, remainder.

def rs_encode_msg(msg_in, nsym):
    '''Reed-Solomon main encoding function, using polynomial division (algorithm Extended Synthetic Division)
    
    Args:
        msg_in: Data codewords in Integer form in the block, as a list.
        nsym: Number of Error Correction Codewords (per block).
    
    Returns:
        Encoded message, a list containing the original data codewords and error-correction codewords.'''
    if (len(msg_in) + nsym) > 255: raise ValueError("Message is too long (%i when max is 255)" % (len(msg_in)+nsym))
    gen = rs_generator_poly(nsym)
    # Init msg_out with the values inside msg_in and pad with len(gen)-1 bytes (which is the number of ecc symbols).
    msg_out = [0] * (len(msg_in) + len(gen)-1)
    # Initializing the Synthetic Division with the dividend (= input message polynomial)
    msg_out[:len(msg_in)] = msg_in

    # Synthetic division main loop
    for i in range(len(msg_in)):
        # Note that it's msg_out here, not msg_in. Thus, we reuse the updated value at each iteration
        # (this is how Synthetic Division works: instead of storing in a temporary register the intermediate values,
        # we directly commit them to the output).
        coef = msg_out[i]

        # log(0) is undefined, so we need to manually check for this case. There's no need to check
        # the divisor here because we know it can't be 0 since we generated it.
        if coef != 0:
            # in synthetic division, we always skip the first coefficient of the divisior, because it's only used to normalize the dividend coefficient (which is here useless since the divisor, the generator polynomial, is always monic)
            for j in range(1, len(gen)):
                msg_out[i+j] ^= gf_mul(gen[j], coef) # equivalent to msg_out[i+j] += gf_mul(gen[j], coef)

    # At this point, the Extended Synthetic Divison is done, msg_out contains the quotient in msg_out[:len(msg_in)]
    # and the remainder in msg_out[len(msg_in):]. Here for RS encoding, we don't need the quotient but only the remainder
    # (which represents the RS code), so we can just overwrite the quotient with the input message, so that we get
    # our complete codeword composed of the message + code.
    msg_out[:len(msg_in)] = msg_in

    return msg_out

# Draft
# print("-- Draft starts here --")
# # Configuration of the parameters and input message
# prim = 0x11d
# n = 58 # set the size you want, it must be > k, the remaining n-k symbols will be the ECC code (more is better)
# k = 52 # k = len(message)
# message = "hello world" # input message
# # message = "https://drive.proton.me/urls/DKMBXXTESM#eCiRKHQqtSxF"
# print("\nOriginal message without code:", message)
# print("Original message as Integer:", [ord(x) for x in message])

# # Initializing the log/antilog tables
# init_tables(prim)

# # Encoding the input message
# mesecc = rs_encode_msg([ord(x) for x in message], n-k)
# print("Original encoded: %s" % mesecc)

# original_w_code = "".join([chr(i) for i in mesecc])
# print("Original encoded string:", original_w_code[:k], "\n", "Code:", original_w_code[k:])
# # print(len(original_w_code[k:])) # 6

# # block1 = ascii_data[:15]
# # msg = rs_encode_msg(block1, 28)
# # print("\nError-correction codewords:", msg[15:])
# # print("gf_exp:", gf_exp, "\n\n", "gf_log:", gf_log)
# # print(len(gf_exp), len(gf_log)) # 512, 256
# print("-- Draft ends here --\n")
# End of draft

def add_pad_bytes(encoded_data: str, qr_ver: int, ec_level: str) -> list:
    """ Find if current data length (in binary) fits the **Total Data codewords** for qr code version and EC level (Refer to ECC Table Dictionary).  
        If not, add at most 4 terminating 0s  
        After adding terminating bits, if still not long enough, add 0 until length is multiple of 8  
        Add Pad Bytes (11101100 00010001) if string still too short  

        Input:
            encoded_data: Data mode + len(Original_string) + Original string in 8-bit binary
        """
    # Get the total number of data bits required for this QR Ver. and EC Level
    total_data_bits_req = (specifications.error_correction_table()[qr_ver][ec_level]["Blocks in Group 1"] * specifications.error_correction_table()[qr_ver][ec_level]["Data codewords per Block in Group 1"]) + \
                        (specifications.error_correction_table()[qr_ver][ec_level]["Blocks in Group 2"] * specifications.error_correction_table()[qr_ver][ec_level]["Data codewords per Block in Group 2"])
    total_data_bits_req *= 8 # 8-bit binary

    # Add terminator of at most four 0 if data is < specifications for total data codewords (refer to ECC table dictionary)
    # In this case, version 6 requires 480 data bits
    # print("Unpadded data:", encoded_data)
    print("Unpadded data length:", len(encoded_data), "\nTotal data bits required:", total_data_bits_req) # 428 < 480

    # Add terminating 0000 if current length does not meet specification of qrcode version
    for _ in range(4):
        if len(encoded_data) < total_data_bits_req:
            encoded_data += '0'
        else:
            break # End loop early if length requirement satisfied

    # Make final total length be a multiple of 8 by adding 0's
    if len(encoded_data) % 8 != 0:
        while len(encoded_data) % 8 != 0:
            encoded_data += '0'

    # Add Pad Bytes (11101100 00010001) if the String is Still too Short
    while len(encoded_data) < total_data_bits_req:
        encoded_data += '11101100'
        if len(encoded_data) == total_data_bits_req:
            break
        else:
            encoded_data += '00010001'

    return encoded_data

# Generate Error correction codewords
def generate_ecc(data: dict, nsym: int):
    """ Generates Error Correction Codewords. Returns Data codewords and Error-correction codewords as 2d lists.  """
    # Configuration of the parameters and input message
    prim = 0x11d
    # Initializing the log/antilog tables
    init_tables(prim)

    # Get Error-Correction Codewords for each Block of Data using rs_encode_msg function
    ecc_in_each_block = [rs_encode_msg(v, nsym)[len(v):] for v in data["Group 1"].values()]

    # If the key "Group 2" exists (i.e. there are 2 Groups in the dictionary)
    if "Group 2" in data:
        # Get ECC for each Block in Group 2
        ecc_2 = [rs_encode_msg(v, nsym)[len(v):] for v in data["Group 2"].values()]
        # Add Group 2's ECC to Group 1
        ecc_in_each_block.extend(ecc_2)

    # Get only the Data codewords for interleaving (if Blocks > 1) later from the dictionary
    data_in_each_block = [v for dictionary in data.values() for v in dictionary.values()]

    return data_in_each_block, ecc_in_each_block

def interleave_and_combine_data(data: list[list], ecc: list[list]) -> list:
    """ If Data codewords is split into more than 1 Block, interleave Data codewords, then interleave Error-correction codewords.
    Put ECC after Data in one list.
     
    Returns:
        1D List of combined data"""
    combined = []
    if len(data) > 1:
        # For qrcode versions with more than 1 block, interleave data and error correction codewords respectively
        # Interleave data codewords
        # Example of a 2 Groups 2 Blocks: G1B1[0], G1B2[0], G2B1[0], G2B2[0], G1B2[1], G1B2[1], G2B1[1], G2B2[1], ...
        interleaved_data = []
        for col in range(max([len(i) for i in data])):
            for row in range(len(data)):
                try:
                    interleaved_data.append(data[row][col]) # data['block1'][0], data['block2'][0], ...
                except IndexError:
                    # If there rows that have fewer columns (for Data with 2 Groups), skip the row and continue to the next row
                    continue

        # print("Interleaved data codewords: ", interleaved_data)

        # Interleave Error-correction codewords
        # NOTE: Number of ECC is same across all Groups and Blocks, so not necessary to find max and will not encounter IndexError
        interleaved_ecc = []
        for col in range(len(ecc[0])):
            for row in range(len(ecc)):
                interleaved_ecc.append(ecc[row][col])
        
        # Put interleaved Error correction codewords after interleaved data codewords
        interleaved_data.extend(interleaved_ecc)
        combined = interleaved_data
    else:
        # If only 1 Block, data and ecc will be nested lists with 1 inner-list. Return the combined of those 2 inner lists
        data[0].extend(ecc[0])
        combined = data[0]
    return combined

def initial_grid(qr_ver: int):
    """ Creates a n x n 2D-list as the grid, where n = size (no. of rows/columns) of the grid.
    Version 1 QR code is 21 x 21,
    Version 2 is 25 x 25, ...
    Version 40 is 177 x 177.  
    Each next version is 4 modules larger than the previous. Hence, n = 21 + 4 (Version no. - 1)"""
    grid = []
    grid_size = 21 + 4 * (qr_ver - 1)
    for _ in range(grid_size):
        row = [0 for _ in range(grid_size)]
        grid.append(row)
    return grid

def position_squares():
    """ Position squares are 7 x 7 squares, with a 3 x 3 square in the middle.\n
    1111111\n
    1000001\n
    1011101\n
    1011101\n
    1011101\n
    1000001\n
    1111111"""
    square = []
    # Outer (7 x 7)
    for i in range(7):
        row = []
        row.append(1) # Start of row

        for _ in range(1, 6):
            # If current row is first or last, append 1 from start to end
            if i == 0 or i == 6:
                row.append(1)
            # else, append 0 from start to end
            else:
                row.append(0)
        row.append(1) # End of row

        # Add row to the square
        square.append(row)
    
    # Inner (3 x 3)
    # Modify square to make an inner square of 3 x 3
    for i in range(2, 5):
        for j in range (2, 5):
            square[i][j] = 1

    for row in range(len(square)):
        for col in range(len(square[row])):
            if square[row][col] == 1:
                square[row][col] = "position1"
            else:
                square[row][col] = "position0"
    return square

def alignment_square():
    """ A 5 x 5 square, with a black spot in the middle at (2, 2).\n
    11111\n
    10001\n
    10101\n
    10001\n
    11111 """
    square = []
    for i in range(5):
        # Make all rows = 1 first
        row = [1 for _ in range(5)]
        # If row is not first or last row, replace 1's with 0's for range(1, 4)
        if 0 < i < 4:
            for j in range(1, 4):
                row[j] = 0
            # If middle row, turn middle position into 1
            if i == 2:
                row[i] = 1
        square.append(row)
    
    square = [["alignment1" if ele == 1 else "alignment0" for ele in row] for row in square]
    return square

# Replace the appropriate positions of the initial grid with the position squares
def set_position_squares(matrix: list):
    """ Adds position squares to the 3 corners of the grid.  
    Position squares are 7 x 7 squares, with a 3 x 3 square in the middle.  
    Located at positions (0, 0), (matrix length - 7, 0) and (0, matrix length - 7)"""
    sq = position_squares()
    for row in range(len(sq)):
        for col in range(len(sq)):
            matrix[row][col] = sq[row][col] # Top-left (0, 0)
            matrix[row][len(matrix) - 7 + col] = sq[row][col] # Top-right (0, matrix length - 7)
            matrix[len(matrix) - 7 + row][col] = sq[row][col] # Bottom-left (matrix length - 7, 0)

    return matrix

# Step 2: Add the Separators
def add_separators(square: list) -> list:
    """ Add the separators.
    Separators are lines of white modules, one module wide, that are placed beside the finder patterns to separate them from the rest of the QR code.
    The separators are only placed beside the edges of the finder patterns that touch the inside of the QR code. """
    for i in range(8):
        # Top-left
        square[i][7] = "separator"
        square[7][i] = "separator"
        # Top-right
        square[i][-8] = "separator"
        square[7][-i-1] = "separator"
        # Bottom-left
        square[-8][i] = "separator"
        square[-i-1][7] = "separator"
    return square

# Center module of alignment square is placed at positions determined by version of qrcode
# For QR Code version 6 the numbers are: 6, 34; i.e. (6, 6), (6, 34), (34, 6), (34, 34)
def permutate_numbers(numbers: tuple):
    """ Given a tuple of numbers, return a set of all combinations of 2 number permutation.  
    Example for version 7 number are: 6, 22, 38. So coordinates are (6, 6), (6, 22), (6, 38), (38, 6), (38, 22), (38, 38), (22, 6), (22, 22), (22, 38)
    """
    # [6, 22, 38]
    # Iterate over the list: for each number, add the next number to a tuple
    coordinates = set() # Set to remove duplicates
    for i in range(len(numbers)):
        for j in range(len(numbers)):
            coordinates.add((numbers[i], numbers[j]))
    
    return coordinates

# Replace the elements of the grid with the alignment_square
# Center module cannot overlap with position squares
def alignment_pos(matrix: list[list], coordinate_pairs: set) -> list:
    """ Center module of alignment square is placed at positions determined by version of qrcode.  
    Refer to alignment_coordinates dictionary from specifications to get coordinates for specific QR versions.\n
    For QR Code version 6 the numbers are: 6, 34; i.e. (6, 6), (6, 34), (34, 6), (34, 34)\n
    Center module cannot overlap with position squares\n
    Find the coordinates that are unoccupied to replace with the center of the alignment squares.
    Row and column coordinates are determined based on qr code version.\n

    NOTE: This function is only valid until version 6! Version 7 - 13 has 3 numbers permutation, 14 - 20 has 4, etc.
    Every 7 versions increase by 1, until version 35 - 40 with 7 sets of numbers to permutate.\n
    Example for version 7 number are: 6, 22, 38. So coordinates are (6, 6), (6, 22), (6, 38), (22, 6), (22, 22), (22, 38), (38, 6), (38, 22), (38, 38)
    
    Returns:
            List of tuples (as coordinates)"""
    coordinates = []
    for pair in coordinate_pairs:
        if matrix[pair[0]][pair[1]] == 0:
            coordinates.append((pair[0], pair[1]))

    return coordinates

def set_alignment_squares(matrix: list, center_coordinates: list):
    """ Adds alignment squares to the grid.  
    Alignment squares are 5x5 squares, with a 1x1 dark module in the middle at (2, 2) """
    alignment = alignment_square()
    for coord in center_coordinates:
        # Variables row and col refers to coordinates of the matrix, not coordinates of the alignment square.
        # Shift to top-left coordinate
        row = coord[0] - 2
        # For each row, iterate over the columns to change 0 to 1
        for i in range(5):
            col = coord[1] - 2
            for j in range(5):
                matrix[row][col] = alignment[i][j]
                col += 1
            row += 1
    return matrix

def timing_strips(square):
    """ Add timing strips to the grid that already has 
    2 lines connecting bottom-right of the top-left position square with the other 2.
    Horizontal timing pattern is placed on the 7th row of the QR code between the separators.
    The vertical timing pattern is placed on the 7th column of the QR code between the separators.
    The timing patterns always start and end with a dark module.\n
    From (6, 8) and (8, 6), add 2 across the row and column respectively, turning 0's into 1's until you reach (len(square) - 9)"""
    for i in range(8, len(square) - 8, 2):
        square[6][i] = 1
        square[i][6] = 1

    return square

# Step 5: Add the Dark Module (Pixel) and Reserved Areas
def dark_module_and_reserved_area(square: list, version: int) -> list:
    """ All QR codes have a dark module beside the bottom left finder pattern.
    More specifically, the dark module is always located at the coordinate ([(4 * V) + 9], 8) where V is the version of the QR code.\n
    There are 2 reserved areas types: Format Information Area and Version Information Area (Version 7 and above)\n
    Format Information Area:\n
    * Near the top-left finder pattern, a one-module strip must be reserved below and to the right of the separator.
    * Near the top-right finder pattern, a one-module strip must be reserved below the separator.
    * Near the bottom-left finder pattern, a one-module strip must be reserved to the right of the separator.\n
    
    QR codes versions 7 and larger must contain two areas where version information bits are placed.
    The areas are a 6x3 block above the bottom-left finder pattern and a 3x6 block to the left of the top-right finder pattern.
"""
    square[(4 * version + 9)][8] = "dark"

    # Format Information Area
    # Start from (0, 8), iterate down the rows until (8, 8)
    # Row 8: (8, 0) until (8, 8) and (8, -8) to (8, -1)
    # (From (4 * version + 10), 8) until ((4 * version + 16), 8)
    # Skip/Exclude if hit 1 (black pixel)
    for i in range(9):
        if square[i][8] != 1:
            square[i][8] = "reserved"
        if square[8][i] != 1:
            square[8][i] = "reserved"
        if square[8][-i] != 1:
            square[8][-i] = "reserved"
    
    for i in range(7):
        square[(4 * version + 10 + i)][8] = "reserved"

    # Version Information Area (For version 7 and above)
    if version >= 7:
        for i in range(6):
            for j in range(3):
                square[i][-9-j] = "reserved"
                square[-9-j][i] = "reserved"
    return square

# New function: Insert data bits using standard QR placement (zig-zag pattern)
def insert_data_bits(matrix: list, data: list) -> list:
    """ Data is inserted in the following order: right-to-left. Starts from bottom-right corner in upward direction.
    If hit any of the reserved, timing, alignment squares, skip them.
    If hit the reserved area at top-right, shift to the left and change direction to downward, retaining right-to-left placement.
    Reserved areas: the elements with value "reserved", row 6, col 6 for timing strips, alignment square, dark pixel at ([(4 * V) + 9], 8)
     """
    n = len(matrix)
    col = n - 1
    row = n - 1
    direction = -1  # moving upward initially

    def is_reserved(matrix, row, col):
        # Skip reserved areas
        if matrix[row][col] in ["reserved", "dark", "separator", "alignment0", "alignment1", "position0", "position1"]:
            return True
        
        # Skip timing strips
        # if row == 6 or col == 6:
        #     return True
        
    while col > 0:
        # End condition
        if len(data) <= 0:
            break
        
        # Skip timing strip at column 6
        if col == 6:
            col -= 1

        while 0 <= row < n:
            # Skip timing strip
            if row == 6:
                row += direction
                continue

            # If position is not reserved, insert data from right-to-left, upward initially
            if not is_reserved(matrix, row, col) and len(data) > 0:
                matrix[row][col] = int(data.pop())
            col -= 1 # Move left regardless

            if not is_reserved(matrix, row, col) and len(data) > 0:
                matrix[row][col] = int(data.pop())
            col += 1 # Move right
            
            row += direction # Move up/down
        
        direction *= -1 # Change direction after going through from 0 to n-1
        row += direction # Adjust row value after direction change as final while-loop cause row to go over Index
        col -= 2 # Move left 2 columns

    return matrix

# Masking function
def masking(num: int, row: int, col: int):
    match num:
        case 0:
            return (row  + col) % 2 == 0
        case 1:
            return row % 2 == 0
        case 2:
            return col % 3 == 0
        case 3:
            return (row + col) % 3 == 0
        case 4:
            return ((row // 2) + (col // 3)) % 2 == 0
        case 5:
            return ((row * col) % 2) + ((row * col) % 3) == 0
        case 6:
            return (((row * col) % 2) + ((row * col) % 3)) % 2 == 0
        case 7:
            return (((row + col) % 2) + ((row * col) % 3)) % 2 == 0

# TODO: Function to find optimal masking function
def optimal_mask():
    return


# Apply masking function
def apply_mask(square: list, num: int):
    """ If the formula for the given mask pattern is true for a given row/column coordinate, switch the bit at that coordinate"""
    n = len(square)

    for row in range(n):
        for col in range(n):
            if masking(num, row, col) and isinstance(square[row][col], int) and row != 6 and col != 6:
                if square[row][col] == 1:
                    square[row][col] = 0
                else:
                    square[row][col] = 1
    return square

# Add a function to set the format strings (elements with value "reserved") based on mask pattern and error correction level (pattern 2, EC level 'H' for this instance)
def set_format_strings(square: list, pattern: int, ec_level: str):
    """ Use a lookup table to get format string based on mask pattern and error correction level. There are 32 total format strings.
    Format strings are located at:
    Full: row 8, col 0:8, row 8 : 0, col 8
    First 7: row len(square) - 1 - 6 : len(square) - 1, col 8
    Last 8: row 8, col len(square) - 1 - 7 : len(square) - 1"""
    format_string_dict = {"L": {0: "111011111000100",
                                1: "111001011110011",
                                2: "111110110101010",
                                3: "111100010011101",
                                4: "110011000101111",
                                5: "110001100011000",
                                6: "110110001000001",
                                7: "110100101110110"},
                          "M": {0: "101010000010010",
                                1: "101000100100101",
                                2: "101111001111100",
                                3: "101101101001011",
                                4: "100010111111001",
                                5: "100000011001110",
                                6: "100111110010111",
                                7: "100101010100000"},
                          "Q": {0: "011010101011111",
                                1: "011000001101000",
                                2: "011111100110001",
                                3: "011101000000110",
                                4: "010010010110100",
                                5: "010000110000011",
                                6: "010111011011010",
                                7: "010101111101101"},
                          "H": {0: "001011010001001",
                                1: "001001110111110",
                                2: "001110011100111",
                                3: "001100111010000",
                                4: "000011101100010",
                                5: "000001001010101",
                                6: "000110100001100",
                                7: "000100000111011"}}
    
    format_string = list(format_string_dict[ec_level][pattern])
    # Set first 7 bits of format string first
    for i in range(7):
        # If (row, col) = timing strip, col + 1
        if i == 6:
            square[8][i + 1] = int(format_string[i])
            # print("Test:", i + 1)
        else:
            square[8][i] = int(format_string[i])

        square[len(square) - 7 + i][8] = int(format_string[i]) # Bottom-left not affected by timing strip
        # print(format_string[i])
    
    # Set final 8 bits of the format string
    row = 8
    for i in range(8):
        # If (row, col) = timing strip, row + 1
        if row == 6:
            row -= 1
        square[row][8] = int(format_string[7 + i])
        square[8][len(square) - 8 + i] = int(format_string[7 + i]) # Top-right not affected by timing strip
        row -= 1
        # print(format_string[7 + i])
    
    return square

def set_version_information_strings(square: list[list], qr_ver: int):
    """ For QR versions 7 and above, add the version information string to the reserved 6x3 modules on bottom-left and top-right.  
    Version info string is inserted from **right** most (least significant) bit.\n
    Refer to table for dictionary of all Version Information Strings from ver 7 to 40.
    """
    ver_string = specifications.version_information_string[qr_ver]
    print("Version string:", ver_string)

    # For bottom-left (6col x 3row): top-to-bottom, left-to-right, i.e. row -> column
    i = 17
    for col in range(6):
        for row in range(3):
            square[len(square) - 11 + row][col] = int(ver_string[i])
            i -= 1
    
    i = 17
    # For top-right (3col x 6row): left-to-right, then top-to-bottom, i.e. column -> row
    for row in range(6):
        for col in range(3):
            square[row][len(square) - 11 + col] = int(ver_string[i])
            i -= 1
    
    return square

# Add a simple function to render the QR code in the terminal.
def print_qr(matrix: list):
    for row in matrix:
        # Print dark modules as "⬛", else print two spaces.
        print("".join([chr(0x2588) * 2 if cell in [1, "alignment1", "position1", "dark"] else "  " for cell in row]))

def proper_qr(matrix: list):
    """ Return the strings in the list from "alignment", "position", "dark" to 1 or 0 """
    # matrix = [[1 if r in ["alignment1", "position1", "dark"] else 0 for r in row] for row in matrix]
    for row in range(len(matrix)):
        for r in range(len(matrix)):
            if matrix[row][r] in ["alignment1", "position1", "dark", 1]:
                matrix[row][r] = 1
            else:
                matrix[row][r] = 0

    return matrix

def quiet_zone(matrix: list):
    """ Add a 4 module wide area of light modules as a Quiet Zone, according to the QR code specification. """
    # Create a quiet row (list of 0's) with the same number of columns as the matrix.
    quiet_row = []
    for _ in range(len(matrix)):
        quiet_row.append(0)
    
    # Insert 4 quiet rows at the top and bottom.
    # Use a copy of quiet_row to ensure each row is independent.
    for _ in range(4):
        matrix.insert(0, quiet_row.copy()) # Top row
        matrix.append(quiet_row.copy()) # Bottom row

    # Add 4 more 0 to bginning and end of each row
    for r in range(len(matrix)):
        for _ in range(4):
            matrix[r].insert(0, 0)
            matrix[r].append(0)
            
    return matrix

def scale_up_pixels(small_pixels, scale_factor):
    """
    Scales up the image by replicating each pixel 'scale_factor' times in both dimensions.
    
    Args:
        small_pixels: 2D list of original pixels (0 for white, 1 for black).
        scale_factor: Integer factor by which to scale the image.
    
    Returns:
        A new 2D list representing the scaled-up image.
    """
    new_pixels = []
    for row in small_pixels:
        # Expand each pixel in the row horizontally.
        new_row = []
        for pixel in row:
            for _ in range(scale_factor):
                new_row.append(pixel)
        # Repeat the entire row vertically.
        for _ in range(scale_factor):
            new_pixels.append(new_row)

    return new_pixels

def save_pbm(filename, matrix):
    """
    Saves the given 2D pixel data in the PBM format.
    
    Args:
        filename: Name of the output file.
        matrix: 2D list of pixels (0 for white, 1 for black).
    """
    # Define the width and height of the image
    height = len(matrix)
    width = len(matrix[0])

    # Open a new file in write mode. The file extension ".pbm" is conventional.
    with open(f"{filename}.pbm", "w") as f:
        # Write the PBM header.
        # "P1" indicates the file is an ASCII PBM.
        f.write("P1\n")
        # The next line contains the image width and height.
        f.write(f"{width} {height}\n")
        
        # Write the pixel data.
        for row in matrix:
            # Join each pixel value with a space and write the row to the file.
            f.write(" ".join(str(pixel) for pixel in row) + "\n")
        print(f"File saved as {filename}.pbm.")

def save_txt(filename, matrix: list):
    """
    Saves the given 2D pixel data in the TXT format.
    
    Args:
        filename: Name of the output file.
        matrix: 2D list of pixels (0 for white, 1 for black).
    """
    # Open a new file in write mode. The file extension ".pbm" is conventional.
    with open(f"{filename}.txt", "w", encoding='utf-8') as f:
        # Write the pixel data.
        for row in matrix:
            new_row = "".join([chr(0x2588) * 2 if pixel == 1 else '  ' for pixel in row])
            print(new_row)
            # Join each pixel value with a space and write the row to the file.
            f.write(new_row + "\n")
        print(f"File saved as {filename}.txt.")

def generate_qr(input_text: str, error_correction_level: str):
    """ Main function """
    data_mode = best_mode(input_string=input_text)
    print("Data mode:", data_mode)
    # print(input_text)

    # Cannot be encoded due to length or datatype error
    if data_mode == 0:
        return 0 # End function early and return 0 as error representation
    
    # Get optimal QR version
    qr_version = smallest_version(input_string=input_text, error_correction=error_correction_level, mode=data_mode)
    # No smallest version
    if qr_version == 0:
        return 0
    print("QR Version:", qr_version)
    
    # Convert input_text into 8-bit binaries in a list
    binary_repr = str_to_bin(input_text)
    # print("Input string(in 8-bit binary):", binary_repr)

    # Add Mode Indicator and string length bits
    data_string = add_mode_n_char_count(input_string=binary_repr, data_mode="byte")
    data_string = add_pad_bytes(encoded_data=data_string, qr_ver=qr_version, ec_level=error_correction_level)

    # Separate the data into sets of 15, 4 blocks
    # data_codewords = {f"Block{i+1}": ascii_data[0 + 15 * i:15 + 15 * i] for i in range(4)}
    data_codewords, ecc_required = split_data_into_blocks(data=data_string, qr_ver=qr_version, ec_level=error_correction_level, ec_table=specifications.error_correction_table())

    # test_data = [67,85,70,134,87,38,85,194,119,50,6,18,6,103,38,246,246,66,7,118,134,242,7,38,86,22,198,199,146,6,182,230,247,119,50,7,118,134,87,38,82,6,134,151,50,7,70,247,118,86,194,6,151,50,224,236,17,236,17,236,17,236]
    # test_data2 = [32, 91, 11, 120, 209, 114, 220, 77, 67, 64, 236, 17, 236] # "HELLO WORLD"
    # data_codewords, ecc_required = split_data_into_blocks(data=test_data2, qr_ver=1, ec_level="Q", ec_table=error_correction_table())

    for k, v in data_codewords.items():
        print(f"{k}: {v}")

    print("Number of Error-Correction Codewords required:", ecc_required)

    # Generate Error correction codewords
    data_codewords, ec_codewords = generate_ecc(data=data_codewords, nsym=ecc_required)
    print("Error-Correction Codewords:", ec_codewords)
    print("Data codewords (2d list):", data_codewords, "\n")

    data_to_fill = interleave_and_combine_data(data=data_codewords, ecc=ec_codewords)
    print("Combined interleaved data and ec codewords:", data_to_fill, "\n")

    # Turn the data back into 8-bit binary numbers
    data_to_fill = [format(i, 'b').zfill(8) for i in data_to_fill]
    # [print(f"Data {i+1}:", data_to_fill[i]) for i in range(len(data_to_fill))]

    # Separate each individual bit as an element in a list
    data_to_fill = list("".join(data_to_fill))
    # Reverse the list so that we can use pop() when placing the data bits
    data_to_fill.reverse()


    # Create grid and insert data
    grid = initial_grid(qr_ver=qr_version) # Initialise grid
    grid = set_position_squares(grid) # Set position squares
    grid = add_separators(grid) # Add Separators
    # print(grid)

    # Add alignment square(s) if Qr Version > 1
    if qr_version > 1:
        coordinate_pairs_set = permutate_numbers(numbers=specifications.alignment_coordinates[qr_version])
        alignment_pattern_locations = alignment_pos(matrix=grid, coordinate_pairs=coordinate_pairs_set)
        print(alignment_pattern_locations)
        grid = set_alignment_squares(grid, alignment_pattern_locations)

    grid = timing_strips(grid) # Add Timing strips
    grid = dark_module_and_reserved_area(grid, version=qr_version) # Add dark module and reserved areas

    # Call the new data insertion after bit list is ready
    grid = insert_data_bits(matrix=grid, data=data_to_fill)
    # for r in grid:
    #     print(r)

    # Use mask pattern 2 for this project
    grid = apply_mask(grid, num=2)
    grid = set_format_strings(grid, pattern=2, ec_level=error_correction_level) # Add format strings

    # If QR Version >= 7, add Version Information String at bottom-left and top-right
    if qr_version >= 7:
        grid = set_version_information_strings(square=grid, qr_ver=qr_version)
    
    # Render the final QR code grid
    # print_qr(grid)

    # for v in grid:
    #     print(v)

    grid = proper_qr(grid) # Set strings to appropriate 1s and 0s
    grid = quiet_zone(grid) # Add quiet zone around grid

    scale_factor = 11  # 41 * 11 = 451, so you'll need extra padding to reach 480.
    scaled = scale_up_pixels(grid, scale_factor) # Make QR output bigger if saving as .pbm image

    # print(chr(0x2B1B))
    # print(chr(0x2B1C))
    save_pbm("output", scaled)
    save_txt("output", grid)
    return 1

if __name__ == "__main__":
    while True:
        try:
            ecl = input("Choose error correction level (H - 30%, Q - 25%, M - 15%, L - 7%): ").upper()
            if ecl.upper() not in ["H", "Q", "M", "L"]:
                raise Exception("Invalid input.")
            break
        except Exception:
            print("Invalid input. Try again.")
    
    # generate_qr(input_text=resume_link, error_correction_level=ecl)
    # generate_qr(input_text=resume_link, error_correction_level='Q')
    # generate_qr(input_text="Lorem ipsum dolor sit amet esse labore non ipsum officia aliq", error_correction_level='H')
    text_to_encode = input("Text to encode: ")
    generate_qr(input_text=text_to_encode, error_correction_level=ecl)