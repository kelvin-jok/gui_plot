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
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import pandas as pd
from pandas.api.types import is_numeric_dtype
try:
    from .interactive_click import interactive_points
    from src.GUI.Windows.plot_functions import *
    from ...Training import *
except ImportError:
    from src.GUI.Windows.interactive_click import interactive_points
    from src.GUI.Windows.plot_functions import *
    from src.Training import *

class displayWindow(QWidget):
    def __init__(self):
        QMainWindow.__init__(self)
        super(displayWindow, self).__init__()
        self.setWindowTitle("Results")
        self.feature_file=[]
        self.imageIDs=[]
        self.plots=[]
        self.filtered_data=0
        self.ch_path = []
        self.plotcols = []
        self.raw_col= [] #ADD 3d rotate if z-axis
        self.numcluster=None
        self.bounds=0
        self.color = [(0, 0.45, 0.74),(0.85, 0.33, 0.1), (0.93, 0.69, 0.13)]
        #self.color=color $image channel colours from main gui
        #menu tabs
        menubar = QMenuBar()
        file = menubar.addMenu("File")
        inputfile = file.addAction("Input Feature File")
        data = menubar.addMenu("Data Analysis")
        classification = data.addMenu("Classification")
        selectclasses = classification.addAction("Select Classes")
        clustering = data.addMenu("Clustering")
        estimate = clustering.addAction("Estimate Clusters")
        setnumber = clustering.addAction("Set Number of Clusters")
        piemaps = clustering.addAction("Pie Maps")
        export = clustering.addAction("Export Cluster Results")
        plotproperties = menubar.addMenu("Plot Properties")
        rotation_enable = plotproperties.addAction("Enable 3D Rotation (Left-Click) & Zoom (Right-Click)")
        rotation_disable = plotproperties.addAction("Disable 3D Rotation & Zoom")
        resetview = plotproperties.addAction("Reset Plot View")

        # defining widgets
        box = QGroupBox()
        boxlayout = QGridLayout()
        selectfile = QPushButton("Select Feature File")
        prevdata = QPushButton("Import Previous Plot Data (.JSON)")
        exportdata = QPushButton("Export Current Plot Data (.JSON)")
        cmap=QPushButton("Legend Colours")
        map_type = QComboBox()
        map_type.addItems(["PCA","t-SNE","UMAP","Sammon"])
        twod = QRadioButton("2D")
        threed = QRadioButton("3D")
        data_columns=QPushButton("Change Plot Data Columns")
        dimensionbox = QGroupBox()
        dimensionboxlayout = QHBoxLayout()
        dimensionboxlayout.addWidget(twod)
        dimensionboxlayout.addWidget(threed)
        dimensionbox.setLayout(dimensionboxlayout)
        colordropdown = QComboBox()
        boxlayout.addWidget(QLabel("File Options"), 0, 0, 1, 1)
        boxlayout.addWidget(selectfile, 1, 0, 1, 1)
        boxlayout.addWidget(exportdata, 2, 0, 1, 1)
        boxlayout.addWidget(prevdata, 3, 0, 1, 1)
        boxlayout.addWidget(QLabel("Plot Type"), 0, 1, 1, 1)
        boxlayout.addWidget(map_type, 1, 1, 1, 1)
        boxlayout.addWidget(dimensionbox, 2, 1, 1, 1)
        boxlayout.addWidget(data_columns, 3, 1, 1, 1)
        boxlayout.addWidget(cmap, 2, 2, 1, 1)
        boxlayout.addWidget(QLabel("Color By"), 0, 2, 1, 1)
        boxlayout.addWidget(colordropdown, 1, 2, 1, 1)
        box.setLayout(boxlayout)
        #menu actions activated
        inputfile.triggered.connect(lambda: self.loadFeaturefile(colordropdown, map_type, True))
        selectclasses.triggered.connect(lambda: TrainingFunctions().selectclasses(np.array(self.filtered_data), np.array(self.labels)) if len(self.plot_data)>0 else errorWindow("Error Dialog","Please Select Feature File. No data is currently displayed"))
        estimate.triggered.connect(lambda: Clustering().cluster_est(self.filtered_data) if len(self.plot_data) > 0 else errorWindow("Error Dialog","Please Select Feature File. No data is currently displayed"))
        setnumber.triggered.connect(lambda: self.setnumcluster(colordropdown.currentText()) if len(self.plot_data) > 0 else errorWindow("Error Dialog","Please Select Feature File. No data is currently displayed"))
        piemaps.triggered.connect(lambda: piechart(self.plot_data, self.filtered_data, self.numcluster, np.array(self.labels), self.plot[0].get_cmap()) if len(self.plot_data) > 0 else errorWindow("Error Dialog","Please Select Feature File. No data is currently displayed"))
        export.triggered.connect(lambda: export_cluster(self.plot_data, self.filtered_data, self.numcluster, self.feature_file[0]) if len(self.plot_data) >0 else errorWindow("Error Dialog","Please Select Feature File. No data is currently displayed"))
        rotation_enable.triggered.connect(lambda: self.main_plot.axes.mouse_init())
        rotation_disable.triggered.connect(lambda: self.main_plot.axes.disable_mouse_rotation())
        resetview.triggered.connect(lambda: reset_view(self))
        exportdata.clicked.connect(lambda: save_file(self, map_type.currentText()) if len(self.plot_data) > 0 else errorWindow("Error Dialog","Please Select Feature File. No data is currently displayed"))
        prevdata.clicked.connect(lambda: import_file(self, map_type, colordropdown, twod, threed))
        #setup Matplotlib
        matplotlib.use('Qt5Agg')
        self.plot_data = []
        self.labels = []
        self.main_plot = MplCanvas(self, width=10, height=10, dpi=100, projection="3d")
        sc_plot = self.main_plot.axes.scatter3D([], [], [], s=10, alpha=1, depthshade=False)  # , picker=True)
        self.main_plot.axes.set_position([-0.2, -0.05, 1, 1])
        self.main_plot.axes.set_facecolor("grey")
        self.main_plot.fig.set_facecolor("grey")
        self.original_xlim = sc_plot.axes.get_xlim3d()
        self.original_ylim = sc_plot.axes.get_ylim3d()
        self.original_zlim = sc_plot.axes.get_zlim3d()
        self.projection = "2d"  # update from radiobutton
        #2d vs 3d settings
        def check_projection(dim, plot):
            if dim == "2d":
                self.projection = dim
                self.main_plot.axes.mouse_init()
                self.main_plot.axes.view_init(azim=-90, elev=90)
                self.main_plot.axes.get_zaxis().line.set_linewidth(0)
                self.main_plot.axes.tick_params(axis='z', labelsize=0)
                self.main_plot.draw()
                self.main_plot.axes.disable_mouse_rotation()
            elif dim == "3d":
                self.projection = dim
                self.main_plot.axes.get_zaxis().line.set_linewidth(1)
                self.main_plot.axes.tick_params(axis='z', labelsize=10)
                self.main_plot.draw()
                #rotate left click, zoom right click
                self.main_plot.axes.mouse_init()
            if self.feature_file and colordropdown.count() > 0 and len(self.plot_data)>0:
                self.data_filt(colordropdown, self.projection, plot, True)

        # button features and callbacks
        selectfile.clicked.connect(lambda: self.loadFeaturefile(colordropdown, map_type, True))
        cmap.clicked.connect(lambda: legend_colors(self) if len(self.labels)>0 else errorWindow("Error Dialog","Please Select Feature File. No data is currently displayed"))
        twod.toggled.connect(lambda: check_projection("2d", map_type.currentText()) if twod.isChecked() else None)
        threed.toggled.connect(lambda: check_projection("3d", map_type.currentText()) if threed.isChecked() else None)
        twod.setChecked(True)
        data_columns.clicked.connect(lambda: self.loadFeaturefile(colordropdown, map_type, True, prevfile=self.feature_file[0]) if self.feature_file else None)
        picked_pt = interactive_points(self.main_plot, self.projection, self.plot_data, self.labels,self.ch_path, self.feature_file, self.color, self.imageIDs, colordropdown)
        self.main_plot.fig.canvas.mpl_connect('pick_event', picked_pt)
        colordropdown.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, self.projection, map_type.currentText(),False) if self.feature_file and colordropdown.count() > 0 else None)
        map_type.currentIndexChanged.connect(lambda: self.data_filt(colordropdown, self.projection, map_type.currentText(),True) if self.feature_file and colordropdown.count() > 0 else None)

        # building layout
        layout = QGridLayout()
        toolbar = NavigationToolbar(self.main_plot, self)
        layout.addWidget(toolbar, 0, 0, 1, 1)
        layout.addWidget(self.main_plot, 1, 0, 1, 1)
        layout.addWidget(box, 2, 0, 1, 1)
        layout.setMenuBar(menubar)
        self.setLayout(layout)
        minsize = self.minimumSizeHint()
        minsize.setHeight(self.minimumSizeHint().height() + 700)
        minsize.setWidth(self.minimumSizeHint().width() + 700)
        self.setFixedSize(minsize)

    def loadFeaturefile(self, grouping, plot, new_plot, prevfile=None):
        filename=''
        if new_plot and isinstance(prevfile, type(None)):
            filename, dump = QFileDialog.getOpenFileName(self, 'Open Feature File', '', "Text files (*.txt *.csv)")#, 'Text files (*.txt))
            print(filename, dump)
        elif isinstance(prevfile, str) and os.path.exists(prevfile) == False:
            errorWindow("Feature File Error","Feature File Path found in selected Plot Data file does not exist: \n'{}'".format(prevfile))
        if filename != '' or (not isinstance(prevfile, type(None)) and os.path.exists(prevfile)):
            #try:
                self.feature_file.clear()
                if new_plot and filename:
                    self.feature_file.append(filename)
                else:
                    self.feature_file.append(prevfile)
                print(self.feature_file)
                grouping, cancel=self.color_groupings(grouping, plot, new_plot)
                if not cancel:
                    reset_view(self)
                    self.data_filt(grouping, self.projection, plot.currentText(), new_plot)
                    self.numcluster=None
            #except Exception as ex:
                if len(self.plot_data)==0:
                    grouping.clear()
            #    errorWindow("Feature File Error", "Check Validity of Feature File (.txt). \nPython Exception Error: {}".format(ex))


    def color_groupings(self, grouping, plot, new_plot):
        #read feature file
        if 'csv' in self.feature_file[0]:
            df = pd.read_csv(self.feature_file[0], nrows=1, na_values='NaN')
        else:
            df=pd.read_csv(self.feature_file[0], sep='\t', nrows=1,na_values='NaN') #.txt files
        chk_lbl=list(df.columns) #get all columns for labels
        num_lbl=list(df._get_numeric_data().columns) #only numerical columns for analysis

        grouping.blockSignals(True)
        grp=[]
        if grouping.count()>1:
            grp=[grouping.itemText(i + 1) for i in range(grouping.count() - 1)]

        #select features window
        win=selectWindow(chk_lbl, "Column Selection - Feature File", "Grouping", "Channels", grp, df, self.ch_path, self.plotcols, self.raw_col, True, num_lbl)
        if not win.x_press:
            #change colorby window
            grouping.clear()
            grouping.addItem("No Grouping")
            if win.colorby_txt.toPlainText() not in ['No Selected Columns', '']:
                for col in win.colorby_txt.toPlainText().rsplit("\n"):
                    grouping.addItem(col)

            #renew selected path & data columns
            self.ch_path.clear()
            self.plotcols.clear()
            self.raw_col.clear()

            if win.chcols.toPlainText() not in ['No Selected Columns', '']:
                #add path button used
                if win.imgpath!='Add Path':
                    self.ch_path.extend([win.imgpath] + win.chcols.toPlainText().rsplit('\n'))
                #path exists in filename
                else:
                    self.ch_path.extend(win.chcols.toPlainText().rsplit('\n'))
            #selected plot columns
            if win.plotcols.toPlainText() not in ['No Selected Columns', '']:
                self.plotcols.extend(win.plotcols.toPlainText().rsplit('\n'))
            self.raw_col=[box.currentText() for box in win.axis.boxes]

            if len(self.raw_col)>0 and self.raw_col.count("None")<2:
                if plot.findText("Raw Data")==-1:
                    plot.addItem("Raw Data")
                if new_plot:
                    plot.setCurrentIndex(plot.findText("Raw Data"))
        grouping.blockSignals(False)
        return(grouping, win.x_press)

    def data_filt(self, grouping, projection, plot, new_plot):
        filter_data = grouping.currentText()
        if 'csv' in self.feature_file[0]:
            feature_data = pd.read_csv(self.feature_file[0], na_values='        NaN')
        else:
            feature_data = pd.read_csv(self.feature_file[0], sep='\t', na_values='        NaN')
        def id_labels(feature_data, X, plot):
            print('Dataset shape:', feature_data.shape)
            if plot!='Raw Data':
                self.filtered_data = X.to_numpy().astype(np.float64)
            else:
                self.filtered_data=np.array([X[col].tolist() if col in X.columns else np.zeros(X.shape[0]) for col in self.raw_col])
            # reset labels
            z = np.ones(X.shape[0]).astype(int)
            self.labels.clear()
            if filter_data != "No Grouping":
                if is_numeric_dtype(feature_data[filter_data]):
                    z = np.array(feature_data[filter_data])
                    self.labels.extend(z.tolist())
                else:
                    z = np.array(feature_data[filter_data], dtype='object')
                    self.labels.extend(list(map(str, z)))
            else:
                self.labels.extend(z.tolist())

            print(self.labels)
            result_plot(self, self.filtered_data, projection, plot, new_plot)

        if plot =="Raw Data":
            X=feature_data.copy()
            X=X[np.array(self.raw_col)[np.where(np.array(self.raw_col)!='None')]]

            X.dropna(axis=0, inplace=True)
            print(X)
            print(feature_data)
            id_labels(feature_data, X, plot)
        else:
            featurecols=self.plotcols

            # remove non-finite/ non-scalar valued rows in both
            feature_data = feature_data[np.isfinite(feature_data[featurecols]).all(1)]
            # min-max scale all data
            mind = np.min(feature_data[featurecols], axis=0)
            maxd = np.max(feature_data[featurecols], axis=0)

            if np.array_equal(mind, maxd) == False:
                featuredf = (feature_data[featurecols] - mind) / (maxd - mind)
                #drop cols with nan
                featuredf.dropna(axis=1, inplace=True)
                id_labels(feature_data, featuredf, plot)
            else:
                errorWindow('Feature File Data Error', 'Check if have more than 1 row of data and that min and max values of MV or texture columns are not the same')

    def setnumcluster(self, group):
        clustnum=setcluster(self.numcluster, self.filtered_data, self.plot_data, np.array(self.labels), group)
        self.numcluster=clustnum.clust

    def closeEvent(self, event):
        # print("closed all windows")
        for window in QApplication.topLevelWidgets():
            window.close()

def show_displayWindow():
    """Show the window and run the application exec method to start the GUI"""
    app = QApplication(sys.argv)
    window = displayWindow()
    window.show()
    app.exec()
# end resultsWindow
