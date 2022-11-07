from interface import Ui_MainWindow
from PyQt5 import QtCore as qtc, QtGui, QtWidgets as qtw
from os import path
import re
import yaml

class OrchestratorWindow(qtw.QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)


        # initial disabled inputs
        self.ui.in_bkpFile.setEnabled(False)
        self.ui.btn_browse_bkpFile.setEnabled(False)

        # connections
        self.ui.btn_save.clicked.connect(self._save)
        self.ui.btn_browse_bkpFile.clicked.connect(self.set_backup_file)
        self.ui.btn_browse_bkpRoot.clicked.connect(self.set_backup_root)
        self.ui.btn_browse_dataRoot.clicked.connect(self.set_data_root)
        for r in self.ui.start_group.children():
            if isinstance(r, qtw.QRadioButton):
                r.clicked.connect(lambda checked,ref=r: self.set_start(ref))
        self.ui.btn_l1a_browse.clicked.connect(lambda: self.set_processor_paths('l1a'))
        self.ui.btn_l1b_browse.clicked.connect(lambda: self.set_processor_paths('l1b'))
        self.ui.btn_l2fb_browse.clicked.connect(lambda: self.set_processor_paths('l2fb'))
        self.ui.btn_l2ft_browse.clicked.connect(lambda: self.set_processor_paths('l2ft'))
        self.ui.btn_l2si_browse.clicked.connect(lambda: self.set_processor_paths('l2si'))
        self.ui.btn_l2sm_browse.clicked.connect(lambda: self.set_processor_paths('l2sm'))
        self.ui.btn_pam_browse.clicked.connect(lambda: self.set_processor_paths('pam'))
        
        self._load()

    def _load(self):
        # read configs
        confFile = 'configurations.yaml'
        if not path.isfile(confFile):
            confFile = 'configurations.sample.yaml'

        with open(confFile, 'r') as f:
            self.configs = yaml.load(f, yaml.FullLoader)
        
        # start
        for r in self.ui.start_group.children():
            if isinstance(r, qtw.QRadioButton) and self.configs['start'] == r.property('data'):
                r.click()
                break
        
        # end
        for r in self.ui.end_group.children():
            if isinstance(r, qtw.QRadioButton) and self.configs['end'] == r.property('data'):
                r.click()
                break
        
        self.ui.in_dataRoot.setText(self.configs['dataRoot']) 
        self.ui.in_bkpRoot.setText(self.configs['backupRoot']) 
        self.ui.in_bkpFile.setText(self.configs['backupFile'])
        self.ui.chk_pam.setChecked(self.configs['PAM'])

        self.ui.in_l1a_wd.setText(self.configs['processors']['L1_A']['workingDirectory'])
        if 'script' in self.configs['processors']['L1_A']:
            self.ui.in_l1a_exe.setText(self.configs['processors']['L1_A']['script'])
            self.ui.chk_l1a_script.setChecked(True)
        else:
            self.ui.in_l1a_exe.setText(self.configs['processors']['L1_A']['executable'])

        self.ui.in_l1b_wd.setText(self.configs['processors']['L1_B']['workingDirectory'])
        if 'script' in self.configs['processors']['L1_B']:
            self.ui.in_l1b_exe.setText(self.configs['processors']['L1_B']['script'])
            self.ui.chk_l1b_script.setChecked(True)
        else:
            self.ui.in_l1b_exe.setText(self.configs['processors']['L1_B']['executable'])

        self.ui.in_l2fb_wd.setText(self.configs['processors']['L2_FB']['workingDirectory'])
        if 'script' in self.configs['processors']['L2_FB']:
            self.ui.in_l2fb_exe.setText(self.configs['processors']['L2_FB']['script'])
            self.ui.chk_l2fb_script.setChecked(True)
        else:
            self.ui.in_l2fb_exe.setText(self.configs['processors']['L2_FB']['executable'])

        self.ui.in_l2sm_wd.setText(self.configs['processors']['L2_SM']['workingDirectory'])
        if 'script' in self.configs['processors']['L2_SM']:
            self.ui.in_l2sm_exe.setText(self.configs['processors']['L2_SM']['script'])
            self.ui.chk_l2sm_script.setChecked(True)
        else:
            self.ui.in_l2sm_exe.setText(self.configs['processors']['L2_SM']['executable'])

        self.ui.in_l2si_wd.setText(self.configs['processors']['L2_SI']['workingDirectory'])
        if 'script' in self.configs['processors']['L2_SI']:
            self.ui.in_l2si_exe.setText(self.configs['processors']['L2_SI']['script'])
            self.ui.chk_l2si_script.setChecked(True)
        else:
            self.ui.in_l2si_exe.setText(self.configs['processors']['L2_SI']['executable'])

        self.ui.in_l2ft_wd.setText(self.configs['processors']['L2_FT']['workingDirectory'])
        if 'script' in self.configs['processors']['L2_FT']:
            self.ui.in_l2ft_exe.setText(self.configs['processors']['L2_FT']['script'])
            self.ui.chk_l2ft_script.setChecked(True)
        else:
            self.ui.in_l2ft_exe.setText(self.configs['processors']['L2_FT']['executable'])

        self.ui.in_pam_wd.setText(self.configs['processors']['PAM']['workingDirectory'])
        if 'script' in self.configs['processors']['PAM']:
            self.ui.in_pam_exe.setText(self.configs['processors']['PAM']['script'])
            self.ui.chk_pam_script.setChecked(True)
        else:
            self.ui.in_pam_exe.setText(self.configs['processors']['PAM']['executable'])

    def _save(self):
        try:
            # start
            for r in self.ui.start_group.children():
                if isinstance(r, qtw.QRadioButton) and r.isChecked():
                    self.configs['start'] = r.property('data')
                    break
            else:
                raise Exception('Missing start processor')
            
            # end
            for r in self.ui.end_group.children():
                if isinstance(r, qtw.QRadioButton) and r.isChecked():
                    self.configs['end'] = r.property('data')
                    break
            else:
                raise Exception('Missing end processor')
            
            # data root
            if self.ui.in_dataRoot.text():
                self.configs['dataRoot'] = self.ui.in_dataRoot.text() 
            else:
                raise Exception('Missing data root')

            # backup root
            if self.ui.in_dataRoot.text():
                self.configs['backupRoot'] = self.ui.in_bkpRoot.text() 
            else:
                raise Exception('Missing backup root')

            # backup file
            if self.ui.in_bkpFile.isEnabled():
                if self.ui.in_bkpFile.text():
                    fileName = path.basename(self.ui.in_bkpFile.text())
                    self.configs['backupFile'] = re.sub(re.compile('\.zip$'), '', fileName) 
                else:
                    raise Exception('Missing backup file')
            else:
                self.configs['backupFile'] = None
            

            # pam
            self.configs['PAM'] = self.ui.chk_pam.isChecked()

            # processors
            data = { 'workingDirectory' : self.ui.in_l1a_wd.text() }
            if self.ui.chk_l1a_script.isChecked():
                data['script'] = self.ui.in_l1a_exe.text()
            else:
                data['executable'] = self.ui.in_l1a_exe.text()
            self.configs['processors']['L1_A'] = data
            
            data = { 'workingDirectory' : self.ui.in_l1b_wd.text() }
            if self.ui.chk_l1b_script.isChecked():
                data['script'] = self.ui.in_l1b_exe.text()
            else:
                data['executable'] = self.ui.in_l1b_exe.text()
            self.configs['processors']['L1_B'] = data

            data = { 'workingDirectory' : self.ui.in_l2sm_wd.text() }
            if self.ui.chk_l2sm_script.isChecked():
                data['script'] = self.ui.in_l2sm_exe.text()
            else:
                data['executable'] = self.ui.in_l2sm_exe.text()
            self.configs['processors']['L2_SM'] = data

            data = { 'workingDirectory' : self.ui.in_l2si_wd.text() }
            if self.ui.chk_l2si_script.isChecked():
                data['script'] = self.ui.in_l2si_exe.text()
            else:
                data['executable'] = self.ui.in_l2si_exe.text()
            self.configs['processors']['L2_SI'] = data

            data = { 'workingDirectory' : self.ui.in_l2ft_wd.text() }
            if self.ui.chk_l2ft_script.isChecked():
                data['script'] = self.ui.in_l2ft_exe.text()
            else:
                data['executable'] = self.ui.in_l2ft_exe.text()
            self.configs['processors']['L2_FT'] = data

            data = { 'workingDirectory' : self.ui.in_l2fb_wd.text() }
            if self.ui.chk_l2fb_script.isChecked():
                data['script'] = self.ui.in_l2fb_exe.text()
            else:
                data['executable'] = self.ui.in_l2fb_exe.text()
            self.configs['processors']['L2_FB'] = data

            data = { 'workingDirectory' : self.ui.in_pam_wd.text() }
            if self.ui.chk_pam_script.isChecked():
                data['script'] = self.ui.in_pam_exe.text()
            else:
                data['executable'] = self.ui.in_pam_exe.text()
            self.configs['processors']['PAM'] = data

            # write configs
            with open('configurations.yaml', 'w') as f:
                yaml.dump(self.configs, f)

            self.close()
        except Exception as e:
            error_dialog = qtw.QErrorMessage(self)
            error_dialog.showMessage(str(e))


    def set_start(self, ref):
        # disable all end processor, then enable only possible ones
        for r in self.ui.end_group.children():
            if isinstance(r, qtw.QRadioButton):
                r.setDisabled(False)
        # enable backup file input only when L1A is not selected 
        self.ui.in_bkpFile.setEnabled(True)
        self.ui.btn_browse_bkpFile.setEnabled(True)
        if ref == self.ui.s_l1a:
            self.ui.e_l1a.click()
            self.ui.btn_browse_bkpFile.setEnabled(False)
            self.ui.in_bkpFile.setEnabled(False)
        elif ref == self.ui.s_l1b:
            self.ui.e_l1a.setDisabled(True)
            self.ui.e_l1b.click()
        elif ref == self.ui.s_l2fb:
            self.ui.e_l1a.setDisabled(True)
            self.ui.e_l1b.setDisabled(True)
            self.ui.e_l2ft.setDisabled(True)
            self.ui.e_l2si.setDisabled(True)
            self.ui.e_l2sm.setDisabled(True)
            self.ui.e_l2fb.click()
        elif ref == self.ui.s_l2ft:
            self.ui.e_l1a.setDisabled(True)
            self.ui.e_l1b.setDisabled(True)
            self.ui.e_l2fb.setDisabled(True)
            self.ui.e_l2si.setDisabled(True)
            self.ui.e_l2sm.setDisabled(True)
            self.ui.e_l2ft.click()
        elif ref ==self.ui.s_l2si:
            self.ui.e_l1a.setDisabled(True)
            self.ui.e_l1b.setDisabled(True)
            self.ui.e_l2ft.setDisabled(True)
            self.ui.e_l2fb.setDisabled(True)
            self.ui.e_l2sm.setDisabled(True)
            self.ui.e_l2si.click()
        elif ref == self.ui.s_l2sm:
            self.ui.e_l1a.setDisabled(True)
            self.ui.e_l1b.setDisabled(True)
            self.ui.e_l2ft.setDisabled(True)
            self.ui.e_l2si.setDisabled(True)
            self.ui.e_l2fb.setDisabled(True)
            self.ui.e_l2sm.click()
        else:
            raise Exception('Something went wrong...')


    def set_data_root(self):
        directory = qtw.QFileDialog.getExistingDirectory(self, "Select Data Root Directory")
        self.ui.in_dataRoot.setText(str(directory))

    def set_backup_root(self):
        directory = qtw.QFileDialog.getExistingDirectory(self, "Select Backup Root Directory")
        self.ui.in_bkpRoot.setText(str(directory))

    def set_backup_file(self):
        fileName, _ = qtw.QFileDialog.getOpenFileName(self, 'Select Backup File', qtc.QDir.rootPath() , '*.zip')
        self.ui.in_bkpFile.setText(str(fileName))

    def set_processor_paths(self, processor):
        try:
            elements = self.ui.tabWidget.currentWidget().children()
            wd_in = next(x for x in elements if f'{processor}_wd' in x.objectName())
            exe_in = next(x for x in elements if f'{processor}_exe' in x.objectName())
            is_script = next(x for x in elements if f'{processor}_script' in x.objectName())
            ext = '*.py' if is_script.isChecked() else '*.exe'
            fileName, _ = qtw.QFileDialog.getOpenFileName(self, f'Select {processor} Executable', qtc.QDir.rootPath() , ext)
            wd_in.setText(path.dirname(fileName))
            exe_in.setText(path.join('.',path.relpath(fileName, start = path.dirname(fileName))))
        except:
            pass


if __name__ == '__main__':
    app = qtw.QApplication([])
    widget = OrchestratorWindow()
    widget.show()
    app.exec_()