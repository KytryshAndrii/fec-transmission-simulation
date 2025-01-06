import multiprocessing as mp
from Utils.Hamming import *
from Utils.Convolutional import *
from Utils.BSC import *
from Utils.GilbertElliot import *

def save_bmp_image(data, file_path, original_shape):
    """Save a numpy array as a BMP image."""
    image = Image.fromarray(data.reshape(original_shape).astype(np.uint8))
    image.save(file_path)

def bits_to_image(bits, shape):
    """Convert bit array back to image data."""
    return np.packbits(bits).reshape(shape)

def image_to_bits(image):
    """Convert image data to a bit array."""
    return np.unpackbits(image)

def split_image(image, parts=4):
    """Split an image into specified number of parts."""
    height = image.shape[0]
    split_height = height // parts
    return [image[i * split_height:(i + 1) * split_height] for i in range(parts)]


def merge_image(parts):
    """Merge split image parts back into a single image."""
    return np.vstack(parts)

def transmit_bsc(data, ber, coding_type):
    if coding_type == 1:  # Hamming
        return bsc_channel_transmission_hamming(data, ber)
    elif coding_type == 2:  # Convolutional
        return bsc_channel_transmission_splot(data, ber)
    else:
        raise ValueError("Invalid coding type selected")


def transmit_gilbert_elliott(data, channel_params, coding_type):
    channel = GilbertElliottChannel(*channel_params)
    if coding_type == 1:  # Hamming
        return channel.transmitHamming(data)
    elif coding_type == 2:  # Convolutional
        return channel.transmitConvolutional(data)
    else:
        raise ValueError("Invalid coding type selected")

def encode_data(data, coding_type,):
    if coding_type == 1:  # Hamming
        return Hamming.CodeDataHammingObraz(data)
    elif coding_type == 2:  # Convolutional
        return ConvolutionalCoder.CodeData(slowo=data, JestObrazem=True)
    else:
        raise ValueError("Invalid coding type selected")

def decode_data(data, coding_type, tb_depth):
    if coding_type == 1:  # Hamming
        return Hamming.DecodeInputDataHammingObraz(data)
    elif coding_type == 2:  # Convolutional
        return ConvolutionalCoder.Decode(data, tb_depth, False, True)
    else:
        raise ValueError("Invalid coding type selected")

def decode_image_part(args):
    """Decode a single image part with the specified parameters."""
    encoded_data, coding_type, tb_depth, part_shape = args
    decoded_bits = decode_data(encoded_data, coding_type, tb_depth)
    decoded_part = bits_to_image(decoded_bits[:np.prod(part_shape) * 8], part_shape)
    return decoded_part

