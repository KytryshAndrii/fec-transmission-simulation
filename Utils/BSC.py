import random

def bsc_channel_transmission(bit_list, ber):
    """
    Simulate transmission through a BSC channel for each sublist of bits in the list.

    bit_list: list where each element is a list of bits (e.g., [1, 0, 1])
    ber: bit error rate (BER)

    Returns the list of received bits and the list of errors.
    """
    received_list = []
    error_list = []
    total_bits = 0
    error_count = 0  # Track total errors for analysis

    for bits in bit_list:
        received_bits = []
        error_bits = []
        for bit in bits:
            error = random.random() < ber  # Random error for each bit
            error_count += error  # Count each error for tracking
            total_bits += 1
            received_bit = (bit + int(error)) % 2  # Ensure type consistency
            received_bits.append(int(received_bit))  # Convert to int
            error_bits.append(int(error))  # 1 indicates error, 0 no error

        received_list.append(received_bits)
        error_list.append(error_bits)

    return received_list, error_list


def bsc_channel_transmission_splot(bit_list, ber):
    """
    Simulate transmission through a BSC channel for each bit in the list.

    bit_list: list of bits (e.g., [1, 0, 1])
    ber: bit error rate (BER)

    Returns the list of received bits and the list of errors.
    """
    received_list = []
    error_list = []
    total_bits = len(bit_list)  # Total number of bits transmitted
    error_count = 0  # Track total errors for analysis

    for bit in bit_list:
        error = random.random() < ber  # Random error for each bit
        error_count += error  # Count each error for tracking
        received_bit = (bit + int(error)) % 2  # Ensure type consistency with int(error)
        received_list.append(int(received_bit))  # Convert to int
        error_list.append(int(error))  # 1 indicates error, 0 no error

    # Print the observed BER
    print(f"Actual BER observed: {error_count / total_bits:.3f}")  # Compare to target BER

    return received_list, error_list
