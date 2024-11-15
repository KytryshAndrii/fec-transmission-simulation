import numpy as np
import time
from Utils.BSC import *
from Utils.GilbertElliot import *
from Utils.Hamming import *
from Utils.HelperFunctions import *
from Utils.Convolutional import *
from PIL import Image

def load_bmp_image(file_path):
    image = Image.open(file_path).convert('RGB')
    return np.array(image)

def save_bmp_image(data, file_path, original_shape):
    image = Image.fromarray(data.reshape(original_shape).astype(np.uint8))
    image.save(file_path)

def image_to_bits(image):
    return np.unpackbits(image)

def bits_to_image(bits, shape):
    return np.packbits(bits).reshape(shape)

def main():
    dataType = int(input("Enter data type: 1 - Text, 2 - Image\n"))
    channelModel = int(input("Enter the channel model: (1 - BSC, 2 - Gilbert-Elliott) \n"))
    codingType = int(input("Enter the type of coding: (1 - Hamming, 2 - Convolutional) \n"))
    tbDepthSetting = 3


    if dataType == 1:
        inputData = input("Enter the input data:\n")
    elif dataType == 2:
        image = load_bmp_image("image.bmp")
        image_shape = image.shape
        inputData = image_to_bits(image)
    else:
        print("Invalid input")
        return

    if codingType == 1:
        if dataType == 2:
            inputDataCoded = Hamming.CodeDataHammingObraz(inputData)
        elif dataType == 1:
            inputDataCoded = Hamming.CodeDataHamming(inputData)

    elif codingType == 2:
        if dataType == 2:

            inputDataCoded = ConvolutionalCoder.CodeData(slowo=inputData, JestObrazem=True)
        elif dataType == 1:
            inputDataCoded = ConvolutionalCoder.CodeData(slowo=inputData, JestObrazem=False)
    else:
        print("Invalid input")
        return



    if channelModel == 1:
        ber = float(input("Enter bit error rate: "))
        start_time = time.time()  # Start the timer
        if codingType == 1:
            inputDataCodedAndNoise, errorList = bsc_channel_transmission(inputDataCoded, ber)
            if dataType == 2:
                inputDataDecoded = Hamming.DecodeInputDataHammingObraz(inputDataCodedAndNoise)
                print(inputDataDecoded)
            else:
                inputDataDecoded = Hamming.DecodeInputDataHamming(inputDataCodedAndNoise, jakoSlowo=True)
                print(inputDataDecoded)

        elif codingType == 2:
            inputDataCodedAndNoise, errorList = bsc_channel_transmission_splot(inputDataCoded, ber)
            if dataType == 2:
                inputDataDecoded = ConvolutionalCoder.Decode(inputDataCodedAndNoise, tbDepthSetting, False, True)
            elif dataType == 1:
                inputDataDecoded = ConvolutionalCoder.Decode(inputDataCodedAndNoise, tbDepthSetting, True, False)
                print(inputDataDecoded)
        else:
            print("Invalid input")
            return

    elif channelModel == 2:
        chanceForGood = float(input("Enter the chance for returning to good state: "))
        chanceForBad = float(input("Enter the chance for going into bad state: "))
        p_err_good = float(input("Enter the probability for error in good state: "))
        p_err_bad = float(input("Enter the probability for error in bad state: "))
        start_time = time.time()  # Start the timer

        if codingType == 1:
            channel = GilbertElliottChannel(chanceForBad, chanceForGood, p_err_good, p_err_bad)
            inputDataCodedAndNoise, errorList = channel.transmitHamming(inputDataCoded)
            if dataType == 2:
                inputDataDecoded = Hamming.DecodeInputDataHammingObraz(inputDataCodedAndNoise)
                print(inputDataDecoded)
            else:
                inputDataDecoded = Hamming.DecodeInputDataHamming(inputDataCodedAndNoise, jakoSlowo=True)
                print(inputDataDecoded)

        elif codingType == 2:
            channel = GilbertElliottChannel(chanceForBad, chanceForGood, p_err_good, p_err_bad)
            inputDataCodedAndNoise, errorList = channel.transmitConvolutional(inputDataCoded)
            if dataType == 2:
                inputDataDecoded = ConvolutionalCoder.Decode(inputDataCodedAndNoise, tbDepthSetting, False, True)
            elif dataType == 1:
                inputDataDecoded = ConvolutionalCoder.Decode(inputDataCodedAndNoise, tbDepthSetting, True, False)
                print(inputDataDecoded)
        else:
            print("Invalid input")
            return

    else:
        print("Invalid input")
        return

    if dataType == 2:
        decoded_bits = inputDataDecoded[:inputData.size]
        decoded_image = bits_to_image(decoded_bits, image_shape)
        save_bmp_image(decoded_image, "decoded_imagesample.bmp", image_shape)

    end_time = time.time()  # End the timer
    elapsed_time = end_time - start_time  # Calculate elapsed time
    print(f"Elapsed time: {elapsed_time} seconds")

if __name__ == '__main__':
    main()