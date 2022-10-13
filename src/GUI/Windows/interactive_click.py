# Copyright (C) 2022 Sunnybrook Research Institute
# This file is part of Phindr3D <https://github.com/DWALab/Phindr3D>.
#
# Phindr3D is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Phindr3D is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Phindr3D.  If not, see <http://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.backend_bases import MouseButton
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import proj3d
import matplotlib
matplotlib.use('Qt5Agg')
import numpy as np
import pandas as pd
from pandas.api.types import is_numeric_dtype
import time
from more_itertools import locate
from .plot_functions import *
from .colorchannelWindow import *
import PIL.Image
import json

#Callback will open image associated with data point. Note: in 3D plot pan is hold left-click swipe, zoom is hold right-click swipe (zoom disabled)
class interactive_points():
    def __init__(self, main_plot, projection, data, labels, ch, feature_file, color, imageID, color_filt):
        self.main_plot=main_plot
        self.projection=projection
        self.data=data
        self.labels=labels
        self.feature_file=feature_file
        self.color=color[:]
        self.imageID=imageID
        self.ch=ch
        self.lbl_filt=color_filt
    def buildImageViewer(self, label, cur_label, index, color, feature_file, imageID):

                self.win = QDialog()
                self.win.resize(800, 500)
                self.win.setWindowTitle("ImageViewer")
                self.error=False
                grid = QGridLayout()

                #info layout
                info_box = QVBoxLayout()
                file_info=QLabel("FileName:")
                file_info.setAlignment(Qt.AlignTop)
                file_info.setStyleSheet("background-color: white")
                file_info.setWordWrap(True)
                file_info.setFixedWidth(200)
                file_info.setMinimumHeight(350)
                info_box.addStretch()
                info_box.addWidget(file_info)
                info_box.addStretch()

                #image plot layout
                x = []
                y = []
                main_plot = MplCanvas(self, width=10, height=10, dpi=600, projection='2d')
                main_plot.fig.set_facecolor('#f0f0f0')
                main_plot.axes.scatter(x, y)
                main_plot.axes.get_xaxis().set_visible(False)
                main_plot.axes.get_yaxis().set_visible(False)

                # adjustbar layout
                adjustbar = QSlider(Qt.Vertical)
                adjustbar.setMinimum(0)
                adjustbar.setValue(0)
                adjustbar.setFixedWidth(50)
                adjustbar.setPageStep(1)
                adjustbar.setSingleStep(1)
                adjustbar.setStyleSheet(
                    "QSlider::groove:vertical {background-color: #8DE8F6; border: 1px solid;height: 700px;margin: 0px;}"
                    "QSlider::handle:vertical {background-color: #8C8C8C; border: 1px silver; height: 30px; width: 10px; margin: -5px 0px;}")

                #parent layout
                toolbar = NavigationToolbar(self.main_plot, self.win)
                grid.addWidget(toolbar, 0, 1)
                grid.addLayout(info_box, 1, 0)
                grid.addWidget(main_plot, 1, 1)
                grid.addWidget(adjustbar, 1, 2)
                self.win.setLayout(grid)

                #callbacks
                self.plot_img(adjustbar, main_plot, self.color, label, cur_label, index, feature_file, file_info, imageID)
                self.win.exec()
    def read_featurefile(self, slicescrollbar, color, label, cur_label, index, feature_file, file_info, imageID):
        if feature_file:
            # extract image details from feature file
            if 'csv' in feature_file[0]:
                data = pd.read_csv(feature_file[0], na_values='NaN')
            else:
                data = pd.read_csv(feature_file[0], sep="\t", na_values='NaN')
            '''
            if os.path.exists(data["MetadataFile"].str.replace(r'\\', '/', regex=True).iloc[0])==False:
                self.error = True
                raise FileNotFoundError
            data = pd.read_csv(data["MetadataFile"].str.replace(r'\\', '/', regex=True).iloc[0], sep="\t", na_values='NaN')
            
            #getting metadatafile
            cols=data.columns.to_list()
            if any("Channel" in ch for ch in cols)==False or ('Stack' not in cols) or ('ImageID' not in cols):
                self.error = True
                raise MissingChannelStackError
            ch_len = (list(np.char.find(list(data.columns), 'Channel_')).count(0))
            '''
            cur_index=0
            if len(np.unique(imageID)) > 1:
                '''
                print("\n")
                print(index)
                print(self.labels)
                print(imageID)
                cat_num=imageID[index]
                print(cat_num)
                cat_locs=np.where(imageID==cat_num)[0]
                print(cat_locs)
                cat_loc_ind=np.where(cat_locs==index)[0][0]
                print(cat_loc_ind)
                print(label[cat_num], type(label[cat_num]), self.lbl_filt.currentText(), np.unique(label)[cat_num], type(np.unique(label)[cat_num]))
                lbl=np.unique(label)[cat_num]
                '''
                '''
                if is_numeric_dtype(data[self.lbl_filt.currentText()]):
                    if str.isdigit(lbl):
                        lbl=int(lbl)
                    else:
                        dec=len(lbl)-str(lbl).find(".")
                        print(str(lbl).find("."), lbl.find("."))
                        print(len(lbl), dec)
                        lbl=round(lbl, dec)
                
                pd_allinstances=data.loc[data[self.lbl_filt.currentText()] == lbl]
                print(pd_allinstances)
                pd_ind=list(pd_allinstances.index)
                print(list(pd_allinstances.index))
                cur_index=pd_ind[cat_loc_ind]
                print(cur_index)
                '''
                #pd_singleinstance=pd_allinstances.iloc[cat_loc_ind]
                #print(pd_singleinstance)
                #print(pd_singleinstance.index)
                #cur_index=pd_singleinstance.index
                #print(index)
                #print(label)
                #print(imageID)
                cur_index=index
                #cur_index = list(locate(label, lambda x: x == cur_label))[index]
                #row_ind = imageID[cur_ind]
                #stacks = data[data[self.ch[0]] == row_ind][self.ch[0]]
            else:
                cur_index=index
                print(cur_index)
                #stacks = data[data[self.ch[0]] == index + 1][self.ch[0]]
            if len(self.ch)==2:
                file_text="Filename: " + os.path.join(self.ch[0],data[self.ch[1]].iloc[cur_index]).replace('\\', "/")
            else:
                file_text = "Filename: " + os.path.join(data[self.ch[0]].iloc[cur_index]).replace('\\', "/")
            if len(file_text)>20:
                #prevent text placed off-screen
                file_text=fill(file_text, 25)
            file_info.setText(file_text)

            #only slice projection can use slider
            slicescrollbar.setMaximum(0)
            # initialize array as image size with rgb and # channels
            '''
            empty_img = PIL.Image.open(data[self.ch[0]].str.replace(r'\\', '/', regex=True).iloc[cur_index]).size
            if PIL.Image.open(data['Channel_1'].str.replace(r'\\', '/', regex=True).iloc[cur_index]).mode in ["CMYK","HSV", "LAB", "RGB", "RGBA", "RGBX", "YCbCr"]:
                self.error = True
                raise ColorIMG
            empty_img = np.zeros((ch_len, empty_img[1], empty_img[0], 3))
            '''
            if len(self.ch) == 2:
                img=np.array(PIL.Image.open(os.path.join(self.ch[0],data[self.ch[1]].iloc[cur_index].replace('\\', "/"))))
            else:
                img = np.array(PIL.Image.open(os.path.join(data[self.ch[0]].iloc[cur_index].replace('\\', "/"))))
            return(data, img)#, meta_loc, stacks, ch_len, bounds, threshold)
    def plot_img(self, slicescrollbar, img_plot, color, label, cur_label, index, feature_file, file_info, imageID):
        #try:
            #data, img, metaloc, stacks,ch_len, bounds, threshold=self.read_featurefile(slicescrollbar, color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt)
            data, img = self.read_featurefile(slicescrollbar, color, label,cur_label, index,feature_file, file_info, imageID)

            img_plot.axes.imshow(img)
            #img_plot.axes.set_aspect(aspect='auto')
            img_plot.axes.axis('off')
            img_plot.fig.subplots_adjust(wspace=0.0075, hspace=0.0075)
            img_plot.draw()
            self.win.show()
            #self.win.exec()
        #except ColorIMG:
        #    errorWindow("Metadata Error", "Cannot use RGB/A or Colored Images")
        #except Exception as ex:
        #    errorWindow("Metadata Error", "Python Error Message: {}".format(ex))
        #    self.error = True
    def color_change(self, ch, color, win_title, col_title, labels, slicescrollbar, img_plot, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt):
        colors=colorchannelWindow(ch, color, win_title, col_title, labels)
        self.color=colors.color
        self.plot_img(slicescrollbar, img_plot, self.color, label, cur_label, index, feature_file, file_info, ch_info, imageID, pjt)

    def __call__ (self, event): #picker is right-click activation
        if event.mouseevent.inaxes is not None and event.mouseevent.button is MouseButton.RIGHT:
            if len(self.ch)==0 or not os.path.exists(self.ch[0]):
                return(errorWindow("Images", "Image Filenames Column invalid. Go to 'Change Plot Data Columns' and select valid Image Filenames Column"))
            #https://github.com/matplotlib/matplotlib/issues/ 19735   ---- code below from github open issue. wrong event.ind coordinate not fixed in current version matplotlib...
            xx = event.mouseevent.x
            yy = event.mouseevent.y
            label = event.artist.get_label()
            #print(label)
            #label_ind=np.where(np.array(self.labels)==label)[0]
            #print(label_ind)
            # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            #x2, y2, z2 = proj3d.proj_transform(self.data[0][label_ind[0]], self.data[1][label_ind[0]], self.data[2][label_ind[0]], self.main_plot.axes.get_proj())
            x2, y2, z2 = proj3d.proj_transform(self.data[0][0], self.data[1][0],
                                               self.data[2][0], self.main_plot.axes.get_proj())
            x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
            # the distance
            d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)

            # find the closest by searching for min distance.
            # from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
            imin = 0
            dmin = 10000000
            for i in range(len(self.labels)):
            #for i in range(np.shape(label_ind)[0]):
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                x2, y2, z2 = proj3d.proj_transform(self.data[0][i], self.data[1][i],
                                                   self.data[2][i], self.main_plot.axes.get_proj())
                #x2, y2, z2 = proj3d.proj_transform(self.data[0][label_ind[i]], self.data[1][label_ind[i]], self.data[2][label_ind[i]], self.main_plot.axes.get_proj())
                x3, y3 = self.main_plot.axes.transData.transform((x2, y2))
                # magic from https://stackoverflow.com/questions/10374930/matplotlib-annotating-a-3d-scatter-plot
                d = np.sqrt((x3 - xx) ** 2 + (y3 - yy) ** 2)
                # We find the distance and also the index for the closest datapoint
                if d < dmin:
                    dmin = d
                    imin = i
            self.main_plot.axes.scatter3D(self.data[0][imin],
                                        self.data[1][imin],
                                        self.data[2][imin], s=35, facecolor="none",
                                        edgecolor='gray', alpha=1)
            '''
            self.main_plot.axes.scatter3D(self.data[0][label_ind[imin]],
                                        self.data[1][label_ind[imin]],
                                        self.data[2][label_ind[imin]], s=35, facecolor="none",
                                        edgecolor='gray', alpha=1)
            '''
            #for debugging
            #print(self.data[0][label_ind[imin]], self.data[1][label_ind[imin]], self.data[2][label_ind[imin]])
            self.main_plot.draw()
            self.main_plot.figure.canvas.draw_idle()
            self.buildImageViewer(self.labels,label, imin,self.color,self.feature_file, self.imageID)

class ColorIMG(Exception):
    pass