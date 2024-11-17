from Utils.BSC import *
from Utils.GilbertElliot import *
from Utils.Hamming import *
from Utils.HelperFunctions import *
from Utils.Convolutional import *
def main():

    channelModel = int(input("Enter the channel model:      (1 - BSC, 2- Gilbert-Elliott) \n"))
    codingType = int(input("Enter the type of coding:       (1 - Hamming, 2 - Convolutional) \n"))
    inputData = input("Enter the input data:\n")

    if codingType == 1:
        inputDataCoded = Hamming.CodeDataHamming(inputData)
        print(inputData)

    elif codingType == 2:
        inputDataCoded = ConvolutionalCoder.CodeData(inputData)
        print(inputData)

    else: print("Invalid input")

    if channelModel == 1:
        ber = float(input("Enter bit error rate: "))

        if codingType == 1:
            inputDataCodedAndNoise, errorList = bsc_channel_transmission(inputDataCoded, ber)
            print(inputDataCodedAndNoise)
            print(errorList)
            inputDataDecoded = Hamming.DecodeInputDataHamming(inputDataCodedAndNoise, True)
            print(inputDataDecoded)

        elif codingType == 2:
            inputDataCodedAndNoise, errorList = bsc_channel_transmission_splot(inputDataCoded, ber)
            inputDataDecoded = ConvolutionalCoder.Decode(inputDataCodedAndNoise, 10, True)
            print(inputDataDecoded)
            print(errorList)

        else: print("Invalid input")


    elif channelModel == 2:
        chanceForGood = float(input("Enter the chance for good: "))
        chanceForBad = float(input("Enter the chance for bad: "))
        p_err_good = float(input("Enter the probability for good: "))
        p_err_bad = float(input("Enter the probability for bad: "))

        if codingType == 1:
            channel = GilbertElliottChannel(chanceForBad, chanceForGood, p_err_good, p_err_bad)
            inputDataCodedAndNoise, errorList = channel.transmitHamming(-inputDataCoded)
            print(inputDataCodedAndNoise)
            print(errorList)
            inputDataDecoded = Hamming.DecodeInputDataHamming(inputDataCodedAndNoise, True)
            print(inputDataDecoded)

        elif codingType == 2:
            channel = GilbertElliottChannel(chanceForBad, chanceForGood, p_err_good, p_err_bad)
            inputDataCodedAndNoise, errorList = channel.transmitConvolutional(inputDataCoded)
            print(inputDataCodedAndNoise)
            print(errorList)
            inputDataDecoded = ConvolutionalCoder.Decode(inputDataCodedAndNoise, 10, True)
            print(inputDataDecoded)

        else: print("Invalid input")

    else: print("Invalid input")

if __name__ == '__main__':
    main()

