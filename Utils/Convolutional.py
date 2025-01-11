import numpy as np
from commpy.channelcoding.convcode import Trellis, conv_encode, viterbi_decode
from Utils.HelperFunctions import word_to_list, decode_bits_to_string

class ConvolutionalCoder:
    K = 3  # Constraint length
    code_rate = (1, K)  # Rate 1/K
    generators = np.array([[5, 7]])
    trellis = Trellis(np.array([K]), generators)

    @staticmethod
    def __Encode(data_bits):
        """
        Static method to encode spliced data.
        :param data_bits: Array of bits to be encoded (1D numpy array)
        :return: Encoded array of bits
        """
        data_bits = np.array(data_bits).flatten()
        encoded_bits = conv_encode(data_bits, ConvolutionalCoder.trellis)
        print(len(encoded_bits.tolist()))
        return encoded_bits.tolist()

    @staticmethod
    def __Decode(encoded_bits, tbDepth):
        """
        Static method to decode encoded spliced data using the Viterbi algorithm.
        :param encoded_bits: Encoded bit array (1D numpy array)
        :param tbDepth: Traceback depth for Viterbi decoding
        :return: Decoded bit array
        """
        encoded_bits_np = np.array(encoded_bits).flatten()
        decoded_bits = viterbi_decode(encoded_bits_np, ConvolutionalCoder.trellis, tb_depth=tbDepth)
        return decoded_bits.tolist()

    @staticmethod
    def CodeData(word, isPicture):
        """
            A function that encodes an entire word (array of bits) using a splice encoder.
            :param word: An array of bits representing the word (e.g. the result of WordTable).
            :param isPicture: A boolean value which defines the input data type
            :return: Encoded bit array
        """
        if not isPicture:
            word = word_to_list(word)
        encoded_bits = ConvolutionalCoder.__Encode(word)
        return encoded_bits

    @staticmethod
    def Decode(codedWord, tbDepth, isAWord, isPicture):
        """
           A function that decodes encoded splice data into the original word.
            :param encodedWord: Encoded bit array
            :param tbDepth: Tracking depth for the Viterbi decoder
            :param asWord: Flag whether to return the result as word
            :param isPicture: A boolean value which defines the input data type
            :return: Decoded data as bit array or word
        """
        if isPicture:
            decoded_bits = ConvolutionalCoder.__Decode(codedWord, tbDepth)
            return decoded_bits

        expected_bit_length = len(codedWord) // 2
        decoded_bits = ConvolutionalCoder.__Decode(codedWord, tbDepth)
        decoded_bits = decoded_bits[:expected_bit_length]

        if len(decoded_bits) % 8 != 0:
            decoded_bits = decoded_bits[:len(decoded_bits) - (len(decoded_bits) % 8)]

        if isAWord:
            wholeWord = decode_bits_to_string(decoded_bits)
            return wholeWord
        else:
            return decoded_bits