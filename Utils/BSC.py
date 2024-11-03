import random

def bsc_channel_transmission(bit_list, ber):
    """
    Symuluje transmisję przez kanał BSC dla każdej podlisty bitów w liście.

    bit_list: lista, gdzie każdy element to lista bitów (np. [1, 0, 1])
    ber: współczynnik błędów bitowych (bit error rate, BER)

    Zwraca listę otrzymanych bitów i listę błędów.
    """
    received_list = []
    error_list = []

    for bits in bit_list:
        received_bits = []
        error_bits = []
        for bit in bits:
            error = random.random() < ber  # Losowanie błędu dla każdego bitu
            received_bit = (bit + error) % 2  # Modulo 2 do symulacji odbioru z błędem
            received_bits.append(int(received_bit))  # Konwersja na int
            error_bits.append(int(error))  # 1 oznacza błąd, 0 brak błędu

        received_list.append(received_bits)
        error_list.append(error_bits)

    return received_list, error_list


def bsc_channel_transmission_splot(bit_list, ber):
    """
    Symuluje transmisję przez kanał BSC dla każdej podlisty bitów w liście.

    bit_list: lista, gdzie każdy element to lista bitów (np. [1, 0, 1])
    ber: współczynnik błędów bitowych (bit error rate, BER)

    Zwraca listę otrzymanych bitów i listę błędów.
    """
    received_list = []
    error_list = []

    for bit in bit_list:
        received_bits = []
        error_bits = []
        error = random.random() < ber  # Losowanie błędu dla każdego bitu
        received_bit = (bit + error) % 2  # Modulo 2 do symulacji odbioru z błędem
        received_bits.append(int(received_bit))  # Konwersja na int
        error_bits.append(int(error))  # 1 oznacza błąd, 0 brak błędu

        received_list.append(received_bits)
        error_list.append(error_bits)

    return received_list, error_list
