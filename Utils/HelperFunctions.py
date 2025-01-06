# Converts a given char into bits
def char_to_bit(char):
    # Step 1: Get the ASCII value of the character
    ascii_value = ord(char)

    # Step 2: Convert the ASCII value to a binary string
    # The [2:] slices off the '0b' prefix from the binary string
    binary_string = bin(ascii_value)[2:]

    # Step 3: Pad the binary string with leading zeros to make it 8 bits long
    padded_binary_string = binary_string.zfill(8)

    # Step 4: Convert the padded binary string to a list of bits
    bits_array = [int(bit) for bit in padded_binary_string]

    return bits_array

# Converts a word into an array that consists of arrays of 8 bits that form a character (char)
def word_to_list(word):
    tempWord = []
    for letter in word:
        tempWord.append(char_to_bit(letter))
    return tempWord

# Converts 1D arrays of bits into a word (used in convolutional)
def decode_bits_to_string(bit_array):
    # Ensure the array length is a multiple of 8
    if len(bit_array) % 8 != 0:
        raise ValueError("The length of the bit array should be a multiple of 8.")

    # Convert each group of 8 bits to a character
    characters = []
    for i in range(0, len(bit_array), 8):
        # Take a slice of 8 bits
        byte = bit_array[i:i + 8]

        # Convert the list of bits to a string of '0' and '1' (binary representation)
        byte_str = ''.join(map(str, byte))

        # Convert binary string to an integer, then to a character
        character = chr(int(byte_str, 2))
        characters.append(character)

    # Join all characters to form the final decoded word
    return ''.join(characters)

# If we have, for example, an array from the word function into arrays, we can use this function to split each sub-array into 2 arrays of 4 bits
def split_array_of_8_to_4(bits_array):
    # Check if the input array has exactly 8 bits
    if len(bits_array) != 8:
        raise ValueError("Input array must have exactly 8 bits.")

    # Split the array into two arrays of 4 bits each
    first_half = bits_array[:4]  # First 4 bits
    second_half = bits_array[4:]  # Last 4 bits

    return first_half, second_half

# Merges two 4-bit arrays into one 8-bit array
def join_4_bit_arrays(array1, array2):
    return array1 + array2

# Converts an array of bits into a character
def bits_to_char(bits):
    byte_str = ''.join(str(bit) for bit in bits)
    return chr(int(byte_str, 2))

"""
If we have as below the word hey (example, these arrays do not mean hey)
[0,1,1,1,0,0,0,1],[0,0,0,0,1,1,1,1],[0,0,1,1,0,0,1,1]
then the function breaks them into smaller arrays, i.e.
[0,1,1,1],[0,0,0,1],[0,0,0,0],[1,1,1,1],[0,0,1,1],[0,0,1,1]
"""
def SplitWordTo4BitsArrays(slowo):
    listabit = []
    for l in slowo:
        table = char_to_bit(l)
        firsthalf,secondhalf = split_array_of_8_to_4(table)
        listabit.append(firsthalf)
        listabit.append(secondhalf)
    return listabit

def splitIntoChunks(array, chunk_size):
    return [array[i:i + chunk_size] for i in range(0, len(array), chunk_size)]


"""
Function for concatenating 4-bit arrays back into a word
substitutes an array of type
[0,1,1,1],[0,0,0,1],[0,0,0,0],[1,1,1,1],[0,0,1,1],[0,0,1,1]
{                 } {                  }{                 }
         H                     E                 J
in the word (example these arrays in ascii do not mean the word hey)
"""
def Connect4BitsArraysToWord(array):
    if len(array) % 2 != 0:
        raise ValueError("Tablica musi mieć parzystą liczbę elementów")

    word = ""
    for i in range(0, len(array), 2):
        array1 = array[i]
        array2 = array[i + 1]
        connected_table = join_4_bit_arrays(array1, array2)
        sign = bits_to_char(connected_table)
        word += sign
    return word