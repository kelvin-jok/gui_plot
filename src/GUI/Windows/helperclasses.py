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

# These classes are not windows, but help build other features in windows
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
import numpy as np
from math import ceil
from collections import OrderedDict
import os
import sys
from itertools import compress
import pandas as pd

# matplotlib figure-plot creation
class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=5, dpi=100, projection="3d"):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        if projection == "3d":
            self.axes = self.fig.add_subplot(111, projection=projection)
        else:
            self.axes = self.fig.add_subplot(111, projection=None)
        super(MplCanvas, self).__init__(self.fig)
        self.cmap = None

    def setNearFull(self):
        self.axes.set_aspect('auto')
        self.axes.set_position([0.01, 0.01, 0.98, 0.98])


# imported matplotlib toolbar. Only use desired functions.
class NavigationToolbar(NavigationToolbar):
    NavigationToolbar.toolitems = (
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        (None, None, None, None),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        (None, None, None, None),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure')
    )

# General PyQt Checkbox/check all
class checkbox(object):
    def __init__(self, grp_title, chk_lbl, win, chk_loc, all_btn, text=False, col_filt=False):
        # checkbox setup
        self.grp_box = QGroupBox()
        self.grp_box.setFlat(True)
        self.grp_list = []
        grp_vbox = QVBoxLayout()
        #title
        if grp_title !="":
            grp_title = QLabel(grp_title)
            grp_title.setFont(QFont('Arial', 20))
            grp_vbox.addWidget(grp_title)
        # add checkboxes to layout
        for lbl in chk_lbl:
            self.grp_list.append(QCheckBox(lbl))
            grp_vbox.addWidget(self.grp_list[-1])
        # select all button
        if all_btn:
            self.all_button = QPushButton("Select All")
            grp_vbox.addWidget(self.all_button)
            # regular checkbox
            if isinstance(text, bool):
                self.all_button.clicked.connect(lambda: [box.setChecked(True) for box in self.grp_list])
            # filtertext all select columns
            #else:
            #    all_button.clicked.connect(lambda: col_filt.setText('\n'.join(text)))
        self.grp_box.setLayout(grp_vbox)
        #gridlayout
        if len(chk_loc) == 2:
            win.layout().addWidget(self.grp_box, chk_loc[0], chk_loc[1], 1, 1)
        #boxlayout
        else:
            win.addWidget(self.grp_box)

#General PyQt dropboxcreation
class dropdownbox(object):
    def __init__(self, labels, cols, layout):
        self.boxes = [QComboBox() for x in range(len(labels))]
        for lbl, box in zip(labels, self.boxes):

            layout.addWidget(QLabel(lbl))
            layout.addWidget(box)
        layout.addStretch(1)


# selectclasses and featurefile checkbox window
class selectWindow(object):
    def __init__(self, chk_lbl, win_title, grp_title, col_title, groupings, rowdata, chan_cols="", plot_cols="", raw_cols="", filter_window=False, filter_lbl=False):
        win = QDialog()
        win.setWindowTitle(win_title)
        win.setLayout(QGridLayout())
        self.x_press = True
        self.imgpath=""
        ok_button = QPushButton("OK")

        # setup checkbox for groups
        if len(chk_lbl) > 0:
            if filter_window:
                #select columns for each category
                old_path="".join(list(filter(lambda x: os.path.exists(x), chan_cols)))
                ch_cols=list(filter(lambda x: not os.path.exists(x) and len(x)>0, chan_cols))
                ch_btn, self.chcols, ch_path = self.select_column(["Select Filename Columns", "Add Path"], "Image Filename Column \n(Note: Must use Add Path button below if path not in dataset)", win, 0, 0,  (lambda x: "\n".join(x) if len(x)>0 else "No Selected Columns" )(ch_cols))
                if old_path:
                    if len(old_path) > 50:
                        old_path = '\n'.join(old_path[i + 49 * i:i + 50 * (i + 1)] for i in range(ceil(len(old_path) / 50)))
                    ch_path.setText(old_path)
                colorby_btn, self.colorby_txt = self.select_column(["Labels groups"], "Labels Column Selection\n", win, 0, 1, (lambda x: "\n".join(x)  if len(x)>0 else "No Selected Columns" )(groupings))
                plotcol_btn, self.plotcols = self.select_column(["Select Plot Data Columns"], " Current Plot Data Selection\n", win, 0, 2, (lambda x: "\n".join(x) if len(x)>0 else "No Selected Columns" )(plot_cols))
                #plotting raw data vs dimensionality reduction
                raw_data_layout = QVBoxLayout()
                raw_box = checkbox('Dimesion Reductionality Plot Analysis', ["Optional Checkbox: Plot Raw Data (Note: At least two axes must be value other than None)"], raw_data_layout, [], False)
                self.axis = dropdownbox(['x-axis (only for Plot Raw Data)', 'y-axis (only for Plot Raw Data)', 'z-axis (only for Plot Raw Data)'], raw_cols, raw_data_layout)

                win.layout().addLayout(raw_data_layout, 0, 3)
                win.layout().addWidget(ok_button, 1, 3)

                #signal callbacks
                colorby_btn.clicked.connect(lambda: self.filtered_col(chk_lbl, "Color Column Selection", "Press to Add/Remove Columns", self.colorby_txt))
                ch_btn.clicked.connect(lambda: self.filtered_col(chk_lbl, "Imagefile Column Selection", "Press to Add/Remove Columns", self.chcols, data=rowdata, user_path=ch_path.text().replace("\n", "")))
                plotcol_btn.clicked.connect(lambda: self.filtered_col(filter_lbl, "Plot Data Column Selection", "Press to Add/Remove Columns", self.plotcols,self.axis.boxes, raw_box.grp_box.findChildren(QCheckBox)[0].isChecked()))
                #reduce_box.grp_box.findChildren(QCheckBox)[0].stateChanged.connect(lambda: raw_box.grp_box.findChildren(QCheckBox)[0].setChecked(False) if reduce_box.grp_box.findChildren(QCheckBox)[0].isChecked()==True else None)
                raw_box.grp_box.findChildren(QCheckBox)[0].stateChanged.connect(lambda: [box.addItems(['None'] + self.plotcols.toPlainText().rsplit('\n')) for box in self.axis.boxes if self.plotcols.toPlainText()!="No Selected Columns"]
                                                                                        if raw_box.grp_box.findChildren(QCheckBox)[0].isChecked()==True else [box.clear() for box in self.axis.boxes])
                ok_button.clicked.connect(lambda: self.selected(win, groupings, self.colorby_txt.toPlainText(), raw_box.grp_box.findChildren(QCheckBox)[0].isChecked(), self.axis.boxes, user_path=ch_path))

                if len(raw_cols) > 0 and raw_cols!=["None"]*3:
                    print(self.plotcols.toPlainText())
                    raw_box.grp_box.findChildren(QCheckBox)[0].setChecked(True)
                    [box.setCurrentText(col) for box, col in zip(self.axis.boxes, raw_cols)]
            else:
                lbl_box = checkbox(grp_title, chk_lbl, win, [0, 0], True)
                ok_button.clicked.connect(lambda: self.selected(win, groupings, lbl_box.grp_box.findChildren(QCheckBox)))
                win.layout().addWidget(ok_button, 3, 0)
        # size window to fit all elements
        minsize = win.minimumSizeHint()
        minsize.setHeight(win.minimumSizeHint().height() + 20)
        minsize.setWidth(win.minimumSizeHint().width() + 100)
        win.setFixedSize(minsize)
        win.show()
        win.exec()

    # return final selected groups/results
    def selected(self, win, groupings, grp_box, raw=False, axes=False, user_path=False):
        if isinstance(grp_box, str):
            #verify data plot columns
            if self.plotcols.toPlainText() in ["No Selected Columns",""] or len(self.plotcols.toPlainText().rsplit("\n"))<2:
                errorWindow("Filter Feature File Error", "Current Plot Data Selection must have at least two column names")
                return None
            else:
                #verify path
                if user_path.text() != 'Add Path':
                    self.imgpath=user_path.text().replace('\n', '')
                else:
                    self.imgpath=""
                #plot raw data verify columns
                if raw==True:
                    ax=[axis.currentText() for axis in axes]
                    if ax.count("None")>1:
                        errorWindow("Plot Raw Data", "At least two axes must be value other than None")
                        return None
                    elif len(np.unique(ax))<3:
                        errorWindow("Plot Raw Data", "Each axes must have a unique column name")
                        return None
                else:
                    groupings.extend(grp_box.rsplit("\n"))
                    [box.addItems(['None']) for box in axes]
        else:
            for checkbox in grp_box:
                # print('%s: %s' % (checkbox.text(), checkbox.isChecked()))
                if checkbox.isChecked():
                    groupings.append(checkbox.text())
        self.x_press = False
        win.close()

    def select_column(self, btn_names, title, win, row, column, txt):
        def path_find(button):
            folder= str(QFileDialog.getExistingDirectory(None, 'Select the Folder Directory for your Images'))
            if folder:
                #textwrap button text
                if len(folder)>50:
                    folder='\n'.join(folder[i+49*i:i+50*(i+1)] for i in range(ceil(len(folder)/50)))
                button.setText(folder)
            elif self.chcols.toPlainText() not in ['No Selected Columns', ""]:
                pass
            else:
                button.setText('Add Path')
        col_box = QVBoxLayout()
        filter_btn = QPushButton(btn_names[0])
        select_title = QLabel(title)
        col_txt = QTextEdit()
        col_txt.setText(txt)
        col_txt.setStyleSheet("background-color: white")
        col_txt.setReadOnly(True)
        col_txt.setAlignment(Qt.AlignTop)
        col_txt.setMinimumHeight(350)
        col_box.addWidget(select_title)
        col_box.addWidget(filter_btn)
        col_box.addWidget(col_txt)

        col_box.addStretch(1)
        win.layout().addLayout(col_box, row, column)
        if len(btn_names)>1:
           path_add=QPushButton(btn_names[1])
           path_add.clicked.connect(lambda: path_find(path_add))
           win.layout().addWidget(path_add)
           return(filter_btn, col_txt, path_add)
        return (filter_btn, col_txt)

    def filtered_col(self, lbl, win_title, col_title, col_text, dropdown=False, raw_check=False, data=False, user_path=False):
        print(user_path)
        if isinstance(user_path, str):
            print(np.shape(data.values))
            print(data.values[0])
            '''
            print(data.values[0][0].rsplit(","))
            print(data.values[:1])
            print(data.values[:1][0][0])
            print(data.values[:1][0][0].rsplit(","))
            print(sys.platform)
            print(type(sys.platform))
            if 'linux' in str(sys.platform):
                user_path=user_path.replace('\\', '/')
                print("linux")
            elif 'win' in str(sys.platform):
                user_path=user_path.replace('/', '\\')
                print("windows")
            
            if path.find("\\")>-1:
                path=path.rsplit('\\')
            elif path.find("/")>-1:
                path=path.rsplit('/')
            '''
            #print([os.path.join((path, col) for col in data.values[:1])])
            '''
            vals=data.values[0]
            cols=list(data.columns)
            print(vals)
            print(np.shape(data.values)[1])
            if np.shape(data.values)[1]==1:
                vals=vals[0].rsplit(",")
                cols=cols[0].rsplit(",")

            for col in vals:
                print(col, user_path)
                print(os.path.join(user_path, str(col)))
                print(os.path.exists(os.path.join(user_path, str(col))))
                #print(os.path.sep.join(path, str(col)))
                #print(os.path.exists(os.path.sep.join(path, str(col))))
            '''
            #try:
            bool_cols = list(map(lambda col: os.path.exists(os.path.join(user_path, str(col)).replace('\\', '/')), data.values[0]))

            #bool_cols = list(map(lambda col: os.path.exists(os.path.join(user_path, str(col))), vals))
            #bool_cols=list(map(lambda col: os.path.exists(os.path.join(user_path, col)), data.values[0][0].rsplit(",")))
            #bool_cols=[os.path.exists(os.path.join(user_path, col)) for col in data.values[0][0].rsplit(",")]
            res = list(compress(range(len(bool_cols)), bool_cols))
            print(res)
            print(data)
            #cols=list(data.columns)[0].rsplit(",")
            #print(cols)
            print("here")
            #print(list(map(lambda ind: cols[ind] ,res)))
            #lbl=list(map(lambda ind: cols[ind] ,res))
            lbl = list(map(lambda ind: list(data.columns)[ind], res))
            print(lbl)
                #data = data.apply(lambda paths: [val for val in paths.values[0].rsplit(",")])
                #check if path exist if concatenate path with first row of file values
                #data = data.apply(lambda col: [os.path.exists(os.path.join(user_path, val)) for val in col.values[0].rsplit(",")], axis=1)  # os.path.exists(str(path)))
                #data= data.rename(index = lambda x: list(data.columns))
                #data.index=list(data.columns)
                #data=data.transpose()
                #print("ere")
                #print(data.columns)
                #print(data)
                #data.set_index(pd.Index(data.columns), inplace=True)
                #print(data.set_index(data.columns, inplace=True))
                #print(data)
                #data.set_index(data.columns, inplace = True)
                #result_df = data.loc[data['result'] == True]
                #print(data.iloc[:,0])
                #print(data.columns)
                #lbl = data.apply(lambda paths: os.path.exists(os.path.join((user_path,paths.values[0]))))#os.path.exists(str(path)))
                #print(list(data.idxmax(axis=1)))
                #lbl=list(data.index[data==True])
                #print(lbl)
                #print(result_df)
        winf = filterWindow(lbl, win_title, col_title, col_text)
        col_text.setText(winf.prevcols)
            #except:
            #    errorWindow("ImageFileName", "No valid paths found from first row of data. Check if the Add Path Button displays the correct path to image folder.")

        if not dropdown == False and len (np.where(np.in1d(col_text.toPlainText().rsplit('\n'), ['No Selected Columns', '']))[0])==0 and raw_check:
            for box in dropdown:
                box.clear()
                box.addItems(['None'] + winf.prevcols.split("\n"))

        # col_text.setWordWrap(True)
        # col_text=winf.prevcols
        # print(self.colselect)
        # col_text.setText(",".join(col_text))


# select columns window
class filterWindow(object):
    def __init__(self, columns, win_title, col_title, prevcols):
        # main layout
        win = QDialog()
        win.setWindowTitle(win_title)
        title = QLabel(col_title)
        title.setFont(QFont('Arial', 25))
        title.setAlignment(Qt.AlignCenter)
        win.setLayout(QVBoxLayout())
        content_layout = QHBoxLayout()
        # win.layout().addWidget(title)
        # label button layout
        box_layout = QVBoxLayout()
        button_box = QGroupBox()
        btn_layout = QVBoxLayout()
        btn_layout.addWidget(title)
        self.btn = []
        btn_grp = QButtonGroup()
        btn_grp.setExclusive(True)
        self.cols = list(OrderedDict.fromkeys(columns))
        self.prevcols = prevcols.toPlainText()
        # self.prevcols=prevcols.text()
        # add label buttons
        for i in range(len(self.cols)):
            self.btn.append(QPushButton(self.cols[i]))
            self.btn[i].setStyleSheet('background-color: rgb' + str((255, 255, 255)) + ';')
            btn_layout.addWidget(self.btn[i])
            btn_grp.addButton(self.btn[i], i + 1)

        btn_layout.addStretch(1)
        button_box.setLayout(btn_layout)
        # win.layout().addWidget(button_box)
        # show selected labels
        lbl_box = QWidget()
        lbl_layout = QGridLayout()
        self.col_filt = QTextEdit("")
        self.col_filt.setReadOnly(True)
        # col_filt.setAlignment(Qt.AlignTop)
        self.col_filt.setStyleSheet("background-color: white")
        self.col_filt.setMinimumWidth(200)
        self.col_filt.setMinimumHeight(400)
        # self.col_filt.setWordWrap(True)
        # manual edit labels
        edit = checkbox('Selected Columns', ["Manually Edit Selected Columns \n Note: Column names must be separated by a new line (Hit Enter for new line)"],
                        lbl_layout, [0, 0], True, self.cols, self.col_filt)
        update = QPushButton("Update Add/Remove Columns Buttons after Manual Changes")
        clear = QPushButton("Clear Selected Columns")
        lbl_layout.addWidget(update, 1, 0)
        lbl_layout.addWidget(clear, 2, 0)
        lbl_layout.addWidget(self.col_filt, 3, 0)  # , 6, 3)
        lbl_box.setLayout(lbl_layout)
        # win.layout().addWidget(self.col_filt)
        content_layout.addWidget(lbl_box)
        content_layout.addLayout(lbl_layout)
        win.layout().addLayout(content_layout)
        # win.layout().addLayout(lbl_layout)
        # ok/cancel button layout
        confirm_layout = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_cancel = QPushButton("Cancel")
        # confirm_layout.addWidget(update)
        confirm_layout.addWidget(btn_ok)
        confirm_layout.addWidget(btn_cancel)
        # add scrollbar for labels
        scrollArea = QScrollArea()
        scrollArea.setWidget(button_box)
        scrollArea.setWidgetResizable(True)
        content_layout.addWidget(scrollArea)
        # win.layout().addWidget(scrollArea)
        win.layout().addLayout(confirm_layout)

        # button callbacks
        edit.grp_box.findChildren(QCheckBox)[0].stateChanged.connect(
            lambda: self.col_filt.setReadOnly(False) if edit.grp_box.findChildren(QCheckBox)[
                0].isChecked() else self.col_filt.setReadOnly(True))
        edit.all_button.clicked.connect(lambda: self.select_all(self.cols))
        btn_grp.buttonPressed.connect(self.selected)
        btn_ok.clicked.connect(lambda: self.update_list(self.cols, self.col_filt.toPlainText(), win, win_title, ok=True))
        #btn_ok.clicked.connect(lambda: self.confirmed_cols(self.cols, win))
        btn_cancel.clicked.connect(lambda: win.close())
        update.clicked.connect(lambda: self.update_list(self.cols, self.col_filt.toPlainText(), win, win_title))
        clear.clicked.connect(lambda: self.update_list(self.cols, "", win, win_title, ok=False, erase=True))
        # window size
        minsize = win.minimumSizeHint()
        minsize.setHeight(win.minimumSizeHint().height() + 100)
        minsize.setWidth(win.minimumSizeHint().width() + 500)
        win.setFixedSize(minsize)
        print(self.prevcols, "it")
        if len(self.prevcols) > 0 and self.prevcols != 'No Selected Columns':
            # if len(prevcols.text())>0 and prevcols.text() != 'No Selected Columns':
            # sorter = np.argsort(columns)
            # sorter=sorter[np.searchsorted(columns, self.prevcols.rsplit('\\'), sorter=sorter)]
            # sorter=sorter[np.searchsorted(columns, prevcols.text().rsplit('\\'), sorter=sorter)]
            sorter = np.where(np.in1d(self.cols, self.prevcols.rsplit('\n')))[0]
            print(sorter)
            for btn_ind in sorter:
                self.btn[btn_ind].setStyleSheet('background-color: rgb' + str((0, 255, 0)) + ';')
            prevvals=np.array(self.cols)[sorter]
            prevvals="\n".join(prevvals)
            # self.col_filt.setText(prevvals)
            self.col_filt.setText(self.prevcols+"\n")
        win.show()
        win.exec()
    def select_all(self, col):
        print(col)
        self.col_filt.setText('\n'.join(col))
        for btn_ind in range(len(col)):
            self.btn[btn_ind].setStyleSheet('background-color: rgb' + str((0, 255, 0)) + ';')

    def selected(self, button):
        print(self.col_filt.toPlainText())
        print(button.text() in self.col_filt.toPlainText())
        print(button.text(), self.cols)
        btn_num = np.argwhere(np.array(self.cols) == button.text())[0][0]
        print(btn_num)
        print(button.text())
        print(np.array(self.col_filt.toPlainText().rsplit('\n')))
        # if clicked button text not exist in selected columns
        if len(np.argwhere(np.array(self.col_filt.toPlainText().rsplit('\n')) == button.text())) == 0:
            self.col_filt.setText(self.col_filt.toPlainText() + button.text() + "\n")
            self.btn[btn_num].setStyleSheet('background-color: rgb' + str((0, 255, 0)) + ';')
        # unselect column
        else:
            txt = self.col_filt.toPlainText().rsplit('\n')
            print(txt)
            txt.remove(self.cols[btn_num])
            self.col_filt.setText("\n".join(txt))# if self.col_filt.toPlainText()[-1] == "\n" else "\n".join(txt) + "\n")
            self.btn[btn_num].setStyleSheet('background-color: rgb' + str((255, 255, 255)) + ';')
        '''
        if not (button.text() + "\\" in self.col_filt.toPlainText().rsplit()):
            self.col_filt.setText(self.col_filt.toPlainText() + button.text() + "\\")
            # button green color selected
            self.btn[btn_num].setStyleSheet('background-color: rgb' + str((255, 255, 255)) + ';')
            # remove from label
        else:
            self.col_filt.setText(self.col_filt.toPlainText().replace(button.text() + "\\", ""))
            # button white color unselected
            self.btn[btn_num].setStyleSheet('background-color: rgb' + str((0, 255, 0)) + ';')

        for btns in range(len(self.btn)):
            if self.btn[btns].text()==button.text():
                btn_num=btns
                #add if not in label
                if not (button.text()+"\\" in self.col_filt.toPlainText()):
                    self.col_filt.setText(self.col_filt.toPlainText() + button.text() +"\\")
                    #button green color selected
                    self.btn[btn_num].setStyleSheet('background-color: rgb' + str((255, 255, 255)) + ';')
                #remove from label
                else:
                    self.col_filt.setText(self.col_filt.toPlainText().replace(button.text()+"\\", ""))
                    #button white color unselected
                    self.btn[btn_num].setStyleSheet('background-color: rgb' +str((0,255,0)) +';')

                break
        #if self.btn[btn_num].palette().button().color().name()=='#ffffff':

        #else:
        '''

    def update_list(self, columns, cur_txt, win, win_title, ok=False, erase=False):
        '''
        sorter = np.argsort(columns)
        print(sorter)
        sorter = sorter[np.searchsorted(columns, cur_txt.rsplit('\\')[:-1], sorter=sorter)]
        print(columns)
        print(cur_txt.rsplit('\\')[:-1])
        print(np.searchsorted(columns, cur_txt.rsplit('\\')[:-1], sorter=sorter))
        print(sorter)
        '''
        #list(map(str.strip, L))
        #disp_txt = list(set(cur_txt.rsplit('\n')[:-1])) #test!!
        print(list(map(str.strip, cur_txt.rsplit('\n'))))
        #print(list(map(str.strip, cur_txt.rsplit('\n'))).remove(''))
        disp_txt = list(OrderedDict.fromkeys((list(map(str.strip, cur_txt.rsplit('\n'))))))
        #disp_txt=np.unique(list(map(str.strip, cur_txt.rsplit('\n'))).remove(''))
        print(disp_txt)
        sorter = np.where(np.in1d(columns, disp_txt))[0]
        print(columns)
        print(np.array(columns)[sorter], list(filter(None, disp_txt)))
        if not np.array_equal(sorted(np.array(columns)[sorter]), sorted(list(filter(None, disp_txt)))) and erase==False:
            errorWindow("Selected Columns Error", "These Selected Columns are invalid: {}".format(
                np.array(disp_txt)[np.where(~np.in1d(disp_txt, np.array(columns)[sorter]))]))
        # sorter=sorter[np.searchsorted(columns, prevcols.text().rsplit('\\'), sorter=sorter)]
        else:
            txt=list(filter(None, disp_txt))
            if ok:
                #if len(txt)>0:
                self.prevcols = "\n".join(txt)  # self.col_filt.toPlainText()[:-1]
                win.close()
                #else:
                #    errorWindow("Selected Columns Error", "No Columns were selected")
            else:
                for btn_ind in range(len(columns)):
                    if btn_ind in sorter:
                        self.btn[btn_ind].setStyleSheet('background-color: rgb' + str((0, 255, 0)) + ';')
                    else:
                        self.btn[btn_ind].setStyleSheet('background-color: rgb' + str((255, 255, 255)) + ';')
                self.col_filt.setText("\n".join(txt))
    '''
    def confirmed_cols(self, columns, win):
        disp_txt=list(OrderedDict.fromkeys((list(map(str.strip, self.col_filt.toPlainText().rsplit('\n'))))))
        #disp_txt = list(set(self.col_filt.toPlainText().rsplit('\n')[:-1]))
        sorter = np.where(np.in1d(columns, disp_txt))[0]
        if not np.array_equal(sorted(np.array(columns)[sorter]), sorted(list(filter(None, disp_txt)))):
            errorWindow("Selected Columns Error", "These Selected Columns are invalid: {}".format(
                np.array(disp_txt)[np.where(~np.in1d(disp_txt, np.array(columns)[sorter]))]))
        else:
            # self.prevcols=self.col_filt.toPlainText()[:-1].rsplit('\\')
            self.prevcols = "\n".join(disp_txt)#self.col_filt.toPlainText()[:-1]
            win.close()
    '''

class errorWindow(object):
    def __init__(self, win_title, text):
        alert = QMessageBox()
        alert.setWindowTitle(win_title)
        alert.setText(text)
        alert.setIcon(QMessageBox.Critical)
        alert.show()
        alert.setWindowFlags(alert.windowFlags() | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        alert.exec()