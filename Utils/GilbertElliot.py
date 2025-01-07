import numpy as np


class GilbertElliottChannel:
    def __init__(self, chance_for_bad, chance_for_good, p_err_good, p_err_bad):
        """
            Initialize the Gilbert-Elliott channel with transition probabilities and BERs for each state.

            :param chance_for_bad: Probability of transitioning from the good state to the bad state (0.0 to 1.0).
            :param chance_for_good: Probability of transitioning from the bad state to the good state (0.0 to 1.0).
            :param p_err_good: Bit error rate (BER) in the good state (0.0 to 1.0).
            :param p_err_bad: Bit error rate (BER) in the bad state (0.0 to 1.0).
        """
        self.chance_for_bad = chance_for_bad
        self.chance_for_good = chance_for_good
        self.p_err_good = p_err_good
        self.p_err_bad = p_err_bad
        self.state = 0

    def transmitHamming(self, bitsarray):
        """
            Simulate the transmission of data encoded with Hamming code over the Gilbert-Elliott channel.

            :param bitsarray: A list of lists, where each inner list contains a 7-bit encoded Hamming code.
            :return: A tuple:
                    - receivedArray: A list of lists, where each inner list contains the received bits after potential errors.
                    - errorsArray: A list of lists, where each inner list contains 1s (errors) or 0s (no errors).
        """
        receivedArray = []
        errorsArray = []
        for array in bitsarray:
            received = []
            errors = []
            for bit in array:
                # State update
                if self.state == 0:
                    if np.random.rand() < self.chance_for_bad:
                        self.state = 1
                else:
                    if np.random.rand() < self.chance_for_good:
                        self.state = 0
                # Error depending on the state
                if self.state == 0:
                    error = np.random.rand() < self.p_err_good
                else:
                    error = np.random.rand() < self.p_err_bad
                errors.append(error)
                received_bit = (bit + int(error)) % 2
                received.append(received_bit)
            receivedArray.append(received)
            errorstemp = []
            for error in errors:
                if (error == True):
                    errorstemp.append(1)
                else:
                    errorstemp.append(0)
            errorsArray.append(errorstemp)

        errorsArray = np.array(errorsArray) #glupi trik na splaszczenie tablicy
        errorsArray.flatten()
        errorsArray = errorsArray.tolist()
        return receivedArray, errorsArray

    def transmitConvolutional(self, bitsarray):
        """
            Simulate the transmission of data encoded with convolutional coding over the Gilbert-Elliott channel.

            :param bitsarray: A list of bits (1D array), where each bit is part of convolutionally encoded data.
            :return: A tuple:
                - receivedArray: A list of received bits after potential errors.
                - errorsArray: A list of 1s (errors) or 0s (no errors).
        """
        receivedArray = []
        errorsArray = []
        for bit in bitsarray:
            received = []
            errors = []

            # Aktualizacja stanu
            if self.state == 0:
                if np.random.rand() < self.chance_for_bad:
                    self.state = 1
            else:
                if np.random.rand() < self.chance_for_good:
                    self.state = 0
            # Error depending on the state
            if self.state == 0:
                error = np.random.rand() < self.p_err_good
            else:
                error = np.random.rand() < self.p_err_bad
            errors.append(error)
            received_bit = (bit + int(error)) % 2
            received.append(received_bit)
            receivedArray.append(received)
            errorstemp = []
            for error in errors:
                if (error == True):
                    errorstemp.append(1)
                else:
                    errorstemp.append(0)

            errorsArray.append(errorstemp)
        errorsArray = np.array(errorsArray) #glupi trik na splaszczenie tablicy
        errorsArray.flatten()
        errorsArray = errorsArray.tolist()
        return receivedArray, errorsArray