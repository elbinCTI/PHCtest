# import string
# import random
# import pickle as P
# import os

# # Configuration for the matrix size
# # 1 header + 95 random columns
# MAX_INDEX = 95 

# def _load_matrix(file_path):
#     """
#     Helper function to load the encryption matrix from a pickle file.
#     """
#     # Ensure extension exists
#     if not file_path.endswith('.dat'):
#         file_path += '.dat'

#     cs = list()
    
#     if not os.path.exists(file_path):
#         print(f"File not found: {file_path}")
#         return None

#     try:
#         with open(file_path, mode="rb") as f:
#             while True:
#                 try:
#                     y = P.load(f)
#                     # Skip the header row ['ch', '1', '2'...]
#                     if y[0] == 'ch':
#                         pass
#                     else:
#                         cs.append(y)
#                 except EOFError:
#                     break
#         return cs
#     except Exception as e:
#         print(f"Error loading file: {e}")
#         return None

# def enc(text, filename_prefix):
#     """
#     Encrypts text using the polyalphabetic substitution from the loaded file.
#     """
#     cs = _load_matrix(filename_prefix)
#     if cs is None:
#         return "Error: Keyfile not found."

#     gs1 = ""
#     p = 1 # Pointer starts at column 1
    
#     for char in text:
#         # Preserve spaces
#         if char == ' ':
#             gs1 += ' '
#             continue
        
#         found = False
#         # Find the row where the first character matches the input char
#         for row in cs:
#             if row[0] == char:
#                 # Append the character at the current pointer index
#                 gs1 += row[p]
#                 found = True
#                 break
        
#         # If character is not in our supported list, just keep it as is
#         if not found:
#             gs1 += char

#         # Increment pointer, reset if it exceeds matrix width
#         p += 1
#         if p > MAX_INDEX:
#             p = 1
            
#     return gs1

# def dec(text, filename_prefix):
#     """
#     Decrypts text using the loaded file.
#     """
#     cs = _load_matrix(filename_prefix)
#     if cs is None:
#         return "Error: Keyfile not found."

#     gs2 = ""
#     p = 1 # Pointer starts at column 1

#     for char in text:
#         # Preserve spaces
#         if char == ' ':
#             gs2 += ' '
#             continue

#         found = False
#         # Find the row where the character at column 'p' matches input char
#         for row in cs:
#             if row[p] == char:
#                 # The decrypted char is the one at index 0 (the header column)
#                 gs2 += row[0]
#                 found = True
#                 break
        
#         # If character not found in matrix (e.g. unknown symbol), keep as is
#         if not found:
#             gs2 += char

#         # Increment pointer, reset if it exceeds matrix width
#         p += 1
#         if p > MAX_INDEX:
#             p = 1

#     return gs2

# def sheetgen(filename):
#     """
#     Generates a new random encryption sheet and saves it to the uploads folder.
#     Ensures that columns are unique so decryption is deterministic.
#     """
#     # Force save to uploads directory
#     output_dir = "uploads"
#     if not os.path.exists(output_dir):
#         os.makedirs(output_dir)

#     file_path = os.path.join(output_dir, f"{filename}.dat")

#     # Define the header row
#     header = ["ch"] + [str(i) for i in range(1, MAX_INDEX + 1)]
    
#     # Define available characters (excluding comma to prevent CSV confusion if exported later)
#     chars = string.ascii_letters + string.digits + string.punctuation
#     chars = chars.replace(",", "")
#     all_chars_list = list(chars)

#     # Initialize rows with the first column (the keys)
#     rows = [header]
#     for c in all_chars_list:
#         rows.append([c])

#     num_rows = len(rows) # Includes header
    
#     # Fill the columns (1 to 95)
#     # We must ensure that within a specific column 'p', a character only appears once.
#     # Otherwise, decryption is impossible (one ciphertext char could map to two plaintexts).
#     for col in range(1, MAX_INDEX + 1):
#         used_in_this_column = set()
        
#         for r in range(1, num_rows):
#             c = random.choice(all_chars_list)
#             # Ensure uniqueness in this vertical column
#             while c in used_in_this_column:
#                 c = random.choice(all_chars_list)
            
#             used_in_this_column.add(c)
#             rows[r].append(c)

#     # Save to pickle file
#     try:
#         with open(file_path, "wb") as f:
#             for row in rows:
#                 P.dump(row, f)
#         print(f"New character set generated at '{file_path}'")
#         return True
#     except Exception as e:
#         print(f"Error generating sheet: {e}")
#         return False



import string
import random
import pickle as P
import os

# Configuration for the matrix size
# 1 header + 95 random columns
MAX_INDEX = 95 

# OPTIMIZATION: Define the base directory relative to this file.
# This ensures that 'uploads' is found correctly regardless of the 
# working directory used by the cloud provider's runner.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _load_matrix(file_path):
    """
    Helper function to load the encryption matrix from a pickle file.
    """
    # Ensure extension exists
    if not file_path.endswith('.dat'):
        file_path += '.dat'

    cs = list()
    
    # Note: 'file_path' coming from main.py (optimized version) will already
    # be an absolute path, so os.path.exists will work reliably.
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None

    try:
        with open(file_path, mode="rb") as f:
            while True:
                try:
                    y = P.load(f)
                    # Skip the header row ['ch', '1', '2'...]
                    if y[0] == 'ch':
                        pass
                    else:
                        cs.append(y)
                except EOFError:
                    break
        return cs
    except Exception as e:
        print(f"Error loading file: {e}")
        return None

def enc(text, filename_prefix):
    """
    Encrypts text using the polyalphabetic substitution from the loaded file.
    """
    cs = _load_matrix(filename_prefix)
    if cs is None:
        return "Error: Keyfile not found."

    gs1 = ""
    p = 1 # Pointer starts at column 1
    
    for char in text:
        # Preserve spaces
        if char == ' ':
            gs1 += ' '
            continue
        
        found = False
        # Find the row where the first character matches the input char
        for row in cs:
            if row[0] == char:
                # Append the character at the current pointer index
                gs1 += row[p]
                found = True
                break
        
        # If character is not in our supported list, just keep it as is
        if not found:
            gs1 += char

        # Increment pointer, reset if it exceeds matrix width
        p += 1
        if p > MAX_INDEX:
            p = 1
            
    return gs1

def dec(text, filename_prefix):
    """
    Decrypts text using the loaded file.
    """
    cs = _load_matrix(filename_prefix)
    if cs is None:
        return "Error: Keyfile not found."

    gs2 = ""
    p = 1 # Pointer starts at column 1

    for char in text:
        # Preserve spaces
        if char == ' ':
            gs2 += ' '
            continue

        found = False
        # Find the row where the character at column 'p' matches input char
        for row in cs:
            if row[p] == char:
                # The decrypted char is the one at index 0 (the header column)
                gs2 += row[0]
                found = True
                break
        
        # If character not found in matrix (e.g. unknown symbol), keep as is
        if not found:
            gs2 += char

        # Increment pointer, reset if it exceeds matrix width
        p += 1
        if p > MAX_INDEX:
            p = 1

    return gs2

def sheetgen(filename):
    """
    Generates a new random encryption sheet and saves it to the uploads folder.
    Ensures that columns are unique so decryption is deterministic.
    """
    # OPTIMIZATION: Use absolute path construction to ensure the 'uploads' folder
    # is the same one the main app is looking at.
    output_dir = os.path.join(BASE_DIR, "uploads")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_path = os.path.join(output_dir, f"{filename}.dat")

    # Define the header row
    header = ["ch"] + [str(i) for i in range(1, MAX_INDEX + 1)]
    
    # Define available characters (excluding comma to prevent CSV confusion if exported later)
    chars = string.ascii_letters + string.digits + string.punctuation
    chars = chars.replace(",", "")
    all_chars_list = list(chars)

    # Initialize rows with the first column (the keys)
    rows = [header]
    for c in all_chars_list:
        rows.append([c])

    num_rows = len(rows) # Includes header
    
    # Fill the columns (1 to 95)
    # We must ensure that within a specific column 'p', a character only appears once.
    # Otherwise, decryption is impossible (one ciphertext char could map to two plaintexts).
    for col in range(1, MAX_INDEX + 1):
        used_in_this_column = set()
        
        for r in range(1, num_rows):
            c = random.choice(all_chars_list)
            # Ensure uniqueness in this vertical column
            while c in used_in_this_column:
                c = random.choice(all_chars_list)
            
            used_in_this_column.add(c)
            rows[r].append(c)

    # Save to pickle file
    try:
        with open(file_path, "wb") as f:
            for row in rows:
                P.dump(row, f)
        print(f"New character set generated at '{file_path}'")
        return True
    except Exception as e:
        print(f"Error generating sheet: {e}")
        return False