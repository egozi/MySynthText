import os
from pathlib import Path

def get_font_paths_list(data_dir='data'):
    """
    Get a simple list of all font file paths.

    Args:
        data_dir: Path to data directory (default: 'data')

    Returns:
        List of font file paths like:
        ["data/fonts/alwaysforever/always_forever.ttf",
         "data/fonts/skylark/Skylark.ttf", ...]
    """
    fonts_dir = os.path.join(data_dir, 'fonts')
    font_paths = []

    # Iterate through all folders in fonts directory
    for folder_name in sorted(os.listdir(fonts_dir)):
        folder_path = os.path.join(fonts_dir, folder_name)

        # Check if it's a directory
        if os.path.isdir(folder_path):
            # Find all .ttf files in the folder
            ttf_files = list(Path(folder_path).glob('*.ttf')) + \
                       list(Path(folder_path).glob('*.TTF'))

            # Add sorted paths to list
            for ttf_file in sorted(ttf_files):
                # Use forward slashes for consistency
                relative_path = str(ttf_file).replace('\\', '/')
                font_paths.append(relative_path)

    return font_paths


def read_fonts_txt(data_dir='data'):
      """
      Read fonts.txt file and return a list of font names.

      Args:
          data_dir: Path to data directory (default: 'data')

      Returns:
          List of font names like:
          ["Ubuntu", "Ubuntu Condensed", "Ubuntu Mono", "always forever"]
      """
      fonts_txt_path = os.path.join(data_dir, 'fonts.txt')
      font_names = []

      try:
          with open(fonts_txt_path, 'r') as f:
              for line in f:
                  font_name = line.strip()
                  # Skip empty lines
                  if font_name:
                      font_names.append(font_name)
      except FileNotFoundError:
          print(f"Error: {fonts_txt_path} not found")
          return []

      return font_names


# Usage example:
if __name__ == '__main__':
    font_list = get_font_paths_list(data_dir='data')

    print("Font paths:")
    for font_path in font_list:
        print(f"  {font_path}")

    print(f"\nTotal: {len(font_list)} fonts")

    # Print as Python list format (for copying)
    print("\n" + "=" * 60)
    print("As Python list:")
    print("=" * 60)
    print(font_list)
