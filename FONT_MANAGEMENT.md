# Font Management Guide

## Overview

The `manage_fonts.py` script provides comprehensive font management for MySynthText. It allows you to:

1. **Add new TTF files** from a folder, organizing them into subfolders by font name
2. **Update fontlist.txt** with the new font entries (format: `folder/font.ttf`)
3. **Create/update fonts.txt** with font names (one per line, no paths)
4. **Update font_px2pt.cp** model file with new fonts for pixel-to-point conversion
5. **Clean up font lists** by removing entries for deleted font folders
6. **List all available fonts** with their properties
7. **Visualize fonts** by rendering text samples (from `vis_fonts.py`)

## Requirements

- pygame with freetype support
- numpy
- Python 3.6+

## Usage

### Add fonts from a folder

```bash
python manage_fonts.py --add-fonts /path/to/ttf/folder
```

This will:
- Scan the folder for all `.ttf` files (recursively)
- Extract the font name from each TTF file
- Create a subfolder with a clean folder name (lowercase, alphanumeric)
- Copy the TTF file to the appropriate subfolder
- Update `fontlist.txt` with new entries
- Create/update `fonts.txt` with font name mappings
- Update `font_px2pt.cp` with font models

**Example:**
```bash
python manage_fonts.py --add-fonts ./new_fonts
```

### Specify custom data directory

```bash
python manage_fonts.py --add-fonts ./new_fonts --data_dir /custom/data/path
```

### Skip font validation

By default, fonts are validated to ensure they can be read. To skip validation:

```bash
python manage_fonts.py --add-fonts ./new_fonts --no-validate
```

### Clean up font lists

Remove entries for deleted font folders:

```bash
python manage_fonts.py --clean-fonts
```

This will:
- Check if all fonts listed in `fontlist.txt` have corresponding folders
- Remove entries for missing folders
- Update `fonts.txt` accordingly

### List all available fonts

```bash
python manage_fonts.py --list-fonts
```

Output example:
```
Available fonts (4 folders):

  ubuntu/
    - Ubuntu-Bold.ttf (Ubuntu)
  ubuntucondensed/
    - UbuntuCondensed-Regular.ttf (Ubuntu Condensed)
  ubuntomono/
    - UbuntuMono-Regular.ttf (Ubuntu Mono)
  newfonts/
    - always_forever.ttf (Always Forever)

Total: 4 font files
```

### Visualize fonts

Display all fonts with sample text in matplotlib:

```bash
python manage_fonts.py --visualize-fonts
```

Customize the visualization:

```bash
# Custom text
python manage_fonts.py --visualize-fonts --vis-text "Hello World!"

# Save to file instead of displaying
python manage_fonts.py --visualize-fonts --vis-output fonts_preview.png

# Larger font size
python manage_fonts.py --visualize-fonts --vis-size 96

# Limit to first 5 fonts
python manage_fonts.py --visualize-fonts --vis-max 5

# Combine options
python manage_fonts.py --visualize-fonts \
  --vis-text "ABCDEFG 123456" \
  --vis-size 80 \
  --vis-max 10 \
  --vis-output preview.png
```

The visualization creates one subplot per font, rendering the specified text with white text on a black background.

### Perform full update

Update all font lists and models:

```bash
python manage_fonts.py --full-update
```

## Directory Structure

The script maintains the following directory structure:

```
data/
├── fonts/
│   ├── fontlist.txt          # List of fonts (folder/file.ttf)
│   ├── fonts.txt             # Font names and paths (FontName|folder/file.ttf)
│   ├── ubuntu/
│   │   └── Ubuntu-Bold.ttf
│   ├── ubuntucondensed/
│   │   └── UbuntuCondensed-Regular.ttf
│   ├── ubuntumono/
│   │   └── UbuntuMono-Regular.ttf
│   └── newfonts/
│       └── always_forever.ttf
└── models/
    └── font_px2pt.cp         # Font pixel-to-point conversion models
```

### fontlist.txt Format

One font per line, path relative to fonts directory:

```
ubuntu/Ubuntu-Bold.ttf
ubuntucondensed/UbuntuCondensed-Regular.ttf
ubuntumono/UbuntuMono-Regular.ttf
newfonts/always_forever.ttf
```

### fonts.txt Format

One font name per line:

```
Ubuntu
Ubuntu Condensed
Ubuntu Mono
always forever
```

### font_px2pt.cp Format

Python pickle file containing font models for pixel-to-point conversion.
Each font name maps to a linear model [slope, intercept].

## Font Naming Rules

When organizing fonts into folders, the script:

1. Extracts the font name from the TTF metadata
2. Converts to lowercase
3. Removes non-alphanumeric characters (except hyphens)
4. Uses this as the folder name

**Examples:**
- "Ubuntu Bold" → `ubuntu` (if original folder is `ubuntu`)
- "DejaVu Sans" → `dejavusans`
- "Times New Roman" → `timesnewroman`
- "My-Font-2024" → `my-font-2024`

## Examples

### Example 1: Add fonts from a folder

```bash
# Create a folder with some TTF files
mkdir ~/Downloads/my_fonts
cd ~/Downloads/my_fonts
# ... copy some TTF files here ...

# Add them to MySynthText
cd ~/source/MySynthText
python manage_fonts.py --add-fonts ~/Downloads/my_fonts
```

Output:
```
Adding fonts from: /home/user/Downloads/my_fonts
============================================================
Found 3 TTF file(s)

Processing: Arial.ttf
  ✓ Added: Arial
    Location: arial/Arial.ttf

Processing: Times.ttf
  ✓ Added: Times New Roman
    Location: timesnewroman/Times.ttf

Processing: Courier.ttf
  ✓ Added: Courier New
    Location: couriernew/Courier.ttf

============================================================
Updating font files...

✓ Updated fontlist.txt with 7 fonts
✓ Updated fonts.txt with 7 fonts (just font names, no paths)

Updating font model (font_px2pt.cp)...
  ✓ Arial
  ✓ Times New Roman
  ✓ Courier New
✓ Updated font_px2pt.cp with 6 font models

✓ Font addition completed!
```

### Example 2: Clean up after removing fonts manually

```bash
# Manually delete a font folder
rm -rf data/fonts/oldFont

# Clean the font lists
python manage_fonts.py --clean-fonts
```

Output:
```
Cleaning font lists...
  - Removed: oldfont/OldFont.ttf (folder not found)
✓ Cleaned fontlist.txt: 1 entries removed
✓ Updated fonts.txt with 6 fonts
```

### Example 3: List all fonts

```bash
python manage_fonts.py --list-fonts
```

## API Usage

You can also use the FontManager class directly in your Python code:

```python
from manage_fonts import FontManager

# Initialize manager
manager = FontManager(data_dir='data')

# Add fonts from folder
added_fonts = manager.add_fonts_from_folder('./new_fonts')

# Update all files
manager.update_fontlist()
manager.update_fonts_txt()
manager.update_font_model()

# List available fonts
manager.list_fonts()

# Clean up
removed = manager.clean_fonts()

# Visualize fonts
manager.visualize_fonts(
    text="Hello World 123",
    font_size=80,
    output_path='fonts_preview.png'  # Save to file
)

# Visualize with default settings (display in window)
manager.visualize_fonts()

# Visualize first 5 fonts
manager.visualize_fonts(max_fonts=5)
```

## Troubleshooting

### Issue: "No TTF files found in [folder]"

**Solution:** Make sure the folder contains `.ttf` files. The script searches recursively, so you can have subdirectories.

### Issue: "Could not extract font name" warning

**Solution:** The font file may be corrupted or in an unsupported format. Use `--no-validate` to skip validation, or manually check the file.

### Issue: Font added but not appearing in generation

**Solution:**
1. Run `python manage_fonts.py --list-fonts` to verify the font was added
2. Check that `fontlist.txt` contains the font entry
3. Run `python manage_fonts.py --full-update` to rebuild all files

## Notes

- Font folders are created with lowercase names (e.g., `ubuntu`, not `Ubuntu`)
- Each folder can contain multiple TTF files (different weights/styles of the same font family)
- The script validates fonts by trying to render a character with them
- Font models are computed using linear regression on glyph heights
- Always backup your `fontlist.txt`, `fonts.txt`, and `font_px2pt.cp` before making large changes

## Related Files

- `add_new_fonts.py` - Original simpler font management script (kept for reference)
- `vis_fonts.py` - Original font visualization script (merged into manage_fonts.py)
- `text_utils.py` - Uses `fontlist.txt` and `font_px2pt.cp` during rendering
- `synthgen.py` - Main synthesis engine that uses selected fonts

## Visualization Feature

The visualization functionality is merged from `vis_fonts.py`. It allows you to:

- **Display fonts** in matplotlib subplots with configurable sample text
- **Customize rendering** with font size, text content, and limits
- **Save visualizations** to PNG/PDF files for documentation
- **Batch preview** all fonts or a subset of them

The visualization uses pygame's freetype to render text exactly as MySynthText does, ensuring the preview matches the actual rendering.
