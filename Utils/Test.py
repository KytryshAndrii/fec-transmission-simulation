import numpy as np
import time
from Utils.BSC import *
from Utils.GilbertElliot import *
from Utils.Hamming import *
from Utils.HelperFunctions import *
from Utils.Convolutional import *
from PIL import Image
import multiprocessing as mp
import pandas as pd

# Utility functions for image handling
def load_bmp_image(file_path):
    """Load an image and convert it to an RGB numpy array."""
    image = Image.open(file_path).convert('RGB')
    return np.array(image)


def save_bmp_image(data, file_path, original_shape):
    """Save a numpy array as a BMP image."""
    image = Image.fromarray(data.reshape(original_shape).astype(np.uint8))
    image.save(file_path)


def image_to_bits(image):
    """Convert image data to a bit array."""
    return np.unpackbits(image)


def bits_to_image(bits, shape):
    """Convert bit array back to image data."""
    return np.packbits(bits).reshape(shape)


def split_image(image, parts=4):
    """Split an image into specified number of parts."""
    height = image.shape[0]
    split_height = height // parts
    return [image[i * split_height:(i + 1) * split_height] for i in range(parts)]


def merge_image(parts):
    """Merge split image parts back into a single image."""
    return np.vstack(parts)


# Encoding and Decoding Handlers
def encode_data(data, coding_type, is_image=False):
    if coding_type == 1:  # Hamming
        return Hamming.CodeDataHammingObraz(data) if is_image else Hamming.CodeDataHamming(data)
    elif coding_type == 2:  # Convolutional
        return ConvolutionalCoder.CodeData(slowo=data, JestObrazem=is_image)
    else:
        raise ValueError("Invalid coding type selected")


def decode_data(data, coding_type, tb_depth, is_image=False):
    if coding_type == 1:  # Hamming
        return Hamming.DecodeInputDataHammingObraz(data) if is_image else Hamming.DecodeInputDataHamming(data,
                                                                                                         jakoSlowo=True)
    elif coding_type == 2:  # Convolutional
        return ConvolutionalCoder.Decode(data, tb_depth, not is_image, is_image)
    else:
        raise ValueError("Invalid coding type selected")


# Channel Transmission Handlers
def transmit_bsc(data, ber, coding_type, is_image=False):
    if coding_type == 1:  # Hamming
        return bsc_channel_transmission_hamming(data, ber)
    elif coding_type == 2:  # Convolutional
        return bsc_channel_transmission_splot(data, ber)
    else:
        raise ValueError("Invalid coding type selected")


def transmit_gilbert_elliott(data, channel_params, coding_type, is_image=False):
    channel = GilbertElliottChannel(*channel_params)
    if coding_type == 1:  # Hamming
        return channel.transmitHamming(data)
    elif coding_type == 2:  # Convolutional
        return channel.transmitConvolutional(data)
    else:
        raise ValueError("Invalid coding type selected")


# Main Application Logic
def process_text_data(input_data, coding_type, channel_model, channel_params):
    encoded_data = encode_data(input_data, coding_type)

    if channel_model == 1:  # BSC
        transmitted_data, error_count, actual_ber_observed = transmit_bsc(encoded_data, channel_params, coding_type)
    elif channel_model == 2:  # Gilbert-Elliott
        transmitted_data, error_count, actual_ber_observed = transmit_gilbert_elliott(encoded_data, channel_params, coding_type)
    else:
        raise ValueError("Invalid channel model selected")

    decoded_data = decode_data(transmitted_data, coding_type, tb_depth=3)
    return decoded_data, error_count, actual_ber_observed


def decode_image_part(args):
    """Decode a single image part with the specified parameters."""
    encoded_data, coding_type, tb_depth, part_shape = args
    decoded_bits = decode_data(encoded_data, coding_type, tb_depth, is_image=True)
    decoded_part = bits_to_image(decoded_bits[:np.prod(part_shape) * 8], part_shape)
    return decoded_part


def process_image_data(image, coding_type, channel_model, channel_params):
    """Process image data by splitting, encoding, transmitting, and decoding with multiprocessing."""
    image_parts = split_image(image)  # Split the image into parts
    encoded_parts = [encode_data(image_to_bits(part), coding_type, is_image=True) for part in image_parts]

    transmitted_parts = []
    for encoded_data in encoded_parts:
        if channel_model == 1:  # BSC
            transmitted_data, _ = transmit_bsc(encoded_data, channel_params, coding_type, is_image=True)
        elif channel_model == 2:  # Gilbert-Elliott
            transmitted_data, _ = transmit_gilbert_elliott(encoded_data, channel_params, coding_type, is_image=True)
        else:
            raise ValueError("Invalid channel model selected")
        transmitted_parts.append(transmitted_data)

    # Prepare arguments for multiprocessing decoding
    decode_args = [
        (transmitted_data, coding_type, 3, part.shape)
        for transmitted_data, part in zip(transmitted_parts, image_parts)
    ]

    # Decode using multiprocessing
    with mp.Pool(processes=mp.cpu_count()) as pool:
        decoded_parts = pool.map(decode_image_part, decode_args)

    final_image = merge_image(decoded_parts)  # Merge parts back into a single image
    return final_image

def calculate_number_of_errors(decoded_data, input_data):
    number_of_errors = 0
    for i in range(len(decoded_data)):
        if decoded_data[i] != input_data[i]:
            number_of_errors += 1
    return number_of_errors


def main():
    print("Welcome to the Data Transmission Simulator!")

    # User inputs
    data_type = 1
    channel_model = 1
    coding_type = int(input("Enter the type of coding: (1 - Hamming, 2 - Convolutional)\n"))
    input_data = input("Enter the input text data:\n")
    number_of_tests = int (input("Enter the number of tests:\n"))

    test_number = 1

    df = pd.DataFrame({})

    while test_number <= number_of_tests:
        ber = 0
        channel_params = ber
        entered_ber_list = []
        actual_ber_list = []
        number_of_errors_list = []
        separator_list = []
        number_of_detected_errors_list = []
        number_of_corrected_errors_list = []

        while ber <= 0.02:

            decoded_data, error_count, actual_ber_observed= process_text_data(input_data, coding_type, channel_model, channel_params)
            print("Decoded Text Data:")
            print(decoded_data)
            print("Actual number of errors: ", calculate_number_of_errors(decoded_data, input_data), "\n")
            number_of_errors = calculate_number_of_errors(decoded_data, input_data)
            number_of_errors_list.append(number_of_errors)
            entered_ber_list.append(ber)
            print(error_count)
            if coding_type == 1:
                actual_ber_list.append(actual_ber_observed)
                number_of_detected_errors_list.append(error_count)
                number_of_corrected_errors_list.append(error_count-number_of_errors)
            elif coding_type == 2:
                actual_ber_list.append(actual_ber_observed)
                number_of_detected_errors_list.append(error_count)
                number_of_corrected_errors_list.append(error_count - number_of_errors)
            else:
                print("Invalid coding type selected")
                return


            separator_list.append(" ")
            ber += 0.0001
            channel_params = ber

        entered_ber_column_name = f"Entered BER test {test_number}"
        actual_ber_column_name = f"Actual BER test {test_number}"
        number_of_errors_column_name = f"Number of errors test {test_number}"
        number_of_detected_errors_column_name = f"Number of detected errors test {test_number}"
        number_of_corrected_errors_column_name = f"Number of corrected errors test {test_number}"
        n=f"Test {test_number}"

        df[n] = separator_list
        df[entered_ber_column_name] = entered_ber_list
        df[actual_ber_column_name] = actual_ber_list
        df[number_of_errors_column_name] = number_of_errors_list
        df[number_of_detected_errors_column_name] = number_of_detected_errors_list
        df[number_of_corrected_errors_column_name] = number_of_corrected_errors_list


        test_number += 1

    if coding_type == 1:
        df.to_excel("Statystyki_Hamming_Projekt_NiDUC.xlsx", index = False)
    elif coding_type == 2:
        df.to_excel("Statystyki_Convolutional_Projekt_NiDUC.xlsx", index=False)
    else:
        raise ValueError("Invalid coding type selected")


    #start_time = time.time()
    #elapsed_time = time.time() - start_time
    #print(f"\nElapsed time: {elapsed_time:.2f} seconds")


if __name__ == '__main__':
    main()
