import numpy as np
from commpy.channelcoding.convcode import Trellis, conv_encode, viterbi_decode

from Utils.HelperFunctions import SlowoNaTablice, decode_bits_to_string


class ConvolutionalCoder:
    # Generator trellis dla kodu splotowego (2,1,3)
    trellis = Trellis(np.array([3]), np.array([[7, 5]]))  # Generatory (7 i 5 w oktalnej)

    @staticmethod
    def __Encode(data_bits):
        """
        Statyczna metoda do kodowania danych splotowych.
        :param data_bits: Tablica bitów do zakodowania (1D numpy array)
        :return: Zakodowana tablica bitów
        """
        # Kodowanie splotowe
        data_bits = np.array(data_bits).flatten()
        encoded_bits = conv_encode(data_bits, ConvolutionalCoder.trellis)
        return encoded_bits.tolist()

    @staticmethod
    def __Decode(encoded_bits, tbDepth):
        """
        Statyczna metoda do dekodowania zakodowanych danych splotowych przy użyciu algorytmu Viterbiego.
        :param encoded_bits: Zakodowana tablica bitów (1D numpy array)
        :param tbDepth: Głębokość śledzenia (traceback depth) dla dekodowania Viterbi
        :return: Odkodowana tablica bitów
        """
        # Convert encoded_bits to a flattened NumPy array to ensure it is 1D
        encoded_bits_np = np.array(encoded_bits).flatten()

        # Decode using the Viterbi algorithm
        decoded_bits = viterbi_decode(encoded_bits_np, ConvolutionalCoder.trellis, tb_depth=tbDepth)

        # Convert the output back to a list for consistency
        return decoded_bits.tolist()

    @staticmethod
    def Zakoduj(slowo):
        """
        Funkcja kodująca całe słowo (tablicę bitów) przy użyciu kodera splotowego.
        :param slowo: Tablica bitów reprezentująca słowo (np. wynik SlowoNaTablice)
        :return: Zakodowana tablica bitów
        """
        tablica_bitow = SlowoNaTablice(slowo)  # Konwersja słowa na tablicę bitów
        encoded_bits = ConvolutionalCoder.__Encode(tablica_bitow)
        return encoded_bits

    @staticmethod
    def Dekoduj(zakodowaneSlowo, tbDepth, jakoSlowo):
        """
        Funkcja dekodująca zakodowane dane splotowe na pierwotne słowo.
        :param zakodowaneSlowo: Zakodowana tablica bitów
        :param tbDepth: Głębokość śledzenia dla dekodera Viterbi
        :param jakoSlowo: Flaga, czy zwrócić wynik jako słowo
        :return: Zdekodowane dane w formie tablicy bitów lub słowa
        """
        # Estimate the number of bits in the original word (before encoding)
        expected_bit_length = len(zakodowaneSlowo) // 2  # Adjust based on rate (e.g., 1/2 rate)

        # Decode the encoded bits
        decoded_bits = ConvolutionalCoder.__Decode(zakodowaneSlowo, tbDepth)

        # Truncate the decoded bits to match the expected original length
        decoded_bits = decoded_bits[:expected_bit_length]

        # Ensure decoded_bits length is a multiple of 8 for conversion
        if len(decoded_bits) % 8 != 0:
            # Trim the excess bits if needed to make the length a multiple of 8
            decoded_bits = decoded_bits[:len(decoded_bits) - (len(decoded_bits) % 8)]

        if jakoSlowo:
            # Convert the trimmed decoded bits back to a string
            slowoCale = decode_bits_to_string(decoded_bits)
            return slowoCale
        else:
            return decoded_bits  # Return as bit array if not converting to string

