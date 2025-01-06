import numpy as np
from PIL import Image
from commpy.channelcoding.convcode import Trellis, conv_encode, viterbi_decode
from commpy.channels import bsc
from multiprocessing import Pool
from Utils.HelperFunctions import SlowoNaTablice, decode_bits_to_string

class ConvolutionalCoder:
    K = 3  # Constraint length
    code_rate = (1, K)  # Rate 1/K
    generators = np.array([[5, 7]])
    trellis = Trellis(np.array([K]), generators)

    @staticmethod
    def encode(data_bits):
        data_bits = np.array(data_bits).flatten()
        encoded_bits = conv_encode(data_bits, ConvolutionalCoder.trellis)
        return encoded_bits.tolist()

    @staticmethod
    def decode(encoded_bits, tbDepth):
        encoded_bits_np = np.array(encoded_bits).flatten()
        decoded_bits = viterbi_decode(encoded_bits_np, ConvolutionalCoder.trellis, tb_depth=tbDepth)
        return decoded_bits.tolist()

    @staticmethod
    def CodeData(slowo, JestObrazem):
        if not JestObrazem:
            slowo = SlowoNaTablice(slowo)
        encoded_bits = ConvolutionalCoder.encode(slowo)
        return encoded_bits

    @staticmethod
    def Decode(zakodowaneSlowo, tbDepth, jakoSlowo, jestObrazem):
        if jestObrazem:
            decoded_bits = ConvolutionalCoder.decode(zakodowaneSlowo, tbDepth)
            return decoded_bits

        expected_bit_length = len(zakodowaneSlowo) // 2
        decoded_bits = ConvolutionalCoder.decode(zakodowaneSlowo, tbDepth)
        decoded_bits = decoded_bits[:expected_bit_length]

        if len(decoded_bits) % 8 != 0:
            decoded_bits = decoded_bits[:len(decoded_bits) - (len(decoded_bits) % 8)]

        if jakoSlowo:
            slowoCale = decode_bits_to_string(decoded_bits)
            return slowoCale
        else:
            return decoded_bits