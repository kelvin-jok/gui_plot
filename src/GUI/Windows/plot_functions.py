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

def treatment_bounds(data, bounds, id, treatmentcol):

    try:
        trt = data[treatmentcol].iloc[id]
        trt_loc =int(np.where(data[treatmentcol].unique() == trt)[0])

        bound = [bounds[0][trt_loc], bounds[1][trt_loc]]
        return(bound)
    except Exception as ex:
        win = errorWindow("Error TreatmentNorm","intensityNormPerTreatment was set with error: {}".format(ex))
        return(False)


def merge_channels(data, rgb_img, ch_len, scroller_value, color, meta_loc, box, bounds, IntensityThreshold):
    # threshold/colour each image channel
    for ind, rgb_color in zip(range(scroller_value, scroller_value + ch_len), color):
        ch_num = str(ind - scroller_value + 1)
        data['Channel_' + ch_num] = data['Channel_' + ch_num].str.replace(r'\\', '/', regex=True)
        cur_img = np.array(PIL.Image.open(data['Channel_' + ch_num].iloc[meta_loc + scroller_value]))
        # medianfilter for slice or MIP projection
        if box == False:
            cur_img = medianBlur(cur_img, 3)
        cur_img= (cur_img - bounds[0][int(ch_num)-1])/(bounds[1][int(ch_num)-1]-bounds[0][int(ch_num)-1]) #bounds from metadata functions compute
        cur_img[cur_img < IntensityThreshold[0][int(ch_num)-1]] = 0
        cur_img[cur_img > 1] = 1
        cur_img = np.dstack((cur_img, cur_img, cur_img))
        rgb_img[int(ch_num) - 1, :, :, :] = np.multiply(cur_img, rgb_color)
    # compute average and norm to mix colours
    rgb_img = np.sum(rgb_img, axis=0)
    max_rng = [np.max(rgb_img[:, :, i]) if np.max(rgb_img[:, :, i]) > 0 else 1 for i in range(3)]
    rgb_img = np.divide(rgb_img, max_rng)
    return (rgb_img)

def result_plot(self, X, projection, plot, new_plot):
    #reset plot
    self.main_plot.axes.clear()
    del self.plots[:]
    if new_plot:
        dim=int(projection[0])
        self.plot_data.clear()
        if plot=="Raw Data":
            #print(X.shape[0])
            #print(X.columns)
            #print([print(col) for col in self.raw_col])
            #[print(col) if col in X.columns else print(None) for col in self.raw_col]
            #P=[X[col].tolist() if col in X.columns else np.zeros(X.shape[0]) for col in self.raw_col]û
            #print(P)
            print(X)
            self.plot_data.extend(X.tolist())
            print(self.plot_data)
        else:
            #send to clustering.py for PCA, Sammon, t-SNE analysis
            P=Clustering().plot_type(X, dim, plot)
            #save new x, y, z data
            self.plot_data.append(P[:,0])
            self.plot_data.append(P[:,1])
            if dim==3:
                self.plot_data.append(P[:, 2])
            else:
                self.plot_data.append(np.zeros(len(self.plot_data[-1])))
    #plot data
    print("here3")
    print(len(np.unique(self.labels)))
    lbl_size=len(np.unique(self.labels))
    colors = plt.cm.get_cmap('gist_rainbow')
    #colors = matplotlib.colormaps['gist_ncar']
    print(colors(0))
    print(colors(257))
    #colors=matplotlib.colors.Colormap('gist_ncar', N=len(np.unique(self.labels)))
    #colors = plt.cm.get_cmap('gist_ncar', lbl_size)#(np.linespace(0,1, lbl_size))
    #colors= plt.cm.get_cmap('gist_ncar')(range(0,256,floor(255/len(np.unique(self.labels)))))
    #colors = plt.cm.get_cmap('gist_ncar')(range(len(np.unique(self.labels))))
    print(np.shape(plt.cm.get_cmap('gist_ncar')(range(0,256,floor(255/len(np.unique(self.labels)))))))
    print(plt.cm.get_cmap('gist_ncar')(range(0,256,floor(255/len(np.unique(self.labels))))))
    print([matplotlib.colors.to_hex(colors(i)) for i in np.linspace(0,1, len(np.unique(self.labels)), endpoint=True)])
    #print([list(colors(i)) for i in np.linspace(0, 255, len(np.unique(self.labels)), endpoint=True)])
    print(colors)
    from sklearn import preprocessing
    le = preprocessing.LabelEncoder()
    #lbls=list(map(str, self.labels))
    print(self.labels)
    lbls=self.labels
    print(lbls)
    le.fit(lbls)
    print(le.classes_)
    cat=np.array(le.transform(lbls))
    print(cat)
    self.imageIDs.clear()
    self.imageIDs.extend(cat)

    print([list(colors(i)) for i in np.linspace(0, 255, len(np.unique(self.labels)), endpoint=True)])
    cmap= mcolors.ListedColormap([list(colors(i)) for i in np.linspace(0, 1, len(np.unique(self.labels)), endpoint=True)])
    legend=True
    #if len(np.unique(self.labels))>1:# and len(np.unique(self.labels))<100:
    print('labels')
    print(cmap)
    print(np.shape([colors(i) for i in np.linspace(0,1, len(np.unique(self.labels)), endpoint=True)]))
    try:
        self.plots.append(
           self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], s=10, alpha=1, depthshade=False, picker=1.5, c=cat, cmap=cmap))
                                         #c=cat, alpha=1, depthshade=False, picker=1.5, cmap= 'gist_rainbow'))#'[list(colors(i)) for i in np.linspace(0, 255, len(np.unique(self.labels)), endpoint=True)]))
    except:
        print(traceback.format_exc())
        #self.plots.append(
        #    self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], label=self.labels, s=10,
        #                                  colors=colors, alpha=1, depthshade=False, picker=1.5))#, cmap=colors))
       # for label, i in zip(np.unique(self.labels), range(len(np.unique(self.labels)))):
        #    print("plot")
         #   self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0][np.where(np.array(self.labels)==label)[0]], self.plot_data[1][np.where(np.array(self.labels)==label)[0]], self.plot_data[2][np.where(np.array(self.labels)==label)[0]], label=label,
          #                  s=10, alpha=1, color=[colors[i]], depthshade=False, picker=1.5, cmap=colors))
    #elif len(np.unique(self.labels))==1:
    #    print('one')
    #    self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0], self.plot_data[1], self.plot_data[2], label=self.labels[0],
    #    s=10, alpha=1,color=[colors(0)], depthshade=False, picker=2, cmap=colors))
    #else:
    #    print('else')
    #    self.plots.append(self.main_plot.axes.scatter3D(self.plot_data[0],self.plot_data[1],self.plot_data[2],c=self.labels,s=10, alpha=1, depthshade=False, picker=1.5,cmap=plt.cm.get_cmap('gist_ncar')))
    '''
        cb_ax = self.main_plot.fig.add_axes([0, 0.01, 0.02, 0.875])
        cbar = self.main_plot.fig.colorbar(self.plot[0], cax=cb_ax)
        cbar.ax.tick_params(labelsize=3)
        cbar.ax.yaxis.offsetText.set_fontsize(2)
        cbar.ax.zorder = 6
        cb_ax.yaxis.tick_left()
    '''
    if len(np.unique(lbls)) > 50: #if more than 50 labels default to colorbar
        legend=False
    print("plotted")
    legend_format(self, plot, colors, new_plot, lbls, legend)
def legend_format(self, plot, colors, new_plot, labels, legend):
    print(legend)
    if legend:
        #default legend formating
        cols=2
        #bbox = (0.5, 0.5, 0.3, 1)
        #bbox=(1.1, 0.5, 0.3, 0.5)
        bbox=(1.1,0.7)
        text=""
        print(np.linspace(0, 1, len(self.labels), endpoint=True))
        handle=[matplotlib.patches.Patch(color=colors(ind), label=label) for label, ind in zip(np.unique(labels), np.linspace(0, 1, len(np.unique(labels)), endpoint=True))]
        print("herehandle")
        #increase legend columns if too many labels
        if len(labels)>1:
            text=max(map(str,labels), key = len)
        if len(np.unique(labels))>40:
            cols=cols + ceil(len(np.unique(labels))/40)
            bbox=(1.1, 0.3)
            #bbox=(1.6, 0.5, 0.3, 1)
        #textwrap if longer than 10 characters
        print(len(text))
        if len(text)>10:
            lbls = [fill(str(lbl), 20) for lbl in np.unique(labels)]
            plt_legend=self.main_plot.axes.legend(handle, lbls, bbox_to_anchor=bbox, ncol=cols, loc=6, borderaxespad=0)#,loc='center right')
        else:
            plt_legend=self.main_plot.axes.legend(handle, list(np.unique(labels)),bbox_to_anchor=bbox, ncol=cols, loc=6, borderaxespad=0)#, loc='center right')
        '''    
        def legend_scroll(event):
            if plt_legend.contains(event):
                bbox = plt_legend.get_bbox_to_anchor()
                if event.mouseevent.button is MouseButton.RIGHT:
                    bbox = Bbox.from_bounds(bbox.x0, bbox.y0 + 20, bbox.width, bbox.height)
                elif event.mouseevent.button is MouseButton.RIGHT:
                    bbox = Bbox.from_bounds(bbox.x0, bbox.y0 - 20, bbox.width, bbox.height)
                tr = plt_legend.axes.transAxes.inverted()
                plt_legend.set_bbox_to_anchor(bbox.transformed(tr))
                fig.canvas.draw_idle()

        self.main_plot.fig.canvas.mpl_connect('button_press_event', legend_scroll)
        '''
        def legend_scroll(event):
                bbox = plt_legend.get_bbox_to_anchor()
                if event.inaxes is not None:
                    print(event.key)
                    if event.key=='up':
                        bbox = Bbox.from_bounds(bbox.x0, bbox.y0 + 20, bbox.width, bbox.height)
                    elif event.key=='down':
                        bbox = Bbox.from_bounds(bbox.x0, bbox.y0 - 20, bbox.width, bbox.height)
                    tr = plt_legend.axes.transAxes.inverted()
                    plt_legend.set_bbox_to_anchor(bbox.transformed(tr))
                    fig.canvas.draw_idle()
        cid = self.main_plot.fig.canvas.mpl_connect('scroll_event', legend_scroll)
        #try: #remove colorbar if legend
            #self.main_plot.colorbar
        self.main_plot.draw()
    else:
        cb_ax = self.main_plot.fig.add_axes([0.625, 0.06, 0.02, 0.875])
        print("bar")
        cbar = self.main_plot.fig.colorbar(self.plots[0], cax=cb_ax)
        print("bar2")
        cbar.ax.tick_params(labelsize=10)
        cbar.ax.yaxis.offsetText.set_fontsize(2)
        cbar.ax.zorder = 6
        cb_ax.yaxis.tick_right()
        self.main_plot.draw()
        cbar.remove()
    #axis/title labels
    self.main_plot.axes.set_title(plot + " Plot")
    self.main_plot.axes.set_xlabel(plot + " 1")
    self.main_plot.axes.set_ylabel(plot + " 2")
    #save original x,y,z axis limits for resetview
    if new_plot:
        self.original_xlim=[self.plots[-1].axes.get_xlim3d()[0], self.plots[-1].axes.get_xlim3d()[1]]
        self.original_ylim=[self.plots[-1].axes.get_ylim3d()[0], self.plots[-1].axes.get_ylim3d()[1]]
        self.original_zlim=[self.plots[-1].axes.get_zlim3d()[0], self.plots[-1].axes.get_zlim3d()[1]]
    #self.main_plot.draw()
    #https: // stackoverflow.com / questions / 55863590 / adding - scroll - button - to - matlibplot - axes - legend


def reset_view(self):
    #reset to starting x, y, z limit
    self.main_plot.axes.set_xlim3d(self.original_xlim)
    self.main_plot.axes.set_ylim3d(self.original_ylim)
    self.main_plot.axes.set_zlim3d(self.original_zlim)
    #xy-plane view
    self.main_plot.axes.view_init(azim=-90, elev=90)
    self.main_plot.draw()

def legend_colors(self):
    #get plot rgb values
    lgd=self.main_plot.axes.get_legend()
    print(lgd)
    print(lgd.legendHandles)
    print(lgd.legendHandles[0].get_facecolor())
    print(self.plots[0].get_facecolor())
    map_colors=[np.array(lbl.get_facecolor()[:-1]) for lbl in self.main_plot.axes.get_legend().legendHandles]
    #lbl, lbl_ind=np.unique(self.labels, return_index=True)
    #map_colors, ind = np.unique(self.plots[0].get_facecolor(), return_index=True, axis=0)
    #map_colors=map_colors[np.argsort(ind)]
    #map_colors = [np.array(self.plots[0].get_facecolor()[ind][:-1]) for ind in lbl_ind]
    #map_colors = [np.array(rgb[:-1]) for rgb in map_colors]
    print(map_colors)
    print(type(map_colors))
    print(map_colors[:])
    print(self.labels)
    #print(ind)
    #print(np.array(self.labels)[ind])
    print(len(np.unique(self.labels)))
    print(np.unique(self.labels).astype(int))
    print(list(map(str, np.unique(self.labels))))
    #map_colors=[np.array(plot.get_facecolor()[0][0:3]) for plot in self.plots]
    #GUI colorpicker
    try:
        colors = colorchannelWindow(len(np.unique(self.labels)), map_colors[:], "Custom Colour Picker", "Labels", list(map(str, np.unique(self.labels))))
    except:
        import traceback
        print(traceback.format_exc())
    colors=np.array(colors.color)
    print("here")
    #change plot colours
    if np.array_equal(colors, np.array(map_colors))==False:
        legend = self.main_plot.axes.get_legend()
        print(legend, "herelegend")
        for i in range(len(colors)):
            legend.legendHandles[i].set_color(colors[i])
            print(colors[i])
        print(colors)
        try:
            print("here")
            cmap=mcolors.ListedColormap(colors)
            print("here2")
            print(dir(self.plots[0]))
            self.plots[0].set_cmap(cmap)
            print("here3")
            self.main_plot.draw()
            print("here4")
        except:
            print(traceback.format_exc())
        #self.plot[0].set_color(colors)
        '''
        if len(np.unique(self.labels))>1:
            for i in range(len(np.unique(self.labels))):
                self.plots[i].set_color(colors[i])
                legend.legendHandles[i].set_color(colors[i])
        else:
            self.plots[0].set_color(colors[0])
            legend.legendHandles[0].set_color(colors[0])
        '''


#export current plot data and x, y, z limits
def save_file(self, map):
    name = QFileDialog.getSaveFileName(self, 'Save File', filter=self.tr('.json'))
    print(name)
    print(map)
    print(self.original_xlim, self.original_ylim, self.original_zlim)
    print(self.feature_file[0])
    print([isinstance(data,np.ndarray) for data in self.plot_data])
    print([data.tolist() if isinstance(data,np.ndarray) else data for data in self.plot_data])
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
        print(info)
        with open("".join(name), 'w') as f:
            json.dump(info, f)

#import plot data
def import_file(self, map_dropdown, colordropdown, twod, threed):
    filename= QFileDialog.getOpenFileName(self, 'Open Plot Data JSON File', '', 'JSON file (*.json)')[0]
    if filename != '':
        with open(filename, "r") as f:
            try:
                data=json.load(f)
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
                            self.loadFeaturefile(colordropdown, map_dropdown, False, data.get('feature_filename'))
                        else:
                            errorWindow("Import Plot Data Error","Check JSON file. 'plot_coordinates' must be 3D (list of x, y, z coordinates)")
                else:
                    errorWindow("Import Plot Data Error", "Check if correct file. Requires Following Labels: plot_projection, plot_coordinates, x_limit , y_limit ,z_limit, 'feature_filename', 'channel_paths','plot_columns','rawdata_columns'")
            except Exception as ex:
                errorWindow("Import Plot Data Error", "Check if correct file. \n\nPython Error: {}".format(ex))

class raw_columns_select(object):
    def __init__(self, columns, win_title, col_title):
        # main layout
        win = QDialog()
        win.setWindowTitle(win_title)
        title = QLabel(col_title)
        raw_data_layout = QVBoxLayout()
        ok_button = QPushButton("OK")
        raw_check = checkbox('Select Data Column Axes', ["Plot Raw Data (Note: At least two axes must be value other than None"],
                             raw_data_layout, [], False)
        axis = dropdownbox(['x-axis', 'y-axis', 'z-axis'], raw_data_layout)
        for box in axis:
            box.clear()
            box.addItems(['None'] + columns)
        raw_data_layout.addWidget(ok_button)

        ok_button.clicked.connect(lambda: self.confirm(axis))

    def confirm(self, axis):
        axes=[box.currentText() for box in axis]

