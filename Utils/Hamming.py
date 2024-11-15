#hamming 7-4
from Utils.HelperFunctions import RozbijSlowoNa4BitoweArraye, Zlacz4BitoweArrayeNaSlowo,splitIntoChunks

class Hamming:
    #KALKULATOR BITOW PARZYSTOSCI ALE NIE UZYWAMY
    @staticmethod
    def __calculate_parity_bits(data):
        # Calculate parity bits
        p1 = data[0] ^ data[1] ^ data[3]
        p2 = data[0] ^ data[2] ^ data[3]
        p3 = data[1] ^ data[2] ^ data[3]
        return [p1, p2, p3]
    #KODER ALE NIE UZYWAMY
    @staticmethod
    def __hamming_encode(data):
        # The input data is expected to be a list of 4 bits (data bits)
        if len(data) != 4:
            raise ValueError("Data must be a list of 4 bits.")

        # Calculate parity bits
        p1, p2, p3 = Hamming.__calculate_parity_bits(data)

        # Return the encoded data (with parity bits added at positions 1, 2, and 4)
        return [p1, p2, data[0], p3, data[1], data[2], data[3]]

    ##DEKODER ALE JEJ NIE UZYWAMY##
    @staticmethod
    def __hamming_decode(encoded_data,bitpacknumber):
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

        # Return the corrected data bits
        return [encoded_data[2], encoded_data[4], encoded_data[5], encoded_data[6]]

    @staticmethod
    def CodeDataHamming(slowo):
        listabit = RozbijSlowoNa4BitoweArraye(slowo)
        listabitencoded = []
        for array in listabit:
            listabitencoded.append(Hamming.__hamming_encode(array))
        return listabitencoded



    def CodeDataHammingObraz(obrazData):
        chunk_size = 4  # Size of each chunk
        obrazData_chunks = splitIntoChunks(obrazData, chunk_size)  # Split into 4-element chunks

        listabitencoded = []
        for chunk in obrazData_chunks:
            encoded_chunk = Hamming.__hamming_encode(chunk)
            listabitencoded.append(encoded_chunk)

        return listabitencoded

    @staticmethod
    def DecodeInputDataHamming(slowoCoded, jakoSlowo):
        slowoDecoded = []
        for i,array in enumerate(slowoCoded):
            slowoDecoded.append(Hamming.__hamming_decode(array,i+1))
        if (jakoSlowo):
            slowopodekode = Zlacz4BitoweArrayeNaSlowo(slowoDecoded)
            return slowopodekode
        else:
            return slowoDecoded
    def DecodeInputDataHammingObraz(slowoCoded):
        slowoDecoded = []
        for i,array in enumerate(slowoCoded):
            slowoDecoded.append(Hamming.__hamming_decode(array,i+1))
        return slowoDecoded

