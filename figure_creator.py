# Need to parse .csv log files, process them, and plot results
# in an organize fashion.
#
# NOTE: This program requires an aggregated log file as a command line argument
#       This program will parse the aggregated log file and produce the
#       following figures based off the following options:
#       -v  aggregate.file  fractal dimension/noise and slope variance/noise
#       -u  n1 n2 image_name    Uniform:  Small Image | Noisey Image | Noisier Image


#       -a    fractal dimension/noise versus acceleration/noise
#       -o    fractal dimension/noise versus other/noise 
#       
# USAGE: python3 figure_creator.py aggregate_file.log -option
#
# Thesis work
# Michael C. Murphy
# Code started: May 8, 2016

import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from math import log
from statistics import variance
import time
from random import randint
from scipy import ndimage

PREVIEW = True

def main():
    print( "Detected", len(sys.argv), "arguments")
    # USAGE:
    # python3 figure_creator.py (-code) (optional aguments) /path/to/aggregate/logsfiles.csv
    # CODE LIST:
    #   -u (Uniform Noise Plot 2x2) -u n1 n2 n3 imagename.png
    #   -g (Gaussian Noise Plot 2x2) -g 10 100 imagename.png
    #   -a (Uniform Noise Dim vs. Slope Variance 1x2)  -v aggregate/logfile.csv
    # **-j (Gaussian Noise Dim vs. Slope Variance 1x2) -j aggregate/logfile.csv
    # **-m (Multiple Uniform Dim vs. Slope Variance 1x2)  -m aggregate/logfile/* (up to n?)
    # **-n (Multiple Gaussian Dim vs. Slope Variance 1x2) -n aggregate/logfile/* (up to n?)
    # **-k (Plot all Dimension vs. All keys 1x4?) -k aggregate/logfile.csv

    if len(sys.argv) < 3:
        print("Insufficient Arguments:")
        print("USAGE:")
        print(" -u (Uniform Noise Plot 2x2)  -u n1 n2 n3 imagename.png")
        print(" -g (Gaussian Noise Plot 2x2) -g sigma1 sigma2 imagename.png")
        print(" -au/-ag (Uniform Noise Dim vs. Slope Variance 1x2)  -au aggregatelog.csv")
        print(" -mu/-mg (Multiple Uniform/Gaussian Noise vs. SV 1x2) -mu aggregatelog(*).csv")
        return

    # expect a '-xyz' type of argument
    if sys.argv[1][1] == "a":
        if len(sys.argv[1]) > 2 and sys.argv[1][2] == "u":
            model = "U"
        elif len(sys.argv[1]) > 2 and sys.argv[1][2] == "g":
            model = "G"
        else:
            print(" >> use -au (uniform) or -ag (gaussian)")
            return
        
        # Parse an aggregated log file
        filename = sys.argv[2]
        file = open( filename, 'r' )
        image_name = filename.split('/')
        image_name = image_name[-1].split('_')
        image_name = image_name[0]

        print(">> IMAGE NAME:",image_name)
        
        # Preparing to plot Dimension vs. Uniform Noise and Slope Variance vs. Uniform Noise
        d = []
        sv = []
        un = []
        AXIS_GRAY = '0.8'
        for line in file:
            if( line[0] != "#" ):
                line = line.strip()
                data = line.split(',')
                d.append(float(data[1]))
                sv.append(float(data[3]))
                un.append(float(data[0]))

        # Find some statistics about the data
        d_min = d.index(min(d))
        region1 = un[d_min]
        sv_max = sv.index(max(sv))
        region2 = un[sv_max]     # grab noise value where max slope variance occurs
        horiz_bar = d[0]        # grab initial dimension value to project horizontally

        # Now prepare to create the figure
        fig, axarr = plt.subplots(2, sharex=True)
        if model == "U":
            fig.suptitle("Box Count Algorithm on " + image_name + " (Uniform Noise, 100 Seeds)", fontsize=14, fontweight='bold')
        else:
            fig.suptitle("Box Count Algorithm on " + image_name + " (Gaussian Noise, 100 Seeds)", fontsize=14, fontweight='bold')
        fig.set_size_inches(10,10,forward=True)  # try to set size of plot??

        # set up gridlines for 1st plot
        axarr[0].grid(b=True, which='major', color=AXIS_GRAY, linestyle='-')
        
        axarr[0].set_ylabel("Fractal Dimension")
        axarr[0].set_xscale('log')
        axarr[0].set_title("Mean Fractal Dimension vs. Noise %")
        axarr[0].set_ylim(0,2)

        if model == "U":
            #axarr[0].errorbar(nx,dimy,dimerr,fmt='r')
            # Plot a vertical bar at slope variance max
            if( region1 > un[0] ):
                axarr[0].plot((region1,region1),(0,2),'r--')
            axarr[0].plot((region2,region2),(0,2),'r--')
            # Plot a horizontal bar at initial dimension value
            axarr[0].plot((un[1],100),(horiz_bar,horiz_bar),'g--')
            # Annotate some text highlighting original dimension
            if( region1 > un[0] ):
                axarr[0].text(region1, d[0]+0.02, " Dimension = " + format(d[0], '.2f'), color='g')
            else:
                axarr[0].text(region2, d[0]+0.02, " Dimension = " + format(d[0], '.2f'), color='g')
        else:
            # Plot a horizontal bar at initial dimension value
            axarr[0].plot((un[1],1000),(horiz_bar,horiz_bar),'g--')
            if ( horiz_bar > 1.8 ):
                axarr[0].text(100,d[0]-0.1, " Dimension = " + format(d[0], '.2f'), color='g')
            else:
                axarr[0].text(un[2],d[0]-0.1, " Dimension = " + format(d[0], '.2f'), color='g')
        axarr[0].plot(un, d, label="dimension")
        
        # set up gridlines for 2nd plot
        axarr[1].grid(b=True, which='major', color=AXIS_GRAY, linestyle='-')
        axarr[1].set_ylabel("Slope Variance")
        axarr[1].set_xscale('log')
        axarr[1].set_title("Mean Slope Variance vs. Noise %")
        if model == "U":
            axarr[1].set_xlabel("% Uniform Noise")
            axarr[1].set_ylim(0,1)
            #axarr[1].errorbar(nx,vary,varerr,fmt='r')
            # Plot a vertical bar at slope variance max
            if( region1 > un[0] ):
                axarr[1].plot((region1,region1),(0,2),'r--')
                axarr[1].text(region1, .8, " " + str(region1) + "% Noise", color='r')
            axarr[1].plot((region2,region2),(0,2),'r--')
            # Annotate some text highlighting where maximum slope variance occurs
            axarr[1].text(region2, .8, " " + str(region2) + "% Noise", color='r')
        else:
            # Set Gaussian Limits / Labels
            axarr[1].set_xlabel("Sigma")
            axarr[1].set_ylim(0,(sv[sv_max]+1)//1)  # Scale Y-axis to maximum slope variance value
        axarr[1].plot(un,sv, label="variance")

        if model == "U":
            saved_figure_name = "Fig_Uniform_DvSV_"+image_name+".png"

        else:
            saved_figure_name = "Fig_Gaussian_DvSV_"+image_name+".png"

        if( True ):
            plt.savefig(saved_figure_name)
            print(">> Figured created:", saved_figure_name)
        else:
            plt.show()
    # ================================================================================
    # Plot Multiple Uniform Noise Div vs. Slope Variance Plots
    # python3 figure_creator.py -m path/to/aggregate/logs*
    # ================================================================================# #
    elif sys.argv[1][1] == "m":
        if( len(sys.argv) < 3 ):
            print("-m too few arguments")
            return

        if len(sys.argv[1]) > 2 and sys.argv[1][2] == "u":
            model = "U"
        elif len(sys.argv[1]) > 2 and sys.argv[1][2] == "g":
            model = "G"
        else:
            print(" >> use -mu (uniform) or -mg (gaussian)")
            return

        # count the number of files to plot:
        plotcount = len(sys.argv) - 2
        print("Adding", plotcount, "plots to Figure")

        # Create the figure shell before we start parsing data and adding to plot
        fig, axarr = plt.subplots(2, sharex=True)
        if (model == "U"):
            fig.suptitle("Box Count Algorithm on " + str(plotcount) + " images (Uniform Noise)", fontsize=14, fontweight='bold')
        else:
            fig.suptitle("Box Count Algorithm on " + str(plotcount) + " images (Gaussian Noise)", fontsize=14, fontweight='bold')
        fig.set_size_inches(10,10,forward=True)  # try to set size of plot??

        # Add Marker styles/colors to plots
        color_idx = 0
        color_m = ("#ff0000","#ff9900","#33cc33","#339933","#0066ff","#ff00ff","#9900cc","#996633","#000000")
        marker_m = ('o','d','*','o','d','*','o','d','*')
        marker_m = ('.','x','4','.','x','4','.','x','4')

        label_count = 0  # adding a number while trying to get labels to work
        for filename in sys.argv[2:]:
            print("> Reading File",filename)
            
            file = open( filename, 'r' )
            image_name = filename.split('/')
            image_name = image_name[-1].split('_')
            image_name = image_name[0]

            '''
            # Parse an aggregated log file
            filename = sys.argv[2]
            file = open( filename, 'r' )
            image_name = filename.split('/')
            image_name = image_name[-1].split('_')
            image_name = image_name[0]
            '''
        
            # Preparing to plot Dimension vs. Uniform Noise and Slope Variance vs. Uniform Noise
            d = []
            sv = []
            un = []
            AXIS_GRAY = '0.8'
            for line in file:
                if( line[0] != "#" ):
                    line = line.strip()
                    data = line.split(',')
                    d.append(float(data[1]))
                    sv.append(float(data[3]))
                    un.append(float(data[0]))

            # Find some statistics about the data
            idx1 = sv.index(max(sv))
            vert_bar = un[idx1]     # grab noise value where max slope variance occurs
            horiz_bar = d[0]        # grab initial dimension value to project horizontally



            # set up gridlines for 1st plot
            axarr[0].grid(b=True, which='major', color=AXIS_GRAY, linestyle='-')
            
            axarr[0].set_ylabel("Fractal Dimension")
            axarr[0].set_xscale('log')
            if (model == "U"):
                axarr[0].set_title("Mean Fractal Dimension vs. Noise %")
            else:
                axarr[0].set_title("Mean Fractal Dimension vs. Sigma")
            axarr[0].set_ylim(0,2)
            #axarr[0].errorbar(nx,dimy,dimerr,fmt='r')
            ## Plot a vertical bar at slope variance max
            ##axarr[0].plot((vert_bar,vert_bar),(0,2),'r--')
            ## Plot a horizontal bar at initial dimension value
            ##axarr[0].plot((un[1],100),(horiz_bar,horiz_bar),'g--')
            ## Annotate some text highlighting original dimension
            ##axarr[0].text(.001, d[0]+0.02, "Dimension = " + format(d[0], '.2f'), color='g')
            axarr[0].plot(un, d, color=color_m[color_idx], marker=marker_m[color_idx], label=image_name)
        
            # set up gridlines for 2nd plot
            axarr[1].grid(b=True, which='major', color=AXIS_GRAY, linestyle='-')
            
            axarr[1].set_ylabel("Slope Variance")
            if( model == "U"):
                axarr[1].set_xlabel("% Uniform Noise")
            else:
                axarr[1].set_xlabel("Sigma")
            axarr[1].set_xscale('log')
            if (model == "U"):
                axarr[1].set_title("Mean Slope Variance vs. Noise %")
            else:
                axarr[1].set_title("Mean Slope Variance vs. Sigma")
            axarr[1].set_ylim(0,1)
            #axarr[1].errorbar(nx,vary,varerr,fmt='r')
            ## Plot a vertical bar at slope variance max
            ##axarr[1].plot((vert_bar,vert_bar),(0,2),'r--')
            ## Annotate some text highlighting where maximum slope variance occurs
            ##axarr[1].text(vert_bar+.1, .8, str(vert_bar) + "% Noise", color='r')
            axarr[1].plot(un,sv, color=color_m[color_idx], marker=marker_m[color_idx], label="V"+str(label_count))
            color_idx += 1
            if color_idx >= len(color_m):
                color_idx = 1


        # temporary vertical bars:  0.003% noise, and 0.3% noise
        ## Plot a vertical bar at slope variance max
        #axarr[0].plot((0.003,0.003),(0,2),'r--')
        #axarr[0].plot((0.3,0.3),(0,2),'r--')
        #axarr[1].plot((0.003,0.003),(0,2),'r--')
        #axarr[1].plot((0.3,0.3),(0,2),'r--')

        axarr[0].legend(loc=0, ncol=2) # , borderaxespad=0.
        if( True ):
            if( model == "U"):
                plt.savefig("Fig_DvsSV_Uniform_Multiplot_"+image_name+".png")
                print(">> SAVED FILE:","Fig_DvsSV_Uniform_Multiplot_"+image_name+".png")
            else:
                plt.savefig("Fig_DvsSV_Gaussian_Multiplot_"+image_name+".png")
                print(">> SAVED FILE:","Fig_DvsSV_Gaussian_Multiplot_"+image_name+".png")
        else:
            plt.show()
    # ================================================================================
    # Uniform Noise Examples
    # python3 figure_creator.py -u 1 10 50 imagename.png
    # ================================================================================# 
    elif sys.argv[1][1] == "u":
        if( len(sys.argv) != 6 ):
            print("-u not enough arguments")
            return
        n1 = float(sys.argv[2])
        n2 = float(sys.argv[3])
        n3 = float(sys.argv[4])
        image = sys.argv[5]
        
        print("@=====================@")
        print("| Uniform Figure Plot")
        print("| Image:", image)
        print("@=====================@")
        
        image_name = image.split('/')
        image_name = image_name[-1].split('_')
        image_name = image_name[0]

        img = get_uniform_rgb_from(image)
        
        # Make a figure that holds multiple plots
        fig = plt.figure()
        fig.set_size_inches(12,12,forward=True)  # try to set size of plot??
        fig.suptitle("Uniform Noise Added to " + image_name, fontsize=14, fontweight='bold')

        # first plot is image with no noise added
        a = fig.add_subplot(2,2,1)  # 2 rows, 2 cols, 1st image?
        imgplot = plt.imshow(img, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title('Original Image')

        a = fig.add_subplot(2,2,2) # second plot has n1 noise added
        newimg = addUniformNoise( img, n1, 10 ) # using SEED = 10 ... it's just an example figure
        imgplot = plt.imshow(newimg, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title("Added Noise at " + str(n1) + "%")

        a = fig.add_subplot(2,2,3) # second plot has n1 noise added
        newimg = addUniformNoise( img, n2, 10 ) # using SEED = 10 ... it's just an example figure
        imgplot = plt.imshow(newimg, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title("Added Noise at " + str(n2) + "%")

        a = fig.add_subplot(2,2,4) # second plot has n1 noise added
        newimg = addUniformNoise( img, n3, 10 ) # using SEED = 10 ... it's just an example figure
        imgplot = plt.imshow(newimg, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title("Added Noise at " + str(n3) + "%")

        plt.savefig("Figure_Uniform_"+image_name)
        print("Figure_Uniform_"+image_name)
        plt.show()
        
    # ================================================================================
    # Gaussian Noise Examples
    # python3 figure_creator.py -g 10 100 imagename.png
    # ================================================================================
    elif sys.argv[1][1] == "g":
        if( len(sys.argv) != 5 ):
            print("-g not enough arguments")
            return
        sig1 = float(sys.argv[2])  # first example case
        sig2 = float(sys.argv[3])  # second example case
        image = sys.argv[4]
        print("@=====================@")
        print("| Gaussian Figure Plot")
        print("| Image:", image)
        print("@=====================@")

        img = get_gaussian_rgb_from(image)
        
        # Make a figure that holds multiple plots
        fig = plt.figure()
        fig.set_size_inches(12,12,forward=True)  # try to set size of plot??
        a = fig.add_subplot(2,2,1)  # 2 rows, 2 cols, 1st image?

        # first plot - raw image   
        ##imgplot = plt.imshow(img, cmap=plt.cm.gray, interpolation='bicubic')
        ##a.set_title('Initial Image')

        ##a = fig.add_subplot(1,3,2)    # 1 row, 3 cols, 2nd image?

        # try applying a gaussian filter...
        img = ndimage.gaussian_filter(img, sigma=(sig1), order=0)
        #print(img[40])
        imgplot = plt.imshow(img, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title('Gaussian Sigma=' + str(sig1))

        # Now I need to reduce the image to a single floating point value....

        imgFiltered = np.empty( [len(img),len(img[0])],dtype=int )  # temp matrix - all 0 ints - same size as image
        for row in range( len(imgFiltered) ):
            for col in range( len(imgFiltered[0]) ):
                # Gaussian filter algorithm here:
                if( np.random.random() > img[row][col][0] ):
                    imgFiltered[row][col] = 0   # set to black
                else:
                    imgFiltered[row][col] = 1

        a = fig.add_subplot(2,2,2)   # 3rd image (was (1,3,3)
        #print(imgFiltered[40])
        imgplot = plt.imshow(imgFiltered, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title('Converted to B/W')


        a = fig.add_subplot(2,2,3)  # 2 rows, 2 cols, 1st image?

        # first plot - raw image   
        ##imgplot = plt.imshow(img, cmap=plt.cm.gray, interpolation='bicubic')
        ##a.set_title('Initial Image')

        ##a = fig.add_subplot(1,3,2)    # 1 row, 3 cols, 2nd image?

        # try applying a gaussian filter...
        img = ndimage.gaussian_filter(img, sigma=(sig2), order=0)
        #print(img[40])
        imgplot = plt.imshow(img, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title('Gaussian Sigma=' + str(sig2))

        # Now I need to reduce the image to a single floating point value....

        imgFiltered = np.empty( [len(img),len(img[0])],dtype=int )  # temp matrix - all 0 ints - same size as image
        for row in range( len(imgFiltered) ):
            for col in range( len(imgFiltered[0]) ):
                # Gaussian filter algorithm here:
                if( np.random.random() > img[row][col][0] ):
                    imgFiltered[row][col] = 0   # set to black
                else:
                    imgFiltered[row][col] = 1

        a = fig.add_subplot(2,2,4)   # 3rd image (was (1,3,3)
        #print(imgFiltered[40])
        imgplot = plt.imshow(imgFiltered, cmap=plt.cm.gray, interpolation='nearest')
        a.set_title('Converted to B/W')

        
        
        image_name = image.split('/')
        image_name = image_name[-1].split('_')
        image_name = image_name[0]
        fig.suptitle("Gaussian Noise Added to " + image_name, fontsize=14, fontweight='bold')
        plt.savefig("Figure_Gaussian_"+image_name)
        print("Figure_Gaussian_"+image_name)
        plt.show()

    else:
        print("Incorrect arguments.  See figure_creator.py header")
        sig1 = float(sys.argv[2])
        
        


    return


# Small helper function: imports the png image file,
# strips the alpha channel, and returns a numpy array
# containing the red-green-blue channel for each pixel
def get_gaussian_rgb_from(filename):
    img3D = mpimg.imread(filename, )            # read png img file
    img3D = np.delete(img3D,np.s_[3:],axis=2)   # strips alpha channel

    return img3D  # was img

# Small helper function: imports the png image file,
# strips the alpha channel, and returns a numpy array
# containing the red-green-blue channel for each pixel
def get_uniform_rgb_from(filename):
    img3D = mpimg.imread(filename, )            # read png img file
    img3D = np.delete(img3D,np.s_[3:],axis=2)   # strips alpha channel
    # condense into true 2D array
    img = np.empty( [len(img3D),len(img3D[0])],dtype=int )
    for row in range( len(img) ):
        for col in range( len(img[0]) ):
            if img3D[row][col].sum() == 0:
                img[row][col] = 0
            else:
                img[row][col] = 1
    return img

# create a Uniform noise model with percent as parameter
# Make sure to seed the noise!
def addUniformNoise(inputArray, percent, seed):
    # Need to calculate the threshold of the noise added based off of size of input Array
    # i.e. if input array is 2100 x 1800 pixels, and percent = 1%,
    # Then we would calculate: 2100x1800*0.01 = 37800 as threshold
    # Minimum number = 0, Maximum number = 2100x1800

    # apply the seed
    np.random.seed(seed)
    
    # create uniform matrix between 0 and 1
    noise = np.random.uniform(size=(len(inputArray),len(inputArray[0])))

    # only select percentage value of numbers as valid noise
    threshold = percent / 100
    noise = np.where( noise < threshold, -1, 0 )   # -1 signals probabilty of noise

    # where inputArray is 0 (black), flip noise sign to + to attenuate signal
    noise = np.where( inputArray < 1, noise*-1, noise )

    # now add noise to image
    inputArray = inputArray + noise

    ''' old noise -- only additive 
    inputArray = inputArray + noise
    inputArray = np.where( inputArray > 0, 1, 0 )
    '''
    return inputArray

main()



