# FEC Transmission Simulation – Reliability and Diagnostics of Digital Systems

## Project Overview
This project was developed as part of the course **Reliability and Diagnostics of Digital Systems 2**.  
Its goal is to model and analyze **data transmission with Forward Error Correction (FEC)** over two types of noisy communication channels:

- **Binary Symmetric Channel (BSC)**  
- **Gilbert–Elliott Channel**

We implemented and compared two families of error-correcting codes:

- **Hamming Code** – a simple block code, able to detect and correct single-bit errors  
- **Convolutional Code** – with **Viterbi decoding**, designed for sequential error correction  

The project includes:
- **Console prototype** for coding/decoding demonstration  
- **Statistical studies** of error correction efficiency (BER analysis, success intervals)  
- **Graphical User Interface (GUI)** for interactive visualization of transmission, noise, and error correction results  

---

## Theoretical Background

### Forward Error Correction (FEC)
FEC encodes data with redundancy, allowing detection and correction of errors **without retransmission**.  
General model:

![Transmission model](./Readmephotos/model.png)

### Hamming Code
- Adds parity bits at power-of-two positions (1, 2, 4, 8, …).  
- Detects and corrects **one-bit errors per block**.  
- Ineffective when **multiple errors** occur within the same block.  

Example encoding scheme:

![Hamming encoding](./Readmephotos/hamming_encode.png)

### Convolutional Codes
- Encode data sequentially using a **shift register** and linear combinations of current and previous bits.  
- Decoding performed via **Viterbi algorithm** using a trellis diagram.  
- Better suited for **burst errors**.  

Implementation snippet:

![Convolutional encoding](./Readmephotos/conv_encode.png)  

---

## Channel Models

### Binary Symmetric Channel (BSC)
- Each bit flips with fixed probability `p` (BER).  
- Models **independent random errors**.  

![BSC model](./Readmephotos/BSC.png)

### Gilbert–Elliott Channel
- Two states: **Good (G)** and **Bad (B)**.  
- Errors occur with low probability in state G, high probability in state B.  
- Models **burst/grouped errors**.  

![Gilbert–Elliott model](./Readmephotos/Gilbert-Elliot.png)

---

## Statistical Studies

We tested transmission of `Lorem Ipsum` text (245 characters) encoded with **Hamming** and **Convolutional** codes.

### Example – Hamming over BSC
- Errors corrected successfully at **low BER**.  
- Multiple errors in one block cannot be corrected.  

![Hamming example](./Readmephotos/hamming_working_example_1.png)  
![Group errors](./Readmephotos/hamming_working_example_group_error_1.png)

### Example – Convolutional over Gilbert–Elliott
- Performs well in channels with burst errors.  
- With poor channel parameters, some errors remain uncorrected.  

![Convolutional example](./Readmephotos/conv_working_example_1.png)

### Measured Data – Hamming over BSC
Sample test output table:

![Hamming data](./Readmephotos/Hamming_BSC_data.png)

Relation of **different characters vs BER**:

![Hamming BER test](./Readmephotos/Hamming_BSC_TEST1.png)

### Measured Data – Convolutional over BSC
Sample table and BER relation:

![Convolutional data](./Readmephotos/CONVOLUTIONAL_BSC_TABLE_Example.png)  
![Conv BER test](./Readmephotos/CONVOLUTIONAL_BSC_TEST1.png)

---

## Graphical User Interface (GUI)

A Python-based GUI was created for interactive experiments.  
Users can:  
- Import an image (e.g. `.bmp`)  
- Simulate transmission over BSC or Gilbert–Elliott channels  
- Apply Hamming or Convolutional codes  
- Visualize noise, corrected output, and pixel differences  

### Example GUI Window
![GUI main window](./Readmephotos/GUI_MAIN.png)

### Example Transmission (Image)
- Top-left: Original image  
- Top-right: Corrupted (no decoding)  
- Bottom-left: After decoding and correction  
- Bottom-right: Pixel differences  

Hamming over channels:

![Hamming image test](./Readmephotos/HAMMING-L-BSC-R-GILELIT.png)  

Convolutional over channels:

![Conv image test](./Readmephotos/CONVOLUTIONAL-L-BSC-R-GILELIT.png)  

---

## Installation & Usage

### Requirements
- Python 3.8+  
- Libraries: `numpy`, `matplotlib`, `commpy`  

### Installation
```bash
git clone https://github.com/KytryshAndrii/fec-transmission-simulation.git
cd fec-transmission-simulation
pip install -r requirements.txt
```

### Running Console Prototype
```
python hamming_console.py
python conv_console.py
```

### Running GUI
```
python gui_main.py
```
