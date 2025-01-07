from Utils.HelperFunctions import SplitWordTo4BitsArrays, Connect4BitsArraysToWord,splitIntoChunks

#hamming 7-4
class Hamming:
    # BITS PARITY CALCULATOR

    numPacksCorrected = 0
    @staticmethod
    def __calculate_parity_bits(data):
        """
            Calculate the parity bits for a 4-bit input data array.
            :param data: A list of 4 bits representing the input data.
            :return: A list of 3 parity bits [p1, p2, p3].
        """
        # Calculate parity bits
        p1 = data[0] ^ data[1] ^ data[3]
        p2 = data[0] ^ data[2] ^ data[3]
        p3 = data[1] ^ data[2] ^ data[3]
        return [p1, p2, p3]

    #KODER
    @staticmethod
    def __hamming_encode(data):
        """
            Encode 4 bits of input data into a 7-bit Hamming code.
            :param data: A list of 4 bits to encode.
            :return: A list of 7 bits, including 3 parity bits and the original 4 data bits.
            :raises ValueError: If the input data is not exactly 4 bits.
        """
        # The input data is expected to be a list of 4 bits (data bits)
        if len(data) != 4:
            raise ValueError("Data must be a list of 4 bits.")

        # Calculate parity bits
        p1, p2, p3 = Hamming.__calculate_parity_bits(data)

        # Return the encoded data (with parity bits added at positions 1, 2, and 4)
        return [p1, p2, data[0], p3, data[1], data[2], data[3]]

    ##DEKODER
    @staticmethod
    def __hamming_decode(encoded_data, bitpacknumber):
        """
            Decode a 7-bit Hamming code into the original 4-bit data, correcting single-bit errors if present.

            :param encoded_data: A list of 7 bits representing the encoded data.
            :param bitpacknumber: The number of the bit pack being decoded (for error reporting).
            :return: A list of 4 bits, representing the original data.
            :raises ValueError: If the input encoded data is not exactly 7 bits.
        """
        if len(encoded_data) != 7:
            raise ValueError("Encoded data must be a list of 7 bits.")

        # Extract the parity and data bits
        p1, p2, d0, p3, d1, d2, d3 = encoded_data

        # Recalculate the parity bits to check for errors
        p1_calc, p2_calc, p3_calc = Hamming.__calculate_parity_bits([d0, d1, d2, d3])

        # Calculate the syndrome (which bit, if any, is wrong)
        error_position = (p1 ^ p1_calc) * 1 + (p2 ^ p2_calc) * 2 + (p3 ^ p3_calc) * 4

        # Correct the error if the syndrome is not 0
        if error_position != 0:
            print(f"Error detected bit pack {bitpacknumber}, at position {error_position}, correcting...")
            encoded_data[error_position - 1] ^= 1  # Flip the erroneous bit
            Hamming.numPacksCorrected += 1

        # Return the corrected data bits
        return [encoded_data[2], encoded_data[4], encoded_data[5], encoded_data[6]]

    @staticmethod
    def CodeDataHamming(word):
        """
            Encode an input word (string) into a list of 7-bit Hamming codes.
            :param word: A string to encode.
            :return: A list of 7-bit encoded data arrays.
        """
        listabit = SplitWordTo4BitsArrays(word)
        listabitencoded = []
        for array in listabit:
            listabitencoded.append(Hamming.__hamming_encode(array))
        return listabitencoded

    @staticmethod
    def CodeDataHammingObraz(imageData):
        """
            Encode image data into a list of 7-bit Hamming codes.
            :param imageData: A binary array representing the image data.
            :return: A list of 7-bit encoded data arrays.
        """
        chunk_size = 4  # Size of each chunk
        imageData_chunks = splitIntoChunks(imageData, chunk_size)  # Split into 4-element chunks

        listabitencoded = []
        for chunk in  imageData_chunks:
            encoded_chunk = Hamming.__hamming_encode(chunk)
            listabitencoded.append(encoded_chunk)

        return listabitencoded

    @staticmethod
    def DecodeInputDataHamming(wordCoded, asWord):
        """
            Decode a list of 7-bit Hamming codes into the original word or data array.
            :param wordCoded: A list of 7-bit encoded data arrays.
            :param asWord: A boolean flag indicating whether to return the decoded data as a string.
            :return: The decoded data as a string (if asWord=True) or a list of 4-bit data arrays.
        """
        decodedWord= []
        for i,array in enumerate(wordCoded):
            decodedWord.append(Hamming.__hamming_decode(array,i+1))
        if asWord:
            word_after_dekode = Connect4BitsArraysToWord(decodedWord)
            return word_after_dekode
        else:
            return decodedWord

    @staticmethod
    def DecodeInputDataHammingObraz(wordCoded):
        """
            Decode a list of 7-bit Hamming codes representing image data.
            :param wordCoded: A list of 7-bit encoded data arrays.
            :return: A list of 4-bit data arrays representing the original image data.
        """
        decodedWord = []
        for i,array in enumerate(wordCoded):
            decodedWord.append(Hamming.__hamming_decode(array,i+1))
        return decodedWord

    def ClearNumCorrectedPacks(self):
        Hamming.numPacksCorrected = 0
    def PrintNumCorrectedPacks(self):
        print(Hamming.numPacksCorrected)