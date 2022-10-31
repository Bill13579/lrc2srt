import sys
import io
import json
import os
from PyQt4 import QtGui, QtCore

class Window(QtGui.QMainWindow):

    def __init__(self):
        settings_file = open('core/set.json', 'r')
        self.settings = json.load(settings_file)
        settings_file.close()

        self.openedFiles = []

        set_defaultDirectory = self.settings['defaultDirectory']
        set_finishNotification = self.settings['finishNotifications']

        super(Window, self).__init__()
        self.move(100, 50)
        self.setFixedSize(800, 600)
        self.setWindowTitle("Lrc2Srt")
        self.setWindowIcon(QtGui.QIcon('res/onlogo.jpg'))

        self.things()

    def things(self):
        btn = QtGui.QPushButton("Quit", self)
        btn.clicked.connect(self.close_application)
        btn.resize(170, 50)
        btn.move(299, 510)

        ''' Start Drawing Settings '''
        settings_label_font = QtGui.QFont("Helvetica", 18)
        settings_label_font.setBold(True)
        settings_label = QtGui.QLabel('Settings: ', self)
        settings_label.move(20, 80)
        settings_label.setFont(settings_label_font)

        deD_font = QtGui.QFont("Helvetica", 9)
        deD_font.setBold(True)
        deD = QtGui.QLabel('Default Directory: ', self)
        deD.move(20, 115)
        deD.setFont(deD_font)

        self.deDIn = QtGui.QTextEdit(self)
        self.deDIn.setGeometry(19, 140, 205, 30)
        self.deDIn.setText(self.settings['defaultDirectory'])
        self.deDIn.setReadOnly(True)
        self.deDInSelect = QtGui.QPushButton("...", self)
        self.deDInSelect.clicked.connect(self.select_dl)
        self.deDInSelect.resize(30, 30)
        self.deDInSelect.move(225, 140)

        self.fiNotification = QtGui.QCheckBox('', self)
        self.fiNotification.stateChanged.connect(self.notifyMe)
        if self.settings['finishNotifications'] == 1:
            self.fiNotification.setCheckState(QtCore.Qt.Checked)
        else:
            self.fiNotification.setCheckState(QtCore.Qt.Unchecked)
        self.fiNotification.move(19, 215)

        self.fiNotificationLF = QtGui.QFont("Helvetica", 10)
        self.fiNotificationLF.setBold(False)
        self.fiNotificationL = QtGui.QLabel('Notification', self)
        self.fiNotificationL.move(40, 215)
        self.fiNotificationL.setFont(self.fiNotificationLF)

        self.timeInterval = QtGui.QLineEdit(self)
        self.timeInterval.setText(str(self.settings['srtSet'][0]['timeInterval']))
        self.timeInterval.setValidator(QtGui.QIntValidator())
        self.timeInterval.setMaxLength(3)
        self.timeInterval.setFont(QtGui.QFont("Arial", 15))
        self.timeInterval.setGeometry(125, 180, 89, 30)
        self.timeInterval.textEdited.connect(self.saveTimeInterval)

        self.timeIntervalText = QtGui.QLabel('Time Interval   : \n*In milliseconds', self)
        self.timeIntervalText.move(19, 180)
        self.timeIntervalTextFont = QtGui.QFont("Helvetica", 10)
        self.timeIntervalTextFont.setBold(True)
        self.timeIntervalText.setFont(self.timeIntervalTextFont)
        ''' End Drawing Settings '''

        # Status
        convertStatusF = QtGui.QFont("Helvetica", 18)
        convertStatusF.setBold(True)
        self.convertStatus = QtGui.QLabel('Status: ', self)
        self.convertStatus.setFont(convertStatusF)
        self.convertStatus.move(20, 290)

        statusTextFont = QtGui.QFont("Helvetica", 17)
        statusTextFont.setBold(True)
        statusTextFont.setPixelSize(20)
        self.statusText = QtGui.QLabel('Waiting...', self)
        self.statusText.setFont(statusTextFont)
        self.statusText.move(60, 330)

        self.statusText2 = QtGui.QLabel('Total: '+str(len(self.openedFiles)), self)
        self.statusText2.setFont(statusTextFont)
        self.statusText2.move(60, 370)

        ### Start Tool Bar ###
        # Open action
        openAction = QtGui.QAction(QtGui.QIcon('res/plus.png'), 'Open File', self)
        openAction.triggered.connect(self.open_file)
        openAction.setStatusTip("Open a file to convert")

        # Close action
        closeAction = QtGui.QAction(QtGui.QIcon('res/minus.png'), 'Close File', self)
        closeAction.triggered.connect(self.close_file)
        closeAction.setStatusTip("Delete a file from the convertion list")

        # Help action
        helpAction = QtGui.QAction(QtGui.QIcon('res/about.png'), 'About lrc2srt', self)
        helpAction.triggered.connect(self.show_about)
        helpAction.setStatusTip("About lrc2srt")

        # Exit Action
        exitAction = QtGui.QAction(QtGui.QIcon('res/exit.png'), 'Exit lrc2srt', self)
        exitAction.triggered.connect(self.close_application)
        exitAction.setStatusTip("Exit the application")

        # Clear List Action
        clearListAction = QtGui.QAction(QtGui.QIcon('res/clear_all.png'), 'Clear opened files', self)
        clearListAction.triggered.connect(self.clear_all_from_list)
        clearListAction.setStatusTip("Clear all items on the opened files list")

        # Add Toolbar
        self.toolBar = self.addToolBar("lrc2srt")
        self.toolBar.setMovable(False)
        self.toolBar.addAction(openAction)
        self.toolBar.addAction(closeAction)
        self.toolBar.addAction(clearListAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(helpAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(exitAction)
        ### End Tool Bar ###

        self.statusBar()


        self.openedFilesT = QtGui.QLabel("Opened Files", self)
        self.openedFilesT.move(300, 50)

        self.openedFilesLF = QtGui.QFont("Helvetica", 16)
        self.openedFilesLF.setBold(True)
        self.openedFilesL = QtGui.QListWidget(self)
        self.openedFilesL.setGeometry(300, 80, 450, 420)
        self.openedFilesL.setFont(self.openedFilesLF)

        startButton = QtGui.QPushButton("Start =>", self)
        startButton.clicked.connect(self.start)
        startButton.setStatusTip("Start converting")
        startButton.resize(270, 50)
        startButton.move(481, 510)

        self.show()

    def saveTimeInterval(self):
        currentChangedTI = self.timeInterval.text()
        self.settings['srtSet'][0]['timeInterval'] = int(currentChangedTI)
        with open('core/set.json', 'w') as opened:
            opened.write(json.dumps(self.settings))
        self.timeInterval.setText(str(self.settings['srtSet'][0]['timeInterval']))

    def subtractFromTimeMili_srtFormat(self, timeStr, subNum):
        ''' Make it a number '''
        tmp1 = timeStr.split(':')
        firstPart = tmp1[0]
        secondPart = tmp1[1]
        tmp2 = tmp1[2]
        tmp3 = tmp2.split(',')
        thirdPart = tmp3[0]
        forthPart = tmp3[1]
        AllInOne_timeStr = int(firstPart+secondPart+thirdPart+forthPart)

        ''' Add it (timeStr's four parts) to list for testing '''
        timeStrInArray = [firstPart, secondPart, thirdPart, forthPart]

        ''' Main Subtract Part '''
        # Turn subNum into a number
        tmp1 = subNum.split(':')
        firstPart = tmp1[0]
        secondPart = tmp1[1]
        tmp2 = tmp1[2]
        tmp3 = tmp2.split(',')
        thirdPart = tmp3[0]
        forthPart = tmp3[1]
        AllInOne_subNum = int(firstPart + secondPart + thirdPart + forthPart)

        ''' Add it (subNum's four parts) to list for testing '''
        subNumInArray = [firstPart, secondPart, thirdPart, forthPart]

        # Subtract
        # Fix before subtract
        AllInOne_subNum_Str = str(AllInOne_subNum)
        forthPart = AllInOne_subNum_Str[-3:]
        AllInOne_timeStr_Str = str(AllInOne_timeStr)
        forthPart = AllInOne_timeStr_Str[-3:]

        if int(subNumInArray[3]) < int(timeStrInArray[3]) or int(subNumInArray[3]) == int(timeStrInArray[3]):
            Subtracted = AllInOne_timeStr - AllInOne_subNum
        else:
            ifUsedRest = int(timeStrInArray[3]) + ( int(timeStrInArray[2]) * 1000 ) + ( int(timeStrInArray[1]) * 60000 ) + ( int(timeStrInArray[0]) * 3600000 )
            if int(subNumInArray[3]) < int(ifUsedRest) or int(subNumInArray[3]) == int(ifUsedRest):
                Subtracted = int(ifUsedRest) - int(subNumInArray[3])
                Subtracted = '00:00:00,' + str(Subtracted)
                tmp = self.fixTime_srt_list([Subtracted])
                Subtracted = tmp[0]

                tmp = Subtracted.split(':')
                first = tmp[0]
                second = tmp[1]
                tmp = tmp[2].split(',')
                third = tmp[0]
                forth = tmp[1]

                Subtracted = int(first + second + third + forth)
            else:
                raise MinimalSubtractionError
        if len(str(Subtracted)) < 9:
            lengthOfSubtracted = len(str(Subtracted))
            Subtracted = str(Subtracted)
            toAdd = 9 - lengthOfSubtracted
            for i in range(0, toAdd):
                Subtracted = '0' + Subtracted
        # Fix Subtracted
        SubtractedLen = len(str(Subtracted))
        Subtracted = str(Subtracted)
        forthPart = Subtracted[-3:]
        thirdPart = Subtracted[-5:-3]
        secondPart = Subtracted[-7:-5]
        firstPart = Subtracted[:-7]

        AllInOne_Result = firstPart + ':' + secondPart + ':' + thirdPart + ',' + forthPart
        # Fix Time
        toReturnList = self.fixTime_srt_list([AllInOne_Result])
        toReturn = toReturnList[0]
        return toReturn

    def addToTime_srtFormat(self, timeStr, addNum):
        ''' Make it a number '''
        tmp1 = timeStr.split(':')
        firstPart = tmp1[0]
        secondPart = tmp1[1]
        tmp2 = tmp1[2]
        tmp3 = tmp2.split(',')
        thirdPart = tmp3[0]
        forthPart = tmp3[1]
        AllInOne_timeStr = int(firstPart+secondPart+thirdPart+forthPart)

        ''' Main Subtract Part '''
        # Turn subNum into a number
        tmp1 = addNum.split(':')
        firstPart = tmp1[0]
        secondPart = tmp1[1]
        tmp2 = tmp1[2]
        tmp3 = tmp2.split(',')
        thirdPart = tmp3[0]
        forthPart = tmp3[1]
        AllInOne_addNum = int(firstPart + secondPart + thirdPart + forthPart)
        # Subtract
        Added = AllInOne_timeStr + AllInOne_addNum
        if len(str(Added)) < 9:
            lengthOfAdded = len(str(Added))
            Added = str(Added)
            toAdd = 9 - lengthOfAdded
            for i in range(0, toAdd):
                Added = '0' + Added
        # Fix Added
        AddedLength = len(str(Added))
        Added = str(Added)
        forthPart = Added[-3:]
        thirdPart = Added[-5:-3]
        secondPart = Added[-7:-5]
        firstPart = Added[:-7]

        AllInOne_Result = firstPart + ':' + secondPart + ':' + thirdPart + ',' + forthPart
        # Fix Time
        toReturnList = self.fixTime_srt_list([AllInOne_Result])
        toReturn = toReturnList[0]
        return toReturn

    def subtract(self, number, howManyToSubtract):
        toReturn = number - howManyToSubtract
        return toReturn

    def addition(self, number, howManyToAdd):
        toReturn = number + howManyToAdd
        return toReturn

    def fixTime_srt_list(self, list):
        ft = list[:]
        fixedTimeList = []
        for i in range(0, len(ft)):
            item = ft[i]
            
            tmp = item.split(':')
            firstPart = tmp[0]
            secondPart = tmp[1]
            thirdPartSet = tmp[2]

            tmp = thirdPartSet.split(',')
            thirdPart = tmp[0]
            forthPart = tmp[1]

            firstPart = int(firstPart)
            secondPart = int(secondPart)
            thirdPart = int(thirdPart)
            try:
                forthPart = int(forthPart)
            except UnicodeEncodeError:
                forthPart = ''.join(e for e in forthPart if e.isalnum())
                forthPart = int(forthPart)

            ''' Start checking conditions '''
            # Forth Part to Third Part
            if int(forthPart) > 999:
                howMany1000InForthPart = int(forthPart) // 1000
                howMany1000InForthPart_Multiplied = 1000 * howMany1000InForthPart
                hm1000ifp_m = howMany1000InForthPart_Multiplied
                differ = int(forthPart) - hm1000ifp_m
                forthPart = differ
                thirdPart += howMany1000InForthPart

            # Third Part to Second Part
            if thirdPart > 59:
                howMany60InThirdPart = thirdPart // 60
                howMany60InThirdPart_Multiplied = 60 * howMany60InThirdPart
                hm60itp_m = howMany60InThirdPart_Multiplied
                differ = thirdPart - hm60itp_m
                thirdPart = differ
                secondPart += howMany60InThirdPart

            # Second Part to First Part
            if secondPart > 59:
                howMany60InSecondPart = secondPart // 60
                howMany60InSecondPart_Multiplied = 60 * howMany60InSecondPart
                hm60isp_m = howMany60InSecondPart_Multiplied
                differ = secondPart - hm60isp_m
                secondPart = differ
                firstPart += howMany60InSecondPart
            ''' Finish checking conditions '''

            ''' Start checking digit '''
            # Check if forth part is smaller than 3
            if len(str(forthPart)) < 3:
                lengthOfForthPart = len(str(forthPart))
                toAdd = 3 - lengthOfForthPart
                forthPartStr = str(forthPart)
                for i in range(0, toAdd):
                    forthPartStr = '0' + forthPartStr
                forthPart = forthPartStr
            # Check if third part is smaller than 2
            if len(str(thirdPart)) < 2:
                lengthOfThirdPart = len(str(thirdPart))
                toAdd = 2 - lengthOfThirdPart
                thirdPartStr = str(thirdPart)
                for i in range(0, toAdd):
                    thirdPartStr = '0' + thirdPartStr
                thirdPart = thirdPartStr
            # Check if second part is smaller than 2
            if len(str(secondPart)) < 2:
                lengthOfSecondPart = len(str(secondPart))
                toAdd = 2 - lengthOfSecondPart
                secondPartStr = str(secondPart)
                for i in range(0, toAdd):
                    secondPartStr = '0' + secondPartStr
                secondPart = secondPartStr
            # Check if first part is 1
            if len(str(firstPart)) == 1:
                firstPartStr = str(firstPart)
                firstPartStr = '0' + firstPartStr
                firstPart = firstPartStr

            toReturn = str(firstPart) + ':' + str(secondPart) + ':' + str(thirdPart) + ',' + str(forthPart)
            fixedTimeList.append(toReturn)

            ''' Finish checking digit '''
        return fixedTimeList


    def notifyMe(self, state):
        setFile = open('core/set.json', 'w')
        if state == QtCore.Qt.Checked:
            self.settings['finishNotifications'] = 1
            setFile.write(json.dumps(self.settings))
        else:
            self.settings['finishNotifications'] = 0
            setFile.write(json.dumps(self.settings))
        setFile.close()


    def select_dl(self):
        Pick = QtGui.QFileDialog.getExistingDirectory(self, 'Select Default Folder', '')
        if Pick:
            Pick = unicode(Pick.toUtf8(), encoding='UTF-8')
            Pick += u'/'
            self.settings['defaultDirectory'] = Pick
            setFile = open('core/set.json', 'w')
            setFile.write(json.dumps(self.settings))
            self.deDIn.setText(Pick)
            setFile.close()


    def close_application(self):
        exitchoice = QtGui.QMessageBox.question(self, 'Close App',
                                                "Are you sure you want to quit? ",
                                                QtGui.QMessageBox.No | QtGui.QMessageBox.Yes)
        if exitchoice == QtGui.QMessageBox.Yes:
            sys.exit()
        else:
            pass

    def clear_all_from_list(self):
        del self.openedFiles[:]
        self.openedFilesL.clear()

    def open_file(self):
        PickFileNames = QtGui.QFileDialog.getOpenFileNames(self, 'Open File', '', '*.lrc')
        if PickFileNames:
            for PickFile in PickFileNames:
                PickFile = unicode(PickFile.toUtf8(), encoding='UTF-8')
                if (PickFile not in self.openedFiles):
                    self.openedFiles.append(PickFile)
                    file_real_name = os.path.basename(PickFile)
                    self.openedFilesL.addItem(file_real_name)
                else:
                    mes = QtGui.QMessageBox.information(self, 'Error', 'Selected files are already opened')
        self.statusText2.setText('Total: '+str(len(self.openedFiles)))

    def close_file(self):
        try:
            close_file_row = self.openedFilesL.currentRow()
            self.openedFilesL.takeItem(close_file_row)
            del self.openedFiles[close_file_row]
            self.statusText2.setText('Total: ' + str(len(self.openedFiles)))
        except IndexError:
            pass

    def start(self):
        if len(self.openedFiles) > 0:
            for i in range(0, len(self.openedFiles)):
                self.statusText.setText('Current: ' + str(i+1))
                inp = self.openedFiles[i]
                inp = unicode(inp)
                if self.settings['defaultDirectory']:
                    savetoFileName = os.path.basename(inp)
                    savetoFileNameFix = savetoFileName.split('.')
                    savetoFileName = savetoFileNameFix[0] + '.srt'
                    savetoFileName = self.settings['defaultDirectory'] + savetoFileName

                    timeInterval = int(self.settings['srtSet'][0]['timeInterval'])

                    self.lrc2srt(inp, savetoFileName, timeInterval)

                else:
                    QtGui.QMessageBox.information(self, 'Error', 'You have to set the default save directory before the convertion!')
            if self.settings['finishNotifications'] == 1:
                        QtGui.QMessageBox.information(self, 'Finished', 'The convertion has finished')
            self.statusText.setText('Waiting...')

    def show_about(self):
        message = 'Lrc2Srt\n\nVersion: v4.2'
        mainMessage = QtGui.QMessageBox.information(self, 'About', message)

    def lrc2srt(self, inpath, outpath, timeInterval):
        # Open required files
        infile = io.open(file=inpath, mode='r', encoding="UTF-8")
        infileLines = infile.readlines()
        infileLS = []
        threePartL = []
        timeDiffer = timeInterval
        timeDiffer = '00:00:00,' + str(timeInterval)
        timeDiffer = self.fixTime_srt_list([timeDiffer])
        timeDiffer = timeDiffer[0]
        contTimeInterval = True
        for line in infileLines:
            # Split it to two part. Start Time and Text
            twopart = line.split("]")
            twopart[0] += "]"
            try:
                infileLS.append([twopart[0], twopart[1]])
            except IndexError:
                pass
        for i in range(0, len(infileLS) + 1):

            # Get the end time
            try:
                nextSet = infileLS[i + 1]
            except IndexError:
                try:
                    nextSet = infileLS[i]
                except IndexError:
                    break
            endSub = nextSet[0]
            endSubTemp = endSub.split("]")
            endSub = endSubTemp[0]
            endSubTemp = endSub.split("[")
            endSub = endSubTemp[1]

            # Change the time to srt format (Part 2)
            AfSplit = endSub.split('.')
            AfSplitSplit = AfSplit[0].split(':')
            minutes = AfSplitSplit[0]
            seconds = AfSplitSplit[1]
            milisecond = AfSplit[1]
            endSub = "00:" + minutes + ":" + seconds + "," + milisecond + "0"
            endSubList = [endSub]
            endSubFixTime = self.fixTime_srt_list(endSubList)
            endSub = endSubFixTime[0]

            try:
                endSub = self.subtractFromTimeMili_srtFormat(endSub, timeDiffer)
            except MinimalSubtractionError:
                contTimeInterval = False

            # Get the start time
            try:
                set = infileLS[i]
            except IndexError:
                break
            startSub = set[0]
            startSubTemp = startSub.split("]")
            startSub = startSubTemp[0]
            startSubTemp = startSub.split("[")
            startSub = startSubTemp[1]

            # Change the time to srt format (Part 1)
            AfSplit = startSub.split('.')
            AfSplitSplit = AfSplit[0].split(':')
            minutes = AfSplitSplit[0]
            seconds = AfSplitSplit[1]
            milisecond = AfSplit[1]
            startSub = "00:" + minutes + ":" + seconds + "," + milisecond + "0"
            startSubFixTime = self.fixTime_srt_list([startSub])
            startSub = startSubFixTime[0]

            if contTimeInterval == False:
                startSub = self.addToTime_srtFormat(startSub, timeDiffer)

            # Put it into a set
            toPut = [startSub, endSub, infileLS[i][1]]
            threePartL.append(toPut)

        # Open output file
        outfile = io.open(file=outpath, mode='w', encoding='UTF-8')

        # Fix the last one

        lastOneFix = threePartL[len(threePartL) - 1][1]
        lastOneFixTemp = lastOneFix.split(":")
        lastOneFix = int(lastOneFixTemp[0])
        lastOneFix += 10000
        lastOneFix = str(lastOneFix)
        lastOneFix = lastOneFix + ":" + lastOneFixTemp[1] + ":" + lastOneFixTemp[2]
        threePartL[len(threePartL) - 1][1] = lastOneFix

        # Write to file
        for j in range(0, len(threePartL)):
            count = j + 1
            time = threePartL[j][0] + " --> " + threePartL[j][1]
            text = threePartL[j][2]
            space = ""

            count = str(count).decode('utf-8')
            time = str(time).decode('utf-8')
            space = space.decode('utf-8')

            count += '\n'
            time += '\n'
            text += '\n'

            outfile.write(count)
            outfile.write(time)
            outfile.write(text)
            outfile.write(space)

        # Close all files that had been opened
        infile.close()
        outfile.close()

class MinimalSubtractionError(Exception):
    pass

def application():
    app = QtGui.QApplication(sys.argv)
    GUI = Window()
    sys.exit(app.exec_())

application()
