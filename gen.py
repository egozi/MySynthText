
# Author: Ankush Gupta
# Date: 2015

"""
Entry-point for generating synthetic text images, as described in:

@InProceedings{Gupta16,
            author           = "Gupta, A. and Vedaldi, A. and Zisserman, A.",
            title                = "Synthetic Data for Text Localisation in Natural Images",
            booktitle        = "IEEE Conference on Computer Vision and Pattern Recognition",
            year                 = "2016",
        }
"""

import numpy as np
import h5py
import os, sys, traceback
import os.path as osp
from synthgen import *
from common import *
import wget, tarfile
import random


## Define some configuration variables:
# NUM_IMG = -1 # no. of images to use for generation (-1 to use all available):
INSTANCE_PER_IMAGE = 1 # no. of times to use the same image
# SECS_PER_IMG = 5 #max time per image in seconds
SECS_PER_IMG = None  # DEBUG 5 #max time per image in seconds

# path to the data-file, containing image, depth and segmentation:
# DATA_PATH = "../prev_project/data2"  #'data'
DATA_PATH = "data/"  #'data'
DB_FNAME = osp.join(DATA_PATH,'dset.h5')
# url of the data (google-drive public file):
DATA_URL = 'http://www.robots.ox.ac.uk/~ankush/data.tar.gz'
OUT_FILE = 'results/SynthText_val.h5'
OUT_FILE = 'results/SynthText_test.h5'
OUT_FILE = 'results/SynthText.h5'
OUT_PATH = 'results/images/'

def get_data():
    """
    Download the image,depth and segmentation data:
    Returns, the h5 database.
    """
    if not osp.exists(DB_FNAME):
        try:
            colorprint(Color.BLUE,'\tdownloading data (56 M) from: '+DATA_URL,bold=True)
            print()
            sys.stdout.flush()
            out_fname = 'data.tar.gz'
            wget.download(DATA_URL,out=out_fname)
            tar = tarfile.open(out_fname)
            tar.extractall()
            tar.close()
            os.remove(out_fname)
            colorprint(Color.BLUE,'\n\tdata saved at:'+DB_FNAME,bold=True)
            sys.stdout.flush()
        except:
            print (colorize(Color.RED,'Data not found and have problems downloading.',bold=True))
            sys.stdout.flush()
            sys.exit(-1)
    # open the h5 file and return:
    return h5py.File(DB_FNAME,'r')


def add_res_to_db(imgname,res,db):
    """
    Add the synthetically generated text image instance
    and other metadata to the dataset.
    """
    dt = h5py.special_dtype(vlen=str)    # old h5py way

    ninstance = len(res)
    for i in range(ninstance):
        dname = "%s_%d"%(imgname, i)
        db['data'].create_dataset(dname,data=res[i]['img'])
        db['data'][dname].attrs['charBB'] = res[i]['charBB']
        db['data'][dname].attrs['wordBB'] = res[i]['wordBB']                
        #db['data'][dname].attrs['txt'] = res[i]['txt']
        L = res[i]['txt']
        # L = [n.encode("ascii", "ignore") for n in L]
        db['data'][dname].attrs['txt'] = np.array(L, dtype=dt)

        # add the fonts (per character)
        F = res[i]['font']
        F = [j for sub in F for j in sub]
        # original:
        # F = [n.encode("ascii", "ignore") for n in F]
        # db['data'][dname].attrs['font'] = F

        # Claude version:
        # F = [n.encode("utf-8") for n in [j for sub in res[i]['font'] for j in sub]]
        # db['data'][dname].attrs['font'] = np.array(F, dtype='U16')

        F = [j for sub in res[i]['font'] for j in sub]
        db['data'][dname].attrs['font'] = np.array(F, dtype=dt)

        # add word-level fonts (one font per word)
        # Since each word is rendered with a single font, take the first character's font of each word
        txt = res[i]['txt']
        word_fonts = []
        char_idx = 0
        for word in txt:
            # Get font for first character of this word
            word_fonts.append(F[char_idx])
            # Move char_idx to the next word
            char_idx += len(word)
        db['data'][dname].attrs['word_font'] = np.array(word_fonts, dtype=dt)


def main(viz=False, n_img=-1):
    # open databases:
    print (colorize(Color.BLUE,'getting data..',bold=True))
    db = get_data()

    # ===========================================================================
    # get the images + segmentations + depth images
    depth_file = osp.join(DATA_PATH, 'depth.h5')
    seg_file = osp.join(DATA_PATH,  'seg.h5')
    images_dir = osp.join(DATA_PATH, 'bg_img/')

    depth_db = h5py.File(depth_file, 'r')
    seg_h5 = h5py.File(seg_file, 'r')
    seg_db = seg_h5['mask']

    text_file_name = "text/text_data_clean.txt" 
    # =========================================================================== 
    print (colorize(Color.BLUE,'\t-> done',bold=True))

    # open the output h5 file:
    out_db = h5py.File(OUT_FILE,'w')
    out_db.create_group('/data')
    print (colorize(Color.GREEN,'Storing the output in: '+OUT_FILE, bold=True))

    # get the names of the image files in the dataset:
    # imnames = sorted(db['image'].keys())
    imnames = sorted(depth_db.keys())

    # =========================================================================== 
    # sample for train and test sets
    random.seed(42)
    im_sample = random.sample(imnames, 5000)
    # train_im = im_sample[:1200]
    # test_im = im_sample[1200:3000]
    # test_im = im_sample[3000:5000]

    # for train set 
    # imnames = train_im
    # imnames = test_im
    imnames = im_sample

    N = len(imnames)
    # N = 5 ## DEBUG
    print (colorize(Color.GREEN,'Number of possible images: ' + str(N), bold=True))
    # =========================================================================== 

    if n_img > 0:
        num_img = n_img
    else:
        num_img = N
    start_idx, end_idx = 0,min(num_img, N)

    RV3 = RendererV3(DATA_PATH,max_time=SECS_PER_IMG, filename=text_file_name)

    # Improve text clarity and separation
    font_state = RV3.text_renderer.font_state
    font_state.strong = 0.0  # Bold text
    font_state.strength = [0.10, 0.50]  # Thick outlines
    font_state.kerning = [2, 5, 0, 50]  # Large character spacing
    font_state.border = 0.7  # Always apply border
    font_state.curved = 0.0  # Straight baselines
    font_state.oblique = 0.0  # No italic

    # Disable curved baselines
    RV3.text_renderer.p_curved = 0.0

    for i in range(start_idx,end_idx):
        imname = imnames[i]
        try:
            # get the image:
            # img = Image.fromarray(db['image'][imname][:])
            img = plt.imread(osp.join(images_dir, imname))
            img = Image.fromarray(img)

            # get the pre-computed depth:
            #  there are 2 estimates of depth (represented as 2 "channels")
            #  here we are using the second one (in some cases it might be
            #  useful to use the other one):
            # depth = db['depth'][imname][:].T
            depth = depth_db[imname][:].T
            depth = depth[:,:,1]

            # get segmentation:
            # seg = db['seg'][imname][:].astype('float32')
            # area = db['seg'][imname].attrs['area']
            # label = db['seg'][imname].attrs['label']

            seg = seg_db[imname][:].astype('float32')
            area = seg_db[imname].attrs['area']
            label = seg_db[imname].attrs['label']

            # re-size uniformly:
            sz = depth.shape[:2][::-1]
            img = np.array(img.resize(sz,Image.LANCZOS))
            seg = np.array(Image.fromarray(seg).resize(sz,Image.NEAREST))

            print (colorize(Color.RED,'%d of %d'%(i,end_idx-1), bold=True))
            res = RV3.render_text(img,depth,seg,area,label,
                                                        ninstance=INSTANCE_PER_IMAGE,viz=viz)

            # save the images:
            im = res[0]['img']
            plt.imsave(osp.join(OUT_PATH, imname), im)

            font_list = res[0]['font']
            font_list = [f for sub_list in font_list for f in sub_list]
            font_name = ['Skylark', 'Ubuntu Mono', 'Sweet Puppy']
            # import ipdb; ipdb.set_trace(context=7) # BREAKPOINT

            charBB = res[0]['charBB']
            nC = charBB.shape[-1]
            plt.figure()
            plt.imshow(im)
            for b_inx in range(nC):

                    if font_list[b_inx]==font_name[0]:
                            color = 'r'
                    elif font_list[b_inx]==font_name[1]:
                            color = 'b'
                    else:
                            color = 'g'
                    bb = charBB[:,:,b_inx]
                    # color = 'r' if font_list[b_inx]==font_name[0] else 'b'
                    x = np.append(bb[0,:], bb[0,0])
                    y = np.append(bb[1,:], bb[1,0])
                    plt.plot(x, y, color)

            plt.savefig(osp.join(OUT_PATH, imname[:-4] + '_bb.jpg'))
            # plt.show()

            if len(res) > 0:
                # non-empty : successful in placing text:
                add_res_to_db(imname,res,out_db)
            # visualize the output:
            if viz:
                if 'q' in input(colorize(Color.RED,'continue? (enter to continue, q to exit): ',True)):
                    break
        except:
            traceback.print_exc()
            print (colorize(Color.GREEN,'>>>> CONTINUING....', bold=True))
            continue

    seg_h5.close()
    depth_db.close()
    # db.close()
    out_db.close()


if __name__=='__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Genereate Synthetic Scene-Text Images')
    parser.add_argument('--viz',action='store_true',dest='viz',default=False,help='flag for turning on visualizations')
    parser.add_argument('--num-images',type=int,dest='num_images',default=-1,help='number of images to process (-1 to use all available, default: -1)')
    args = parser.parse_args()
    main(args.viz, args.num_images)
