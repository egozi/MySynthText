import h5py
import pandas as pd
import random
import numpy as np

from get_font_paths import read_fonts_txt
font_list = read_fonts_txt()
# font_list = ['Flower Rose Brush', 'Sweet Puppy', 'Skylark', 'always forever', 'VertigoFLF', 'Ubuntu Mono', 'Wanted M54']

def create_csv(fn, csv_name, add_usage=False, public_prob=0.5, randomize_fonts=False):
    db = h5py.File(fn, 'r')
    im_names = list(db['data'].keys())
    df = []

    for im in im_names:
        print(im)
        word_fonts = db['data'][im].attrs['word_font']

        txt = db['data'][im].attrs['txt']
        txt = txt.tolist()
        # txt = [t.decode('utf-8') for t in txt]

        # Create one entry per word with its font
        if randomize_fonts:
            # Use random fonts from font_list instead of actual fonts
            im_df = [{'image': im, 'word': word, 'font': np.random.choice(font_list)}
                     for word in txt]
        else:
            # Use actual fonts
            im_df = [{'image': im, 'word': word, 'font': font}
                     for word, font in zip(txt, word_fonts)]
        df.extend(im_df)

    df = pd.DataFrame(df)

    # Add index column
    df.insert(0, 'ind', range(len(df)))

    # Add Usage column if requested
    if add_usage:
        df['Usage'] = df.apply(lambda x: 'Public' if random.random() < public_prob else 'Private', axis=1)

    # just for probs like results:
    # df = pd.concat([df, pd.get_dummies(df['font'], dtype=float)], axis=1)
    # df.drop(['font'], axis=1, inplace=True)

    # df.to_csv('char_font_preds.csv')
    # df.to_csv('train.csv')
    df.to_csv(csv_name, index=False)    


if __name__ == '__main__':
    print('Crate csv...')
    train_file = 'results/train.h5'
    test_with_labels = 'results/test_wl.h5'

    create_csv(fn=train_file, csv_name='train.csv')
    create_csv(fn=test_with_labels, csv_name='gt.csv')

