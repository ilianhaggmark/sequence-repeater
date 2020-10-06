# -*- coding: utf-8 -*-
"""
June 2019

@author: ilian Haggmark
"""

import wx
import wx.grid as gridlib
from wx.lib.intctrl import IntCtrl

import csv

import pyautogui, time # sys
from pynput.keyboard import Key, Listener

import contextlib
with contextlib.redirect_stdout(None):  # to suppress unnecessary print out
    import pygame as pg

class MyFrame(wx.Frame):  
       
    def __init__(self):
        super().__init__(parent=None, title='Sequence Repeater 0.02',size=(350,460)) #,style= wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX)
        panel = wx.Panel(self)
        self.r = 10 # Number of Actions
        self.n = 1  # Number of Iterations
        self.j = 0 # extra number 

        vbox = wx.BoxSizer(wx.VERTICAL) 
        
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)     
        st1 = wx.StaticText(panel, label='Action steps   ')
        hbox1.Add(st1, flag=wx.RIGHT, border=8)
        self.tc1 = IntCtrl(panel,value=self.r,size=(50,-1))
        hbox1.Add(self.tc1, proportion=1)
        vbox.Add(hbox1, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10) #wx.EXPAND|
        
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)     
        st2 = wx.StaticText(panel, label='Iterations    ')
        hbox2.Add(st2, flag=wx.RIGHT, border=8)
        self.tc2 = IntCtrl(panel,value=self.n,size=(50,-1))
        hbox2.Add(self.tc2, proportion=1)
        vbox.Add(hbox2, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)  # wx.EXPAND|
        
        vbox.Add((-1, 10))
        
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)   
        btn1 = wx.Button(panel, label='Update')
        btn1.Bind(wx.EVT_BUTTON, self.on_update)
        hbox3.Add(btn1, 0, wx.ALL | wx.CENTER, 5) 
        btn4 = wx.Button(panel, label='Set Pos')
        btn4.Bind(wx.EVT_BUTTON, self.on_setPos)
        hbox3.Add(btn4, 0, wx.ALL | wx.CENTER, 5)        
        btn5 = wx.Button(panel, label='Run')
        btn5.Bind(wx.EVT_BUTTON, self.on_run)
        hbox3.Add(btn5, 0, wx.ALL | wx.EXPAND, 10) 
        vbox.Add(hbox3, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        

        
        self.myGrid = gridlib.Grid(panel)
        self.myGrid.CreateGrid(self.r, 4)
        self.myGrid.SetColLabelValue(0, "Action")
        self.myGrid.SetColLabelValue(1, "X")
        self.myGrid.SetColLabelValue(2, "Y")
        self.myGrid.SetColLabelValue(3, "Value")
        
        self.myGrid.SetDefaultColSize(55, resizeExistingCols=True)
#        self.myGrid.SetColSize(0, 60)
#        self.myGrid.SetColSize(1, 60)
#        self.myGrid.SetColSize(2, 60)
        self.myGrid.SetColSize(3, 80)
        self.myGrid.SetRowLabelSize(40)
        
        self.myGrid.ShowScrollbars(wx.SHOW_SB_NEVER,wx.SHOW_SB_DEFAULT)
        vbox.Add(self.myGrid, 0,  wx.ALL |wx.EXPAND,10)
        
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.gridEvent)
        
        panel.SetSizer(vbox) 
        
        self.statusbar = self.CreateStatusBar(2)
        #self.statusbar.SetStatusWidths([170, -1])
        self.statusbar.SetStatusText('Actions %d, Iterations %d' % (self.r,self.n))
        self.statusbar.SetStatusText('',1)
        
        
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        editMenu = wx.Menu()
        helpMenu = wx.Menu()
        
        # FILE MENU
       
        loadFile = wx.MenuItem(fileMenu, wx.ID_OPEN, '&Load File\tCtrl+O')
        self.Bind(wx.EVT_MENU, self.on_load, loadFile)
        fileMenu.Append(loadFile)
        
        saveFile = wx.MenuItem(fileMenu, wx.ID_SAVE, '&Save\tCtrl+S')
        self.Bind(wx.EVT_MENU, self.on_save, saveFile)
        fileMenu.Append(saveFile)
        
        fileMenu.AppendSeparator()
        
        quitApp = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+Q')
        self.Bind(wx.EVT_MENU, self.OnQuit, quitApp)
        fileMenu.Append(quitApp)
        
        menubar.Append(fileMenu, '&File')

        # EDIT MENU
        
        run = wx.MenuItem(editMenu, wx.ID_ANY, '&Run\tF5')
        self.Bind(wx.EVT_MENU, self.on_run, run)
        editMenu.Append(run)
        
        editMenu.AppendSeparator()
        
        cleartable = wx.MenuItem(editMenu, wx.ID_ANY, '&Clear table')
        self.Bind(wx.EVT_MENU, self.on_cleartable, cleartable)
        editMenu.Append(cleartable)

        setposition = wx.MenuItem(editMenu, wx.ID_ANY, '&Set Position')
        self.Bind(wx.EVT_MENU, self.on_setPos, setposition)
        editMenu.Append(setposition)
        
        update = wx.MenuItem(editMenu, wx.ID_ANY, '&Update')
        self.Bind(wx.EVT_MENU, self.on_update, update)
        editMenu.Append(update)
        
        menubar.Append(editMenu, '&Edit')     
        
        # HELP MENU        
        
        howtouse = wx.MenuItem(helpMenu, wx.ID_ANY, '&How to use')
        self.Bind(wx.EVT_MENU, self.on_howtouse, howtouse)
        helpMenu.Append(howtouse)
        
        about = wx.MenuItem(helpMenu, wx.ID_ANY, '&About Sequence Repeater')
        self.Bind(wx.EVT_MENU, self.on_about, about)
        helpMenu.Append(about)
        
        menubar.Append(helpMenu, '&Help')
        
        self.SetMenuBar(menubar)
        
        self.fixGrid()

        self.Show()
        super().Raise()
        
    def OnQuit(self, e):
        self.Close()
        
    def on_about(self, e):
        wx.MessageBox("Sequence Repeater 0.1.0    © 2020 Ilian Häggmark\n\n"
            "This is an application to simplify repetitions of "
           "short mouse click sequences. The code was written in Python 3.6 with wxPython, "
           "Pyautogui, Pynput, and Pygame."
           "", caption='About Sequence Repeater', style=wx.CENTRE)

    def on_howtouse(self, e):
        wx.MessageBox("How to use Sequence Repeater \n\n"
            "5 types of events can be set up in a sequence, \n\n "
           "left click, right click, sleep, intpr, and double click. \n\n"
           "All can take input in the form of a string called 'value'. "
           "left click, double click, and intpr will simply print the input "
           "at the location and sleep's value specifies the time to sleep in "
           "seconds (1 s by default). \n\n"
           "intpr can interpret a formatted string on the form f'your-string' "
           "to enable different values for each iteration 'i'. The string "
           "should typically be something like f'img2_{100*i:05}'. This gives "
           "the sequence img2_00000 img2_00100 img2_00200 etc. "
           "To get an offset one can also use f'img{20+i:04}' which gives "
           "img0020 img0021 img 0022 etc. \n\n"
           "The five events are triggered by left arrow (left click), "
           "right arrow (right click), up arrow (double click), "
           "down arrow (sleep), and ctrl (intpr). Double click on each row "
           "label to set mouse position, write in the fields or set all by "
           "pressing Set Pos", caption='About Sequence Repeater', style=wx.CENTRE)    
    
    def on_cleartable(self, e):
        for row in range(0,self.r):
            for col in range(0,4):
                self.myGrid.SetCellValue(row, col,"")
        self.statusbar.SetStatusText('Table cleared',1)
        
    def  gridEvent(self, event):
        row = event.GetRow()
        if row >= 0:
            self.on_setPos(event,True, row)
            
        
    def fixGrid(self):
        panelcolour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        self.myGrid.SetDefaultCellBackgroundColour(panelcolour)
        for row in range(0,self.r):
            for col in range(0,4):
                self.myGrid.SetCellBackgroundColour(row, col, wx.WHITE)   
    
    def on_update(self, event):
        old_r = self.myGrid.GetNumberRows()
        self.r = self.tc1.GetValue()
        self.n = self.tc2.GetValue()
        self.changeGridSize()
        self.statusbar.SetStatusText('Actions %d, Iterations %d' % (self.r,self.n))
        error = 0
        for row in range(self.r):
            action = self.myGrid.GetCellValue(row, 0)
            if action != 'click' and action != 'dclick' and action != 'intpr'\
            and action != 'sleep' and action != 'rclick' and action != '':
                error = 1
        if error == 1:
            self.statusbar.SetStatusText('Error in action input',1)        
        if error == 0 and old_r == self.r: # Nothing changed and no error
            self.statusbar.SetStatusText('',1)
        
    def changeGridSize(self):
        old_r = self.myGrid.GetNumberRows()
        if self.r > old_r:
            self.myGrid.AppendRows(self.r - old_r)
            print("appending %d row(s)" % (self.r - old_r))
            self.statusbar.SetStatusText('appending %d row(s)' % (self.r - old_r),1)
            self.myGrid.SetVirtualSize( self.myGrid.GetSize() ) 
            self.fixGrid()
        elif self.r < old_r:
            self.myGrid.DeleteRows(self.r,old_r-self.r) 	
            print("deleting %d row(s)" % (old_r-self.r))
            self.statusbar.SetStatusText('deleting %d row(s)' % (old_r-self.r),1)
            self.fixGrid()
        else:
            print('do nothing')
    def on_save(self, event):
        with wx.FileDialog(self, "Save CSV file", wildcard="CSV files (*.csv)|*.csv",
                      style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # save the current contents in the file
            pathname = fileDialog.GetPath()
            print(pathname)
            with open(pathname, 'w',   newline='') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerow(['Iterations',self.n,'Actions',self.r])
                writer.writerow(['#','X','Y','Value'])
                for row in range(self.r):
                    tempRow = []
                    for col in range(4):
                        tempRow.append(self.myGrid.GetCellValue(row, col))
                    writer.writerow(tempRow)
            writeFile.close()                    
            
    def on_load(self, event):            
        with wx.FileDialog(self, "Open CSV file", wildcard="CSV files (*.csv)|*.csv",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:
            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
    
            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            print('Opening %s' % pathname)
            with open(pathname, 'r') as readFile:
                reader = csv.reader(readFile)
                lines = list(reader)

                self.n=int(lines[0][1])
                self.r=int(lines[0][3])

                self.changeGridSize()
                
                self.tc1.SetValue(self.r)
                self.tc2.SetValue(self.n)
                
                for row in range(self.r):
                    for col in range(4):
                        self.myGrid.SetCellValue(row, col,"%s" % (lines[row+2][col]))
            self.statusbar.SetStatusText('Actions %d, Iterations %d' % (self.r,self.n))
                        
    def on_setPos(self, event, oneRow=False, k=0):                       

        class SetPosInterrupted(Exception): 
            """Set position interrupted by user"""
            pass
        
        def on_press(key):
            print(key)
            if(key == Key.left or key == Key.right or key == Key.down\
               or key == Key.up or key == Key.ctrl_r or key == Key.ctrl_l):    
                x, y = pyautogui.position()
                if key == Key.left:
                    tempRow = ['click',str(x),str(y),'']
                    for col in range(4):
                        self.myGrid.SetCellValue(self.j, col,"%s" % (tempRow[col]))
                    print('%d of %d actions set' % (self.j+1,self.r)) 
                if key == Key.right:
                    tempRow = ['rclick',str(x),str(y),'']
                    for col in range(4):
                        self.myGrid.SetCellValue(self.j, col,"%s" % (tempRow[col])) 
                    print('%d of %d actions set' % (self.j+1,self.r))
                if key == Key.down:
                    tempRow = ['sleep',str(x),str(y),1]
                    for col in range(4):
                        self.myGrid.SetCellValue(self.j, col,"%s" % (tempRow[col]))                  
                    print('%d of %d actions set' % (self.j+1,self.r))
                if key == Key.up:
                    tempRow = ['dclick',str(x),str(y),'']
                    for col in range(4):
                        self.myGrid.SetCellValue(self.j, col,"%s" % (tempRow[col]))                  
                    print('%d of %d actions set' % (self.j+1,self.r))                    
                if (key == Key.ctrl_l or key == Key.ctrl_r):
                    tempRow = ['intpr',str(x),str(y),'']
                    for col in range(4):
                        self.myGrid.SetCellValue(self.j, col,"%s" % (tempRow[col]))                  
                    print('%d of %d actions set' % (self.j+1,self.r))  
                        
                return False
            if(key == Key.esc):
                raise SetPosInterrupted
            else:
                print('Else')
        
        if oneRow == False:
            for i in range(self.r):       
                pg.init()
                pg.quit()  

                self.j = i
                try:
                    with Listener(on_press=on_press) as listener:
                        listener.join()
                        self.statusbar.SetStatusText('%d of %d actions set' % (self.j+1,self.r),1) 
                except SetPosInterrupted:
                    self.statusbar.SetStatusText('Interrupted by user',1) 
                    print('Set position interrupted by user')                    
                    break     
        else: 
            pg.init()
            pg.quit()  

            self.j = k
            try:
                with Listener(on_press=on_press) as listener:
                    listener.join()
                    self.statusbar.SetStatusText('row %d set' % (self.j+1),1) 
                    self.myGrid.DeselectRow(self.j)
            except SetPosInterrupted:
                self.statusbar.SetStatusText('Interrupted by user',1) 
                print('Set position interrupted by user')                    
                return     
            
            
        
    def on_run(self, event):   
        start = time.time()         
        for i in range(self.n):
             print('iteration: %d' % (i+1))
             for j in range(self.r): # 2 to remove first two rows
                 action = self.myGrid.GetCellValue(j,0)
                 x = self.myGrid.GetCellValue(j,1)
                 y = self.myGrid.GetCellValue(j,2)
                 value = self.myGrid.GetCellValue(j,3)
                 
                 if action == 'click':
                     pyautogui.click(x=int(x), y=int(y),button='left')
                     time.sleep(0.1)
                     if value != '':
                         pyautogui.typewrite(value, interval=0.02)
                         print('entered number')
                     else:
                         print('click')
                     
                 elif action == 'dclick':
                     pyautogui.doubleClick(x=int(x), y=int(y),button='left')
                     time.sleep(0.1)
                     if value != '':
                         pyautogui.typewrite(value, interval=0.02)
                         print('entered number')
                     else:                     
                         print('double click')
                         
                 elif action == 'rclick':
                     pyautogui.click(x=int(x), y=int(y),button='right')
                     time.sleep(0.1)
                     #if value != '':
                     #    pyautogui.typewrite(value, interval=0.02)
                     #    print('entered number')
                     #else:                     
                     print('right click')                               
                         
                 elif action == 'intpr':
                     pyautogui.click(x=int(x), y=int(y),button='left')
                     time.sleep(0.1)
                     if value != '':
                         intprstring = eval(value)
                         pyautogui.typewrite(intprstring, interval=0.02)
                         print('entered interpreted string')
                     else:                     
                         print('no string input')                         
        
                 elif action == 'sleep':
                     if value != '':
                         t = int(value)
                         print('waiting %d sec' % t)
                         time.sleep(t)
                 else:
                     print('Unknown input')
                     time.sleep(0.1)
        super().Raise() # Raises window to front after run completed
        end = time.time()                     
        self.statusbar.SetStatusText('Finished! %d s elapsed.' % (end-start),1) 
      
        
if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()
    del app
