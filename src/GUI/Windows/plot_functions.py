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

import numpy as np
from cv2 import medianBlur
import PIL.Image
from src.GUI.Windows.colorchannelWindow import *
import matplotlib
import matplotlib.pyplot as plt
from math import ceil, floor
from textwrap import fill
from sklearn import preprocessing
from src.GUI.Windows.helperclasses import *
import matplotlib.colors as mcolors
import json
try:
    from ...Clustering import *
    from .helperclasses import *
    #from ...Data.DataFunctions import *
    #from ...Data.Metadata import *
    #from ...PhindConfig.PhindConfig import PhindConfig
except ImportError:
    from src.Clustering import *
    from src.GUI.Windows.helperclasses import *
    #from src.Data.DataFunctions import *

def result_plot(self, X, projection, plot, new_plot):
    #reset plot
    self.main_plot.axes.clear()
    del self.plots[:]
    if new_plot:
        dim=int(projection[0])
        self.plot_data.clear()
        if plot=="Raw Data":
            self.plot_data.extend([X[:,0], X[:,1], X[:,2]])
            print(self.plot_data)
        else:
            #send to clustering.py for PCA, Sammon, t-SNE, UMAP analysis
            P=Clustering().plot_type(X, dim, plot)
            #save new x, y, z data
            self.plot_data.append(P[:,0])
            self.plot_data.append(P[:,1])
            if dim==3:
                self.plot_data.append(P[:, 2])
            else:
                self.plot_data.append(np.zeros(len(self.plot_data[-1])))

    #create categorical labels
    le = preprocessing.LabelEncoder()
    lbls=self.labels
    le.fit(lbls)
    cat=np.array(le.transform(lbls))
    self.imageIDs.clear()
    self.imageIDs.extend(cat)
    #colour map
    colors = plt.cm.get_cmap('gist_rainbow')
    cmap= mcolors.ListedColormap([list(colors(i)) for i in np.linspace(0, 1, len(np.unique(self.labels)), endpoint=True)])
    legend=True
    #plot data
    if len(np.unique(lbls))<50 or all(map(lambda x: isinstance(x, str), self.labels)):
        self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], s=10, alpha=1, depthshade=False, picker=1.5, c=cat, cmap=cmap))
    else: #if more than 50 labels default to colorbar
        self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], s=10, alpha=1,
                                      depthshade=False, picker=1.5, c=self.labels, cmap=cmap))

    legend_format(self, plot, colors, new_plot, lbls, legend)
def legend_format(self, plot, colors, new_plot, labels, legend):
    #remove previous colorbar
    if len(self.main_plot.fig.axes)>1:
        self.main_plot.fig.axes[-1].remove()
    if legend:
        #default legend formating
        cols=2
        bbox=(1.1,0.7)
        text=""
        handle=[matplotlib.patches.Patch(color=colors(ind), label=label) for label, ind in zip(np.unique(labels), np.linspace(0, 1, len(np.unique(labels)), endpoint=True))]
        #increase legend columns if too many labels
        if len(labels)>1:
            text=max(map(str,labels), key = len)
        if len(np.unique(labels))>40:
            cols=cols + ceil(len(np.unique(labels))/40)
            bbox=(1.1, 0.3)
        #textwrap if longer than 10 characters
        if len(text)>10:
            lbls = [fill(str(lbl), 10) for lbl in np.unique(labels)]
            plt_legend=self.main_plot.axes.legend(handle, lbls, bbox_to_anchor=bbox, ncol=cols, loc=6, borderaxespad=0)#,loc='center right')
        else:
            plt_legend=self.main_plot.axes.legend(handle, list(np.unique(labels)),bbox_to_anchor=bbox, ncol=cols, loc=6, borderaxespad=0)#, loc='center right')
        if plt_legend:
            plt_legend.set_draggable(True)
    else:
        #add colorbar
        cb_ax = self.main_plot.fig.add_axes([0.625, 0.06, 0.02, 0.875])
        cbar = self.main_plot.fig.colorbar(self.plots[0], cax=cb_ax)
        #colorbar formatting
        if all(map(lambda x: isinstance(x, str), self.labels)):
            cbar.ax.tick_params(labelsize=0)
        else:
            cbar.ax.tick_params(labelsize=10)
        cbar.ax.yaxis.offsetText.set_fontsize(2)
        cbar.ax.zorder = 6
        cb_ax.yaxis.tick_right()
    #axis/title labels
    self.main_plot.axes.set_title(plot + " Plot")
    self.main_plot.axes.set_xlabel(plot + " 1")
    self.main_plot.axes.set_ylabel(plot + " 2")
    #save original x,y,z axis limits for resetview
    if new_plot:
        print(self.plots[-1].axes.get_xlim3d())
        self.original_xlim=[self.plots[-1].axes.get_xlim3d()[0], self.plots[-1].axes.get_xlim3d()[1]]
        self.original_ylim=[self.plots[-1].axes.get_ylim3d()[0], self.plots[-1].axes.get_ylim3d()[1]]
        self.original_zlim=[self.plots[-1].axes.get_zlim3d()[0], self.plots[-1].axes.get_zlim3d()[1]]
    self.main_plot.draw()

def reset_view(self):
    #reset to starting x, y, z limit
    self.main_plot.axes.set_xlim3d(self.original_xlim)
    self.main_plot.axes.set_ylim3d(self.original_ylim)
    self.main_plot.axes.set_zlim3d(self.original_zlim)
    #xy-plane view
    self.main_plot.axes.view_init(azim=-90, elev=90)
    self.main_plot.draw()

def legend_colors(self):
    try:
        #get plot rgb values
        legnd=self.main_plot.axes.get_legend()
        map_colors=[np.array(lbl.get_facecolor()[:-1]) for lbl in self.main_plot.axes.get_legend().legendHandles]

        #GUI colorpicker
        colors = colorchannelWindow(len(np.unique(self.labels)), map_colors[:], "Custom Colour Picker", "Labels", list(map(str, np.unique(self.labels))))
        colors = np.array(colors.color)
        # change plot colours
        if np.array_equal(colors, np.array(map_colors)) == False:
            for i in range(len(colors)):
                legnd.legendHandles[i].set_color(colors[i])
            cmap = mcolors.ListedColormap(colors)
            self.plots[0].set_cmap(cmap)
            self.main_plot.draw()
    except:
        errorWindow("Set Legend Colours", "Python Exception Error: {}".format(traceback.format_exc()))

#export current plot data and x, y, z limits
def save_file(self, map):
    name = QFileDialog.getSaveFileName(self, 'Save File', filter=self.tr('.json'))
    if name[0] !='':
        info = {
                'plot_projection': map,
                'plot_coordinates': [data.tolist() if isinstance(data,np.ndarray) else data for data in self.plot_data],
                'x_limit': self.original_xlim,
                'y_limit': self.original_ylim,
                'z_limit': self.original_zlim,
                'channel_paths':self.ch_path,
                'plot_columns':self.plotcols,
                'rawdata_columns':self.raw_col,
                'feature_filename': self.feature_file[0]
        }
        with open("".join(name), 'w') as f:
            json.dump(info, f)

#import plot data
def import_file(self, map_dropdown, colordropdown, twod, threed):
    filename= QFileDialog.getOpenFileName(self, 'Open Plot Data JSON File', '', 'JSON file (*.json)')[0]
    if filename != '':
        with open(filename, "r") as f:
            try:
                data=json.load(f)
                #validate json file
                if list(data.keys())==['plot_projection','plot_coordinates','x_limit','y_limit','z_limit',
                                       'channel_paths','plot_columns','rawdata_columns','feature_filename']:
                        plot_coord=[np.array(plot_data) for plot_data in data.get('plot_coordinates')]
                        if len(plot_coord)==3:
                            self.plot_data.clear()
                            #2d/3d set
                            if np.all(np.array(data.get('plot_coordinates')[2])) != 0:
                                threed.setChecked(True)
                            else:
                                twod.setChecked(True)
                            #set data from json file
                            self.plot_data.extend(plot_coord)
                            self.original_xlim = data.get('x_limit')
                            self.original_ylim = data.get('y_limit')
                            self.original_zlim = data.get('z_limit')
                            map_dropdown.blockSignals(True)
                            if map_dropdown.findText(data.get('plot_projection'))==-1:
                                map_dropdown.addItem(data.get('plot_projection'))
                            map_dropdown.setCurrentIndex(map_dropdown.findText(data.get('plot_projection')))
                            map_dropdown.blockSignals(False)
                            self.ch_path=data.get('channel_paths')
                            self.plotcols=data.get('plot_columns')
                            self.raw_col=data.get('rawdata_columns')
                            #call feature file selection columns
                            self.loadFeaturefile(colordropdown, map_dropdown, False, data.get('feature_filename'))
                        else:
                            errorWindow("Import Plot Data Error","Check JSON file. 'plot_coordinates' must be 3D (list of x, y, z coordinates)")
                else:
                    errorWindow("Import Plot Data Error", "Check if correct file. Requires Following Labels: plot_projection, plot_coordinates, x_limit , y_limit ,z_limit, 'feature_filename', 'channel_paths','plot_columns','rawdata_columns'")
            except Exception as ex:
                errorWindow("Import Plot Data Error", "Check if correct file. \n\nPython Error: {}".format(ex))
