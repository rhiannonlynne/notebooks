import os
import matplotlib.pyplot as plt
from astropy.io import fits
import pyregion

def plot_CCD(imagefile, regionfile=None, outfile=None):
    hdu_list = fits.open(imagefile)
    data = hdu_list[0].data
    header = hdu_list[0].header
    hdu_list.close()
    fig = plt.figure(figsize=(40.71, 40.00))
    ax = plt.axes([0, 0, 1, 1])
    plt.imshow(data, cmap='gray', vmin=55, vmax=110, origin='lower')
    plt.axis('off')
    if regionfile is not None:
        reg = pyregion.open(regionfile).as_imagecoord(header)
        patches, artists = reg.get_mpl_patches_texts()
        for p in patches:
            ax.add_patch(p)
        for t in artists:
            ax.add_artist(t)
    if outfile is None:
        outfile = imagefile.replace('.fits', '.png')
    plt.savefig(outfile, format='png', pad_inches=0, bbox_inches=0)
    plt.close('all')

if __name__ == '__main__':

    for i in [0, 1, 2, 3, 4, 5, 6, 7]:
        tail = '%d_R_2_2_S_0_0_r.fits' % i
        imagefile = 'image_%s' % tail
        outfile = 'img%02d.png' % i
        plot_CCD(imagefile, outfile=outfile)
        imagefile = 'ssmimage_%s' % tail
        outfile = 'ssm%02d.png' % i
        plot_CCD(imagefile, outfile=outfile)
        imagefile = 'ssmimage_%s' % tail
        regionfile = 'regions_%d.reg' % i
        outfile = 'ssm_reg%02d.png' % i
        plot_CCD(imagefile, regionfile=regionfile, outfile=outfile)
