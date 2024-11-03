import numpy as np
class GilbertElliottChannel:
    def __init__(self, chance_for_bad, chance_for_good, p_err_good, p_err_bad):
        self.chance_for_bad = chance_for_bad  # Przejście z dobrego do złego (szansa od 0.0 do 1.0)
        self. chance_for_good=  chance_for_good  # Przejście ze złego do dobrego (szansa od 0.0 do 1.0)
        self.p_err_good = p_err_good  # BER w stanie dobrym (szansa od 0.0 do 1.0)
        self.p_err_bad = p_err_bad    # BER w stanie złym (szansa od 0.0 do 1.0)
        self.state = 0  # 0 - dobry, 1 - zły

    def transmit(self, bitsarray):
        receivedArray = []
        errorsArray = []
        for array in bitsarray:
            received = []
            errors = []
            for bit in array:
                # Aktualizacja stanu
                if self.state == 0:
                    if np.random.rand() < self.chance_for_bad:
                        self.state = 1
                else:
                    if np.random.rand() < self.chance_for_good:
                        self.state = 0
                # Błąd w zależności od stanu
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
                if (error==True):
                    errorstemp.append(1)
                else:
                    errorstemp.append(0)

            errorsArray.append(errorstemp)
        return receivedArray, errorsArray