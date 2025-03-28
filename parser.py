

def analyze_log(filepath, reference_ciphertext):
    fault_count = 0
    reset_count = 0

    with open(filepath, 'r') as file:
        for line in file:
            if "board no response" in line:
                reset_count += 1
            elif "AES encryption successful" in line:
                continue  
            elif "[" in line and "]" in line:
                try:
                    parts = line.split(" - ", 1)
                    if len(parts) < 2:
                        continue
                    cipher_line = parts[1].strip()
                    


    print("Total Faults Detected: {}".format(fault_count))
    print("Total Resets (board no response): {}".format(reset_count))

reference_ciphertext = ['\xec', '\xfa', '\x81', '\x88', 'h', '"', 'G', '.', '-', '\x0b', '\x08', '\x88', 'Z', '\x16', '\xfd', '\x01']
log_file = "glitch_log1743033460.95.txt"  
analyze_log(log_file, reference_ciphertext)
