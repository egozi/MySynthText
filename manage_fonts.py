#!/usr/bin/env python3
"""
Font Management Script for MySynthText

This script provides comprehensive font management:
1. Add new TTF files from a folder, organizing them into subfolders by font name
2. Update fontlist.txt and fonts.txt with new fonts
3. Update font_px2pt.cp model file with new fonts
4. Clean up fontlist.txt by removing entries for deleted font folders
5. Validate font integrity
6. Visualize fonts with sample text

Usage:
    python manage_fonts.py --add-fonts /path/to/ttf/folder [--data_dir data]
    python manage_fonts.py --clean-fonts [--data_dir data]
    python manage_fonts.py --list-fonts [--data_dir data]
    python manage_fonts.py --visualize-fonts [--vis-text "..."] [--vis-output output.png]
"""

import os
import argparse
import pickle
import shutil
import re
from pathlib import Path
import pygame
from pygame import freetype, Color
import numpy as np
import matplotlib.pyplot as plt


class FontManager:
    def __init__(self, data_dir='data'):
        """Initialize font manager with paths."""
        self.data_dir = data_dir
        self.fonts_dir = os.path.join(data_dir, 'fonts')
        self.fontlist_path = os.path.join(self.fonts_dir, 'fontlist.txt')
        self.fonts_txt_path = os.path.join(self.fonts_dir, 'fonts.txt')
        self.font_model_path = os.path.join(data_dir, 'models', 'font_px2pt.cp')
        self.newfonts_dir = os.path.join(self.fonts_dir, 'newfonts')

        # Ensure newfonts directory exists
        os.makedirs(self.newfonts_dir, exist_ok=True)

        pygame.init()

    def extract_font_name(self, ttf_path):
        """
        Extract font name from TTF file.
        Returns a clean folder name based on font name.
        """
        try:
            font = freetype.Font(ttf_path, size=12)
            font_name = font.name if font.name else os.path.splitext(os.path.basename(ttf_path))[0]

            # Clean font name: lowercase, remove spaces, keep only alphanumeric and hyphens
            clean_name = re.sub(r'[^a-z0-9-]', '', font_name.lower().replace(' ', ''))

            # Fallback if cleaning resulted in empty string
            if not clean_name:
                clean_name = os.path.splitext(os.path.basename(ttf_path))[0].lower()

            return font_name, clean_name
        except Exception as e:
            print(f"Warning: Could not read font from {ttf_path}: {e}")
            return None, None

    def add_fonts_from_folder(self, source_folder, validate=True):
        """
        Add all TTF files from a source folder to the fonts directory.
        Organizes them into subfolders by font name.

        Args:
            source_folder: Path to folder containing TTF files
            validate: Whether to validate fonts before adding

        Returns:
            List of (font_name, folder_path) tuples for added fonts
        """
        if not os.path.isdir(source_folder):
            print(f"Error: Source folder not found: {source_folder}")
            return []

        # Find all TTF files
        ttf_files = list(Path(source_folder).glob('**/*.ttf')) + \
                    list(Path(source_folder).glob('**/*.TTF'))

        if not ttf_files:
            print(f"No TTF files found in {source_folder}")
            return []

        print(f"Found {len(ttf_files)} TTF file(s)")

        added_fonts = []
        existing_fonts = self.get_existing_fonts()

        for ttf_file in ttf_files:
            ttf_path = str(ttf_file)
            print(f"\nProcessing: {os.path.basename(ttf_path)}")

            # Extract font name
            font_name, clean_name = self.extract_font_name(ttf_path)

            if not font_name or not clean_name:
                print(f"  ✗ Skipped: Could not extract font name")
                continue

            # Validate font
            if validate and not self._validate_font(ttf_path):
                print(f"  ✗ Skipped: Font validation failed")
                continue

            # Create font folder
            font_folder = os.path.join(self.fonts_dir, clean_name)
            os.makedirs(font_folder, exist_ok=True)

            # Copy TTF file to folder
            dest_path = os.path.join(font_folder, os.path.basename(ttf_path))
            try:
                shutil.copy2(ttf_path, dest_path)
                print(f"  ✓ Added: {font_name}")
                print(f"    Location: {clean_name}/{os.path.basename(ttf_path)}")
                added_fonts.append((font_name, clean_name, dest_path))
            except Exception as e:
                print(f"  ✗ Failed to copy file: {e}")
                continue

        return added_fonts

    def _validate_font(self, ttf_path):
        """Validate that a TTF file can be read by pygame."""
        try:
            font = freetype.Font(ttf_path, size=12)
            # Test rendering a character
            rect = font.get_rect('A')
            return rect.width > 0
        except Exception as e:
            print(f"    Validation error: {e}")
            return False

    def get_existing_fonts(self):
        """Get list of fonts in the fonts directory."""
        fonts = {}
        for item in os.listdir(self.fonts_dir):
            item_path = os.path.join(self.fonts_dir, item)
            if os.path.isdir(item_path):
                ttf_files = list(Path(item_path).glob('*.ttf')) + \
                           list(Path(item_path).glob('*.TTF'))
                if ttf_files:
                    fonts[item] = [str(f) for f in ttf_files]
        return fonts

    def update_fontlist(self, added_fonts=None):
        """
        Update fontlist.txt with current fonts.
        Format: folder_name/font_file.ttf
        """
        existing_fonts = self.get_existing_fonts()

        font_entries = []
        for folder_name, ttf_paths in sorted(existing_fonts.items()):
            for ttf_path in sorted(ttf_paths):
                relative_path = f"{folder_name}/{os.path.basename(ttf_path)}"
                font_entries.append(relative_path)

        # Write fontlist.txt
        with open(self.fontlist_path, 'w') as f:
            for entry in font_entries:
                f.write(entry + '\n')

        print(f"\n✓ Updated fontlist.txt with {len(font_entries)} fonts")
        return font_entries

    def update_fonts_txt(self, added_fonts=None):
        """
        Create/update fonts.txt with font names (one per line).
        """
        existing_fonts = self.get_existing_fonts()

        font_names = []
        for folder_name, ttf_paths in sorted(existing_fonts.items()):
            for ttf_path in sorted(ttf_paths):
                try:
                    font = freetype.Font(ttf_path, size=12)
                    font_name = font.name if font.name else folder_name
                    font_names.append(font_name)
                except:
                    # Fallback if can't read font name
                    font_names.append(folder_name)

        # Write fonts.txt
        with open(self.fonts_txt_path, 'w') as f:
            for font_name in font_names:
                f.write(font_name + '\n')

        print(f"✓ Updated fonts.txt with {len(font_names)} fonts")
        return font_names

    def update_font_model(self):
        """
        Update the font_px2pt.cp model file with new fonts.
        Creates linear models for pixel-to-point conversion.
        """
        print("\nUpdating font model (font_px2pt.cp)...")

        existing_fonts = self.get_existing_fonts()
        models = {}

        ys = np.arange(8, 200).astype(float)
        A = np.c_[ys, np.ones_like(ys)]

        for folder_name, ttf_paths in existing_fonts.items():
            for ttf_path in ttf_paths:
                try:
                    font = freetype.Font(ttf_path, size=12)
                    h = []
                    for y in ys:
                        h.append(font.get_sized_glyph_height(y))
                    h = np.array(h)
                    m, _, _, _ = np.linalg.lstsq(A, h, rcond=None)
                    models[font.name] = m
                    print(f"  ✓ {font.name}")
                except Exception as e:
                    print(f"  ✗ Failed to process {ttf_path}: {e}")
                    continue

        # Save model
        os.makedirs(os.path.dirname(self.font_model_path), exist_ok=True)
        with open(self.font_model_path, 'wb') as f:
            pickle.dump(models, f)

        print(f"✓ Updated font_px2pt.cp with {len(models)} font models")
        return models

    def clean_fonts(self):
        """
        Clean up fontlist.txt and fonts.txt by removing entries for
        non-existent font folders.
        """
        print("\nCleaning font lists...")

        existing_fonts = self.get_existing_fonts()
        existing_folders = set(existing_fonts.keys())

        # Read current fontlist.txt
        if os.path.exists(self.fontlist_path):
            with open(self.fontlist_path, 'r') as f:
                current_entries = [line.strip() for line in f if line.strip()]
        else:
            current_entries = []

        # Filter out entries from non-existent folders
        cleaned_entries = []
        removed_count = 0

        for entry in current_entries:
            folder_name = entry.split('/')[0] if '/' in entry else entry
            if folder_name in existing_folders:
                cleaned_entries.append(entry)
            else:
                print(f"  - Removed: {entry} (folder not found)")
                removed_count += 1

        # Write cleaned fontlist.txt
        with open(self.fontlist_path, 'w') as f:
            for entry in cleaned_entries:
                f.write(entry + '\n')

        print(f"✓ Cleaned fontlist.txt: {removed_count} entries removed")

        # Update fonts.txt as well
        self.update_fonts_txt()

        return removed_count

    def list_fonts(self):
        """List all available fonts."""
        existing_fonts = self.get_existing_fonts()

        if not existing_fonts:
            print("No fonts found")
            return

        print(f"\nAvailable fonts ({len(existing_fonts)} folders):\n")

        for folder_name, ttf_paths in sorted(existing_fonts.items()):
            print(f"  {folder_name}/")
            for ttf_path in sorted(ttf_paths):
                try:
                    font = freetype.Font(ttf_path, size=12)
                    print(f"    - {os.path.basename(ttf_path)} ({font.name})")
                except:
                    print(f"    - {os.path.basename(ttf_path)}")

        print(f"\nTotal: {sum(len(v) for v in existing_fonts.values())} font files")

    def visualize_fonts(self, text="abcdefghijklmnop ABCDEFGHIJKLMNOP 0123456789",
                       font_size=64, output_path=None, max_fonts=None):
        """
        Visualize all fonts by rendering text samples.

        Args:
            text: Text to render for each font (default: alphanumeric sample)
            font_size: Size of font to render (default: 64)
            output_path: Path to save the visualization image (optional)
            max_fonts: Maximum number of fonts to visualize (optional)
        """
        existing_fonts = self.get_existing_fonts()

        if not existing_fonts:
            print("No fonts found")
            return

        # Flatten font list
        font_list = []
        for folder_name, ttf_paths in sorted(existing_fonts.items()):
            for ttf_path in sorted(ttf_paths):
                try:
                    font_obj = freetype.Font(ttf_path, size=12)
                    font_name = font_obj.name if font_obj.name else folder_name
                    font_list.append((font_name, ttf_path))
                except:
                    font_list.append((folder_name, ttf_path))

        if not font_list:
            print("No valid fonts found")
            return

        # Limit number of fonts to visualize
        if max_fonts:
            font_list = font_list[:max_fonts]

        num_fonts = len(font_list)
        print(f"Visualizing {num_fonts} fonts...")

        # Create figure with subplots
        fig, axes = plt.subplots(num_fonts, 1, figsize=(14, 2*num_fonts))

        # Handle single font case (axes is not a list)
        if num_fonts == 1:
            axes = [axes]

        # Render and display each font
        for idx, (font_name, ttf_path) in enumerate(font_list):
            try:
                font = freetype.Font(ttf_path, size=font_size)
                font.antialiased = True
                font.origin = True

                # Render text
                surface, _ = font.render(
                    text,
                    fgcolor=Color(255, 255, 255, 255),
                    bgcolor=Color(0, 0, 0, 0)
                )

                # Convert to numpy array
                img = pygame.surfarray.array3d(surface)
                img = np.transpose(img, [1, 0, 2])

                # Display in subplot
                axes[idx].imshow(img)
                axes[idx].set_title(f"{font_name}", fontsize=10, loc='left')
                axes[idx].set_axis_off()

                print(f"  ✓ {font_name} ({img.shape})")

            except Exception as e:
                print(f"  ✗ Failed to render {font_name}: {e}")
                axes[idx].text(0.5, 0.5, f"Failed to load\n{font_name}",
                             ha='center', va='center')
                axes[idx].set_axis_off()

        plt.tight_layout()

        # Save or show
        if output_path:
            plt.savefig(output_path, dpi=100, bbox_inches='tight')
            print(f"\n✓ Visualization saved to: {output_path}")
        else:
            plt.show()

        return fig, axes


def main():
    parser = argparse.ArgumentParser(
        description='Font Management for MySynthText',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Add fonts from a folder:
    python manage_fonts.py --add-fonts /path/to/fonts/folder

  Clean up font lists:
    python manage_fonts.py --clean-fonts

  List all available fonts:
    python manage_fonts.py --list-fonts

  Visualize all fonts:
    python manage_fonts.py --visualize-fonts

  Visualize fonts with custom text and save to file:
    python manage_fonts.py --visualize-fonts --vis-text "Hello World" --vis-output fonts.png

  Visualize first 5 fonts with larger font size:
    python manage_fonts.py --visualize-fonts --vis-max 5 --vis-size 96

  Do everything (add, update, clean):
    python manage_fonts.py --add-fonts /path/to/fonts --full-update
        """
    )

    parser.add_argument('--add-fonts', type=str, metavar='FOLDER',
                        help='Add all TTF files from a folder')
    parser.add_argument('--clean-fonts', action='store_true',
                        help='Clean font lists (remove entries for missing folders)')
    parser.add_argument('--list-fonts', action='store_true',
                        help='List all available fonts')
    parser.add_argument('--visualize-fonts', action='store_true',
                        help='Visualize all fonts with sample text')
    parser.add_argument('--vis-text', type=str,
                        default='abcdefghijklmnop ABCDEFGHIJKLMNOP 0123456789',
                        help='Text to use for visualization (default: alphanumeric)')
    parser.add_argument('--vis-size', type=int, default=64,
                        help='Font size for visualization (default: 64)')
    parser.add_argument('--vis-output', type=str, metavar='PATH',
                        help='Save visualization to file (PNG/PDF)')
    parser.add_argument('--vis-max', type=int, metavar='N',
                        help='Maximum number of fonts to visualize')
    parser.add_argument('--full-update', action='store_true',
                        help='Perform complete update (update lists and model)')
    parser.add_argument('--data_dir', type=str, default='data',
                        help='Path to data directory (default: data)')
    parser.add_argument('--no-validate', action='store_true',
                        help='Skip font validation during addition')

    args = parser.parse_args()

    # Create font manager
    manager = FontManager(data_dir=args.data_dir)

    # Perform requested operations
    if args.add_fonts:
        print(f"Adding fonts from: {args.add_fonts}")
        print("=" * 60)
        added = manager.add_fonts_from_folder(args.add_fonts, validate=not args.no_validate)

        if added:
            print("\n" + "=" * 60)
            print("Updating font files...")
            manager.update_fontlist()
            manager.update_fonts_txt()
            manager.update_font_model()
            print("\n✓ Font addition completed!")
        else:
            print("No fonts were added")

    if args.full_update:
        print("Performing full update...")
        print("=" * 60)
        manager.update_fontlist()
        manager.update_fonts_txt()
        manager.update_font_model()
        print("\n✓ Full update completed!")

    if args.clean_fonts:
        manager.clean_fonts()

    if args.list_fonts:
        manager.list_fonts()

    if args.visualize_fonts:
        manager.visualize_fonts(
            text=args.vis_text,
            font_size=args.vis_size,
            output_path=args.vis_output,
            max_fonts=args.vis_max
        )

    if not any([args.add_fonts, args.clean_fonts, args.list_fonts, args.visualize_fonts, args.full_update]):
        parser.print_help()


if __name__ == '__main__':
    main()
