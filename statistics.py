"""
HDF5 Database Statistics - Analyze MySynthText dataset
Computes and visualizes statistics on images, words, and font distribution.
"""

import h5py
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt


def compute_database_statistics(db_file):
    """
    Read HDF5 database and compute statistics on the data.

    Args:
        db_file: Path to the HDF5 database file

    Returns:
        Dictionary containing statistics
    """
    db = h5py.File(db_file, 'r')

    print("\n" + "="*70)
    print("HDF5 Database Statistics")
    print("="*70)
    print(f"\nDatabase file: {db_file}")
    print(f"Root keys: {list(db.keys())}")

    # Find the data group (might be at different levels)
    if 'data' in db:
        data = db['data']
    else:
        # Try to find data group
        print("\nAvailable groups/datasets:")
        for key in db.keys():
            print(f"  - {key}: {type(db[key])}")
        raise ValueError("Could not find 'data' group in HDF5 file")

    # Initialize counters
    num_images = 0
    num_words = 0
    num_chars = 0
    font_counter = Counter()
    image_names = []

    print(f"\nScanning {len(data.keys())} entries...\n")

    # Iterate through all images
    for image_key in data.keys():
        try:
            # Check if this is a dataset or group
            item = data[image_key]

            # Skip if not a dataset
            if not isinstance(item, h5py.Dataset):
                continue

            num_images += 1
            image_names.append(image_key)

            # Get metadata from attributes
            if 'txt' not in item.attrs or 'word_font' not in item.attrs:
                print(f"  Warning: {image_key} missing txt or word_font attributes, skipping")
                continue

            txt = item.attrs['txt']
            word_fonts = item.attrs['word_font']

            # Handle different data types for txt
            if isinstance(txt, bytes):
                txt = [txt.decode('utf-8')]
            elif isinstance(txt, np.ndarray):
                txt = [t.decode('utf-8') if isinstance(t, bytes) else str(t) for t in txt]
            elif isinstance(txt, str):
                txt = [txt]

            # Count words and fonts
            num_words_in_image = len(txt)
            num_words += num_words_in_image

            # Count characters
            if 'charBB' in item.attrs:
                charBB = item.attrs['charBB']
                num_chars += charBB.shape[-1] if len(charBB.shape) > 0 else 0

            # Count font occurrences
            if isinstance(word_fonts, np.ndarray):
                for font in word_fonts:
                    font_name = font.decode('utf-8') if isinstance(font, bytes) else str(font)
                    font_counter[font_name] += 1
            else:
                font_name = word_fonts.decode('utf-8') if isinstance(word_fonts, bytes) else str(word_fonts)
                font_counter[font_name] += 1

        except Exception as e:
            print(f"  Error processing {image_key}: {e}")
            continue

    db.close()

    # Compute statistics
    total_fonts = len(font_counter)

    print(f"\n[1] IMAGE STATISTICS")
    print(f"    Total images: {num_images}")
    if num_images > 0:
        print(f"    Average words per image: {num_words / num_images:.2f}")
        print(f"    Average characters per image: {num_chars / num_images:.2f}")
    else:
        print(f"    ERROR: No images found in database!")
        return None

    print(f"\n[2] WORD STATISTICS")
    print(f"    Total words: {num_words}")
    print(f"    Total characters: {num_chars}")
    print(f"    Unique fonts used: {total_fonts}")

    print(f"\n[3] FONT DISTRIBUTION")
    print(f"    {'Font':<30} {'Count':<10} {'Percentage':<10}")
    print(f"    {'-'*50}")

    # Sort by frequency
    sorted_fonts = sorted(font_counter.items(), key=lambda x: x[1], reverse=True)

    for font, count in sorted_fonts:
        percentage = (count / num_words) * 100
        # Handle long font names
        font_display = font if len(font) <= 28 else font[:25] + "..."
        print(f"    {font_display:<30} {count:<10} {percentage:>7.2f}%")

    print(f"    {'-'*50}")
    print(f"    {'TOTAL':<30} {num_words:<10} {'100.00%':>7}")

    print(f"\n[4] IMAGE DETAILS (first 10)")
    print(f"    {'Image':<35} {'Words':<8} {'Chars':<8}")
    print(f"    {'-'*50}")

    # Re-open database to get image details
    db = h5py.File(db_file, 'r')
    data = db['data']

    for i, image_key in enumerate(image_names[:10]):
        try:
            if image_key in data:
                item = data[image_key]
                if isinstance(item, h5py.Dataset):
                    txt = item.attrs.get('txt', [])
                    charBB = item.attrs.get('charBB', None)
                    num_chars = charBB.shape[-1] if charBB is not None and len(charBB.shape) > 0 else 0
                    num_words = len(txt) if isinstance(txt, (list, np.ndarray)) else 1
                    print(f"    {image_key:<35} {num_words:<8} {num_chars:<8}")
        except Exception as e:
            print(f"    {image_key:<35} Error: {str(e)[:20]}")

    db.close()

    if num_images > 10:
        print(f"    ... and {num_images - 10} more images")

    print(f"\n" + "="*70 + "\n")

    # Return statistics as dictionary
    stats = {
        'num_images': num_images,
        'num_words': num_words,
        'num_chars': num_chars,
        'total_fonts': total_fonts,
        'font_counter': font_counter,
        'avg_words_per_image': num_words / num_images if num_images > 0 else 0,
        'avg_chars_per_image': num_chars / num_images if num_images > 0 else 0,
        'image_names': image_names
    }

    return stats


def plot_font_distribution(stats, top_n=None):
    """
    Plot font distribution histogram.

    Args:
        stats: Statistics dictionary from compute_database_statistics()
        top_n: Show only top N fonts (None to show all)
    """
    font_counter = stats['font_counter']

    # Sort and optionally limit
    sorted_fonts = sorted(font_counter.items(), key=lambda x: x[1], reverse=True)

    if top_n:
        sorted_fonts = sorted_fonts[:top_n]

    fonts, counts = zip(*sorted_fonts)

    # Plot
    fig, ax = plt.subplots(figsize=(14, 6))

    x_pos = np.arange(len(fonts))
    bars = ax.bar(x_pos, counts, edgecolor='black', alpha=0.7)

    # Color the bars
    colors = plt.cm.Set3(np.linspace(0, 1, len(fonts)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)

    ax.set_xlabel('Font Name', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (number of words)', fontsize=12, fontweight='bold')
    ax.set_title('Font Distribution in Dataset', fontsize=14, fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(fonts, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)

    # Add value labels on bars
    for i, (bar, count) in enumerate(zip(bars, counts)):
        height = bar.get_height()
        percentage = (count / stats['num_words']) * 100
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(count)}\n({percentage:.1f}%)',
                ha='center', va='bottom', fontsize=9)

    plt.tight_layout()
    plt.show()


def plot_statistics_summary(stats):
    """
    Create a summary plot with multiple subplots.

    Args:
        stats: Statistics dictionary from compute_database_statistics()
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: Font distribution pie chart
    font_counter = stats['font_counter']
    sorted_fonts = sorted(font_counter.items(), key=lambda x: x[1], reverse=True)
    fonts, counts = zip(*sorted_fonts)

    ax = axes[0, 0]
    ax.pie(counts, labels=fonts, autopct='%1.1f%%', startangle=90)
    ax.set_title('Font Distribution (Pie Chart)', fontweight='bold')

    # Plot 2: Font distribution bar chart
    ax = axes[0, 1]
    x_pos = np.arange(len(fonts))
    colors = plt.cm.Set3(np.linspace(0, 1, len(fonts)))
    ax.bar(x_pos, counts, color=colors, edgecolor='black', alpha=0.7)
    ax.set_xlabel('Font', fontweight='bold')
    ax.set_ylabel('Word Count', fontweight='bold')
    ax.set_title('Font Distribution (Bar Chart)', fontweight='bold')
    ax.set_xticks(x_pos)
    ax.set_xticklabels(fonts, rotation=45, ha='right', fontsize=9)
    ax.grid(axis='y', alpha=0.3)

    # Plot 3: Summary statistics
    ax = axes[1, 0]
    ax.axis('off')
    summary_text = f"""
    Dataset Statistics Summary

    Total Images:        {stats['num_images']}
    Total Words:         {stats['num_words']}
    Unique Fonts:        {stats['total_fonts']}

    Avg Words/Image:     {stats['avg_words_per_image']:.2f}

    Top 3 Fonts:
    """

    for i, (font, count) in enumerate(sorted_fonts[:3]):
        pct = (count / stats['num_words']) * 100
        summary_text += f"\n    {i+1}. {font}: {count} ({pct:.1f}%)"

    ax.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
            verticalalignment='center',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    # Plot 4: Cumulative distribution
    ax = axes[1, 1]
    cumsum = np.cumsum(counts)
    cumsum_pct = (cumsum / cumsum[-1]) * 100

    ax.plot(range(len(fonts)), cumsum_pct, marker='o', linestyle='-', linewidth=2, markersize=6)
    ax.axhline(y=80, color='r', linestyle='--', label='80% threshold', alpha=0.7)
    ax.axhline(y=90, color='orange', linestyle='--', label='90% threshold', alpha=0.7)
    ax.set_xlabel('Font Index (sorted by frequency)', fontweight='bold')
    ax.set_ylabel('Cumulative Percentage (%)', fontweight='bold')
    ax.set_title('Cumulative Font Distribution', fontweight='bold')
    ax.grid(alpha=0.3)
    ax.legend()
    ax.set_ylim([0, 105])

    plt.tight_layout()
    plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Analyze HDF5 database statistics for MySynthText dataset'
    )
    parser.add_argument('--db', type=str, default='results/SynthText.h5',
                        help='Path to HDF5 database file')
    parser.add_argument('--plot', action='store_true',
                        help='Show font distribution plot')
    parser.add_argument('--summary', action='store_true',
                        help='Show summary plots')
    parser.add_argument('--top-n', type=int, default=None,
                        help='Show only top N fonts in plots')

    args = parser.parse_args()

    # Compute statistics
    stats = compute_database_statistics(args.db)

    if stats is None:
        print("Failed to compute statistics!")
        exit(1)

    # Show plots if requested
    if args.plot and stats:
        plot_font_distribution(stats, top_n=args.top_n)

    if args.summary and stats:
        plot_statistics_summary(stats)
