def increment_mbi(mbi):
    """
    Increment an MBI by 1, following the specified rules for each position and rolling over when necessary.
    """
    # Define allowed character sets for each position in the MBI
    allowed_chars = [
        "123456789",               # Position 1: Numeric 1-9
        "ACDEFGHJKMNPQRTUVWXY",     # Position 2: Alphabetic excluding S, L, O, I, B, Z
        "1234567890ACDEFGHJKMNPQRTUVWXY", # Position 3: Alphanumeric excluding S, L, O, I, B, Z
        "0123456789",               # Position 4: Numeric 0-9
        "ACDEFGHJKMNPQRTUVWXY",     # Position 5: Alphabetic excluding S, L, O, I, B, Z
        "1234567890ACDEFGHJKMNPQRTUVWXY", # Position 6: Alphanumeric excluding S, L, O, I, B, Z
        "0123456789",               # Position 7: Numeric 0-9
        "ACDEFGHJKMNPQRTUVWXY",     # Position 8: Alphabetic excluding S, L, O, I, B, Z
        "ACDEFGHJKMNPQRTUVWXY",     # Position 9: Alphabetic excluding S, L, O, I, B, Z
        "0123456789",               # Position 10: Numeric 0-9
        "0123456789"                # Position 11: Numeric 0-9
    ]
    
    # Remove hyphens for easier processing and work with list for mutability
    mbi_list = list(mbi)
    
    # Start incrementing from the last position
    for i in range(len(mbi_list) - 1, -1, -1):
        current_char = mbi_list[i]
        allowed_set = allowed_chars[i]
        next_index = allowed_set.index(current_char) + 1

        if next_index < len(allowed_set):
            mbi_list[i] = allowed_set[next_index]
            break
        else:
            mbi_list[i] = allowed_set[0]  # Reset position and carry over

    # Return the MBI without hyphens
    return ''.join(mbi_list)

def generate_mbis(start_mbi, count):
    """
    Generate a list of MBIs, starting from `start_mbi`, incrementing by 1 for `count` times.
    """
    mbis = [start_mbi]
    for _ in range(count - 1):
        next_mbi = increment_mbi(mbis[-1])
        mbis.append(next_mbi)
    
    return mbis

# Example usage:
starting_mbi = "1EG4TE5MK73"  # Starting MBI value without hyphens
n =   40# Number of MBIs to generate

mbi_list = generate_mbis(starting_mbi, n)
print("Generated MBIs:")
for mbi in mbi_list:
    print(mbi)
