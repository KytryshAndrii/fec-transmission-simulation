import numpy as np
import time
from Utils.BSC import *
from Utils.GilbertElliot import *
from Utils.Hamming import *
from Utils.HelperFunctions import *
from Utils.Convolutional import *
from PIL import Image
import multiprocessing as mp

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
        transmitted_data, _, actual_ber_observed = transmit_bsc(encoded_data, channel_params, coding_type)
    elif channel_model == 2:  # Gilbert-Elliott
        transmitted_data, _ = transmit_gilbert_elliott(encoded_data, channel_params, coding_type)
    else:
        raise ValueError("Invalid channel model selected")

    decoded_data = decode_data(transmitted_data, coding_type, tb_depth=3)
    return decoded_data


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


def main():
    print("Welcome to the Data Transmission Simulator!")

    # User inputs
    data_type = int(input("Enter data type: 1 - Text, 2 - Image\n"))
    channel_model = int(input("Enter the channel model: (1 - BSC, 2 - Gilbert-Elliott)\n"))
    coding_type = int(input("Enter the type of coding: (1 - Hamming, 2 - Convolutional)\n"))

    # Channel parameters
    if channel_model == 1:
        ber = float(input("Enter bit error rate: "))
        channel_params = ber
    elif channel_model == 2:
        chance_good = float(input("Enter the chance for returning to good state: "))
        chance_bad = float(input("Enter the chance for going into bad state: "))
        p_err_good = float(input("Enter the probability for error in good state: "))
        p_err_bad = float(input("Enter the probability for error in bad state: "))
        channel_params = (chance_bad, chance_good, p_err_good, p_err_bad)
    else:
        print("Invalid channel model")
        return

    start_time = time.time()

    if data_type == 1:  # Text data
        input_data = input("Enter the input text data:\n")
        decoded_data = process_text_data(input_data, coding_type, channel_model, channel_params)
        print("Decoded Text Data:")
        print(decoded_data)


    elif data_type == 2:  # Image data
        image = load_bmp_image("image.bmp")
        decoded_image = process_image_data(image, coding_type, channel_model, channel_params)
        save_bmp_image(decoded_image, "decoded_image.bmp", decoded_image.shape)
        print("Decoded image saved as 'decoded_image.bmp'")

    else:
        print("Invalid data type selected")
        return


    elapsed_time = time.time() - start_time
    print(f"\nElapsed time: {elapsed_time:.2f} seconds")


if __name__ == '__main__':
    main()