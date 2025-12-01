"""
Script to generate fonts.txt file containing font family names
as they are saved in the result structure (res).

Reads fontlist.txt which contains file paths, extracts the actual
font family names from the TTF files, and writes them to fonts.txt.
"""

import os.path as osp
import os
import subprocess


def get_font_name_from_ttf(font_path):
    """
    Extract font family name from a TTF file using fonttools.

    Parameters:
    -----------
    font_path : str
        Full path to the TTF font file

    Returns:
    --------
    str : Font family name, or None if extraction fails
    """
    try:
        from fontTools.ttLib import TTFont

        font = TTFont(font_path)

        # Try to get the family name from the name table
        for record in font['name'].names:
            # Family name is typically name ID 1
            if record.nameID == 1:
                # Decode the name
                if isinstance(record.string, bytes):
                    try:
                        return record.string.decode('utf-16-be')
                    except:
                        return record.string.decode('utf-8', errors='ignore')
                else:
                    return record.string

        return None
    except Exception as e:
        print(f"Error reading font {font_path}: {e}")
        return None


def generate_font_names(data_dir='data', output_file='fonts.txt'):
    """
    Read fontlist.txt and create fonts.txt with font family names.

    Parameters:
    -----------
    data_dir : str
        Path to data directory containing fonts/fontlist.txt
    output_file : str
        Output filename for the font names list (will be saved in data_dir)

    Returns:
    --------
    list : List of font family names
    """

    fontlist_path = osp.join(data_dir, 'fonts/fontlist.txt')
    output_path = osp.join(data_dir, output_file)

    if not osp.exists(fontlist_path):
        raise FileNotFoundError(f"fontlist.txt not found at {fontlist_path}")

    # Read font file paths from fontlist.txt
    with open(fontlist_path, 'r') as f:
        font_paths = [line.strip() for line in f if line.strip()]

    font_names = []

    print(f"Processing {len(font_paths)} fonts...")

    # Extract font family names from each TTF file
    for i, font_path in enumerate(font_paths):
        full_path = osp.join(data_dir, 'fonts', font_path)

        if not osp.exists(full_path):
            print(f"Warning: Font file not found: {full_path}")
            continue

        font_name = get_font_name_from_ttf(full_path)

        if font_name:
            font_names.append(font_name)
            print(f"  [{i+1}/{len(font_paths)}] {font_path} -> {font_name}")
        else:
            print(f"  [{i+1}/{len(font_paths)}] {font_path} -> ERROR: Could not extract font name")

    # Write font names to output file
    with open(output_path, 'w') as f:
        for name in font_names:
            f.write(name + '\n')

    print(f"\nSuccessfully created {output_path}")
    print(f"Total fonts: {len(font_names)}")
    print("\nFont names:")
    for name in font_names:
        print(f"  - {name}")

    return font_names


if __name__ == '__main__':
    # Run from the script's directory
    script_dir = osp.dirname(osp.abspath(__file__))
    data_dir = osp.join(script_dir, 'data')

    font_names = generate_font_names(data_dir=data_dir, output_file='fonts.txt')
