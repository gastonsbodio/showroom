# Desarrollado para LaSociedadPost
# Author: Leandro Inocencio aka Cesio (cesio.arg@gmail.com)


from urllib import urlopen
from functools import partial
from lasp.tactic.utils import get_md5
from lasp.tactic.versioner import Versioner
from lasp.tactic.project_configs import *
from lasp.tactic.media import Path
from lasp.tactic.utils import ensure_module
from lasp.packages.pyseq.pyseq import Sequence



try:    # Nuke < 11
    globals().update(ensure_module('PySide'))
    from PySide.QtCore import *
    from PySide.QtGui import *
except: # Nuke > 11
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
	
from lasp.qt import *

import os
import re
import json
import lasp.tactic.sobjects as sobjects
import lasp.tactic.context as context
import lasp.tactic.project_configs as cfg
import generateNote
import NotesView
import subprocess
import Progress_Bar
import time
import CompressorApp as ComApp
import json_saver as app_json

reload(sobjects)
reload(context)
reload(cfg)

filters_json_path = 'c:/tmp/filters.json'

head_re = re.compile(r'(.*?)[0-9]+\..*')

programa = {'pdPlayer': ['C:/Program Files/Pdplayer 64/pdplayer64.exe ','C:/Program Files (x86)/Pdplayer/pdplayer.exe '],
             'kinovea': 'C:/Program Files/Kinovea/Kinovea.exe -file ',
            'winrar': 'C:/Program Files/WinRAR/WinRAR.exe '}#Hay que dejar un espacio al final del path para que funcione

supervisor_list = ['lasp-igorfinkiel', 'lasp-mkamijo', 'lasp-ehasl', 'lasp-elozano', 'lasp-msantilli', 'lasp-aturano']
coordinador_list = ['lasp-gpicart', 'lasp-aavila', 'lasp-aestevez', 'lasp-cmoscariello', supervisor_list]
status_list = ['Pendiente', 'Asignado', 'En Proceso', 'Ajustar', 'Stand By', 'Revisar', 'Supervisar', 'Aprobado Interno'
            , 'Aprobado', 'Entregado']
comboBox_analog_column = {'combo_Proyecto_Filtra': 'proyecto', 'combo_Episodio_Filtra': 'episodio', 'combo_Escena_Filtra': 'secuencia', 'combo_Prio_Filtra': 'prioridad', 'combo_Asignado_Filtra': 'asignado', 'combo_Complejidad_Filtra': 'complejidad', 'combo_Status_Filt': 'status', 'combo_Supervisor_Filt': 'supervisor'}

def getMayaWindow():
    from shiboken import wrapInstance
    import maya.OpenMayaUI as omui
    return wrapInstance(long(omui.MQtUtil.mainWindow()), QWidget)

class AddTaskRow(QThread):
    """Clase Trhead que se encarga de ordenar la informacion que se importa de la base de datos en un diccionario,
    para luego ser enviada a 'add_task_row' y cargar la info en la tabla correspondiente"""
    taskData = Signal(dict, int)
    adjustTables = Signal()
    progress_values = Signal(int)#Emite signal con el valor de progreso del cargado de tareas
    set_max = Signal(int)
    open_progress_bar = Signal()#Emite signal para abrir el statausBar
    close_progess_bar = Signal()#Emite signal para cerrar el statusBar


    def __init__(self, tasks, tables, filters):
        """Inicializa la clase AddTaskRow"""
        QThread.__init__(self)
        self.tasks = tasks
        self.tables = {}
        self.filters = filters
        for key, table in tables.items():
            self.tables[key] = table.columns

    def __del__(self):
        self.wait()

    def run(self):
        """Corre el Thread"""
        data = {}
        self.open_progress_bar.emit()
        for progress, task in enumerate(self.tasks):
            self.set_max.emit(self.tasks._data.__len__())
            if not task:
                break
            elif task.search_code.startswith('PLANOS'):
                columns = self.tables['shots']
            elif task.search_code.startswith('ASSETS_3D'):
                columns = self.tables['assets']
            elif task.search_code.startswith('MATTE_PAINTING'):
                columns = self.tables['assets']
            elif task.search_code.startswith('CONCEPTS'):
                columns = self.tables['assets']
            elif task.search_code.startswith('GRAFICAS'):
                columns = self.tables['assets']
            else:
                continue

            work = sobjects.get_work(task, ['code', 'name', 'secuencias_code', 'supervisor', 'assigned'])

            if work:
                data['task'] = task
                for column in columns:
                    data[column] = {}
                    if column == 'image':
                        sobjects.server.set_project(task.project_code)
                        if work.thumbnail == None:
                            data[column]['value'] = 'None'
                        else:
                            data[column]['value'] = work.thumbnail

                    elif column == 'asignado':
                        sobjects.server.set_project(task.project_code)
                        data[column]['value'] = task._data['assigned']

                    elif column == 'name':
                        sobjects.server.set_project(task.project_code)
                        name = unicode(work.name)
                        data[column]['value'] = name

                    elif column == 'proyecto':
                        sobjects.server.set_project(task.project_code)
                        data[column]['value'] = work._project

                    elif column == 'secuencia':
                        sobjects.server.set_project(task.project_code)
                        self.sequence = sobjects.server.query('LaSP/secuencias', filters=(['code', work.secuencias_code],),
                                                         columns=['name', 'episodios_code'])
                        if self.sequence:
                            data[column]['value'] = str(self.sequence[0]['name'])

                        else:
                            data[column]['value'] = 'None'

                    elif column == 'episodio':
                        sobjects.server.set_project(task.project_code)
                        if self.sequence:
                            episodio = sobjects.server.query('LaSP/episodios', filters=(['code', self.sequence[0]['episodios_code']],),
                                                             columns=['name'])
                            if episodio:
                                data[column]['value'] = episodio[0]['name']
                            else:
                                data[column]['value'] = 'None'

                    elif column == 'notas':
                        sobjects.server.set_project(task.project_code)
                        search_type = 'sthpw/note'
                        filters = []
                        filters.append(['search_type', task.search_type])
                        filters.append(['search_id', task.search_id])
                        self.note = (sobjects.server.query(search_type, filters,
                                                           columns=['note', 'timestamp', ]))  # 'search_code']))

                        if self.note:
                            # data[column]['value'] = 'Notas (' + str(len(self.note)) + ')'
                            data[column]['value'] = len(self.note)
                        else:
                            pass

                    elif column == 'descripcion':
                        sobjects.server.set_project(task.project_code)
                        search_type = 'LaSP/planos'
                        filters = []
                        filters.append(['code', work.code], )
                        descriptions = sobjects.server.query(search_type, filters, )  # columns=['description'])
                        if descriptions:
                            data[column]['value'] = descriptions[0]['description']
                        else:
                            data[column]['value'] = 'None'

                    elif column == 'status':
                        self.status = getattr(task, column)
                        data[column]['value'] = self.status

                    elif column == 'supervisor':
                        data[column]['value'] = task.supervisor

                    elif column == 'snapshot':
                        data[column]['value'] = str(len(task.snapshot_code))
                    else:
                        data[column]['value'] = getattr(task, column)

                self.taskData.emit(data, progress)
        self.adjustTables.emit()
        self.close_progess_bar.emit()

class LoadImageFromUrl(QThread):
    """Clae Thread que se encarga de preparar la carga de la imagen icono en la tabla (el Signal se conecta en la linea
     1309)"""
    recibeImage = Signal(dict)

    def __init__(self, url, w, h):
        QThread.__init__(self)
        self.url = url
        self.w = w
        self.h = h

    def __del__(self):
        self.wait()

    def run(self):
        try:
            if self.url:
                image = QLabel()
                image.setScaledContents(True)
                data = urlopen(self.url).read()
                self.recibeImage.emit(data)

        except IOError:
            pass

class ImagePopup:
    """Genera el popup con la imagen/icono seleccionada de la tabla"""
    def __init__(self, bitmap, w=640, h=360):
        self.image = QLabel()
        self.image.show()
        self.image.setScaledContents(True)
        self.image.setPixmap(bitmap)
        self.image.resize(w, h)

def remove_version(path):
    return ''.join(re.findall('(.*)_v[0-9]+([.].*)', path)[0])

class AutoLoader(QWidget):
    """Clase principal que inicializa la interfaz, botones, popup, carga de datos y otros"""
    def __init__(self, context=None):
        QWidget.__init__(self)
        self.ui = load_ui(__file__[:__file__.rindex('.')] + '.ui', self)
        self.context = context
        if self.context:
            self.sobject = self.context.currentSobject
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.ui)
        self.tables = {'shots': self.ui.Seq_Shot_TaskTable, 'assets': self.ui.assets_taskTable}
        self.ui.Seq_Shot_TaskTable.type = 'shots'
        self.assets_taskTable = 'assets'
        self.windows_title = self.windowTitle()

        self.carga = 0
        self.saved_filters_list = []

        self.ui.combo_Sup_Modif.setEnabled(True)
        if self.checkSupervisorLogin():
            self.ui.CoordinacionCheckBox.setEnabled(True)
            self.ui.combo_Sup_Modif.setEnabled(True)
            self.ui.combo_Asignado_Modif.setEnabled(True)
            self.ui.combo_Asignado_Filtra.setEnabled(True)
            self.ui.supervisorCheckBox.setEnabled(True)
        elif self.checkCoordinadorLogin():
            self.ui.CoordinacionCheckBox.setEnabled(True)
            # self.ui.supervisorCheckBox.setEnabled(True)
            self.ui.combo_Sup_Modif.setEnabled(True)
            self.ui.combo_Asignado_Modif.setEnabled(True)
            self.ui.combo_Asignado_Filtra.setEnabled(True)
        # else:
        self.ui.combo_Sup_Modif.setEnabled(True)

        self.ui.loginName.setText('Login: %s' % self.server.login)
        # self.ui.actionLog_in_new_User.triggered.connect(self.relogin)

        for table in self.tables.values():
            table.setSortingEnabled(True)
            table.setContextMenuPolicy(Qt.CustomContextMenu)
            table.customContextMenuRequested.connect(self.on_context_menu)

        try:
            self.ui.refresh_button.clicked.connect(self.refresh)
            self.ui.create_button.clicked.connect(self.create_file)
            self.ui.createfrom_button.clicked.connect(self.create_from_file)

            self.ui.load_button.clicked.connect(self.load_file)
            self.ui.import_button.clicked.connect(self.import_file)
            self.ui.save_button.clicked.connect(self.save_file)
            self.ui.show_button.clicked.connect(self.show_file)
            self.ui.save_filters_button.clicked.connect(self.save_all_filters)
            self.ui.load_filters_button.clicked.connect(self.load_filters)
            self.ui.loginName.clicked.connect(self.relogin)
            self.ui.Filter_Button.clicked.connect(self.filtrar)
            self.ui.Clean_Filters_Button.clicked.connect(self.clean_filters)


            self.ui.filter_app.stateChanged.connect(self.refresh)
            # SubMenu principal del boton derecho****************
            self.popMenu = QMenu(self.ui.Seq_Shot_TaskTable)
            # Agrega subMenus al Menu principal******************
            self.exploreMenu = self.popMenu.addMenu('Explore')
            self.openMenu = self.popMenu.addMenu('Open')
            self.superviseMenu = self.popMenu.addMenu('Supervisar')
            self.noteMenu = self.popMenu.addMenu('Notes')

            action = QAction('View Thumbnail', self.ui.Seq_Shot_TaskTable)
            action2 = QAction('Open Compressor', self.ui.Seq_Shot_TaskTable)
            self.popMenu.addAction(action)
            self.popMenu.addAction(action2)
            action.triggered.connect(self.view_thumbnail)
            action2.triggered.connect(self.export_shot_method)

            # Filters//////////////////////////////////
            self.makeModifCombos()
            # self.refreshFilerCombos()

            self.ui.Seq_Shot_TaskTable.itemDoubleClicked.connect(self.create_file)
            self.ui.combo_Status_Filt.activated.connect(self.status_filter_metod)
            self.ui.combo_Supervisor_Filt.activated.connect(self.supervisor_filter_metod)
            self.ui.combo_Asignado_Filtra.activated.connect(self.assigned_filter_metod)
            self.ui.combo_Escena_Filtra.activated.connect(self.escena_filtra_metod)
            self.ui.combo_Asignado_Filtra.activated.connect(self.asignado_filtra_metod)
            # self.ui.combo_Proyecto_Filtra.activated.connect(self.proyecto_filtra_metod)

            self.ui.supervisorCheckBox.stateChanged.connect(self.supervisorSelect)
            self.ui.CoordinacionCheckBox.stateChanged.connect(self.coordinadorSelected)

            # Edit///////////////////////////////////
            self.ui.combo_Status_Modif.activated.connect(self.set_status)
            self.ui.combo_Sup_Modif.activated.connect(self.set_supervisor)
            self.ui.combo_Asignado_Modif.activated.connect(self.set_assigned)

            self.progress_bar_window = Progress_Bar.Module()
            self.progress_bar_window.close_principal_window.connect(self.close_ramon_window)
            self.populate_task_table()
            self.populate_app_context()

            self.ui.combo_Proyecto_Filtra.activated.connect(self.activate_project_combo)
            if self.context.soft == 'maya':
                self.context.dock_ui()
        except Exception, e:
            raise e


    def activate_project_combo(self, index):
        """En caso de estar seleccionada la vista de coordinacion y ser activado el combo de proyecto, este metodo
        se encarga de llenar y cargar los combos de Episodios y Escenas. en base al proyecto seleccionado"""
        if sobjects.coordinadorView and self.ui.combo_Proyecto_Filtra.currentText():
            self.generateSubFiltersInCoordinationView()
            self.turn_disable_combos()
            self.ui.combo_Escena_Filtra.setEnabled(True)
            self.ui.combo_Episodio_Filtra.setEnabled(True)
            QMessageBox.information(None, u'Importante', 'A continuacion seleccione Episodio y/o Escena...')
        else:
            self.proyecto_filtra_metod(index)

    def generateSubFiltersInCoordinationView(self):
        project = self.ui.combo_Proyecto_Filtra.currentText()
        sobjects.server.set_project(project)
        self.generateEpidosdiosComboInCoordinatorView(project)
        self.generateSecuenciasComboInCoordinatorView(project)

    def generateEpidosdiosComboInCoordinatorView(self, project):
        self.refreshEpisodioCombo()
        relative_dir = project + "/episodios"
        exp = "@GET(LaSP/episodios['relative_dir', '=', " + "'" + relative_dir + "'" + "].name)"
        episodios_list = self.server.eval(exp)
        self.ui.combo_Episodio_Filtra.addItems(sorted(episodios_list))
        self.ui.combo_Episodio_Filtra.setSizeAdjustPolicy(self.ui.combo_Episodio_Filtra.AdjustToContents)

    def generateSecuenciasComboInCoordinatorView(self, project):
        self.refreshEscenaCombo()
        relative_dir = project + "/secuencias"
        exp = "@GET(LaSP/secuencias['relative_dir', '=', " + "'" + relative_dir + "'" + "].name)"
        secuencias_list = self.server.eval(exp)
        self.ui.combo_Escena_Filtra.addItems(sorted(secuencias_list))
        self.ui.combo_Escena_Filtra.setSizeAdjustPolicy(self.ui.combo_Escena_Filtra.AdjustToContents)

    def coordinadorSelected(self, state):
        """IDEM supervisorSelect pero con el checkBox de Coordinacion"""
        if state == 2:
            self.turn_filters_to_cero()
            self.turn_to_coordinadorView()

        else:
            self.turn_filters_to_cero()
            self.ui.supervisorCheckBox.setEnabled(True)
            self.turn_enabled_combos()
            sobjects.coordinadorView = False
            self.refresh()

    def turn_to_coordinadorView(self):
        """Metodo que se encarga de llevar la interfaz al modo Coordinacoin inicial una vez que se ha seleccionado
        el checkBox de coordinacion:
                -deshabilita la mayoria de los filtros/combos, dejando solo habilitado el de Proyectos
                -setea la variable 'coordinadorView' del modulo 'sobjects' a 'True'
                -llama al metodo Refresh() para refrescar la tabla
                -Muestra un mensaje popUp de advertencia"""
        sobjects.coordinadorView = True
        self.turn_disable_combos()
        self.refresh()
        QMessageBox.warning(None, u'Advertencia!', 'Seleccione proyecto para comenzar')

    def turn_disable_combos(self):
        self.ui.supervisorCheckBox.setEnabled(False)
        self.ui.combo_Escena_Filtra.setEnabled(False)
        self.ui.combo_Episodio_Filtra.setEnabled(False)
        self.ui.combo_Asignado_Filtra.setEnabled(False)
        self.ui.combo_Supervisor_Filt.setEnabled(False)
        self.ui.combo_Status_Filt.setEnabled(False)

    def turn_enabled_combos(self):
        """Habilita combos"""
        self.ui.combo_Escena_Filtra.setEnabled(True)
        self.ui.combo_Episodio_Filtra.setEnabled(True)
        self.ui.combo_Asignado_Filtra.setEnabled(True)
        self.ui.combo_Status_Filt.setEnabled(True)
        self.ui.combo_Supervisor_Filt.setEnabled(True)

    def filtrar(self):
        """Metodo que responde cuando se activa el boton 'Filtrar'"""
        # self.turn_enabled_combos()
        self.refresh()

    def close_ramon_window(self):
        """Cierra la ventana principal"""
        self.close()

    def save_all_filters(self):
        """Metodo que se encarga de guardar los filtros seleccionados en un .json (con el boton 'Save Filters')
        par luego ser cargados con el boton 'Load Filters'"""

        if self.filters:
            new = app_json.Main(filters_json_path)
            new.save(self.filters)
        else:
            QMessageBox.information(None, u'Atencion!', 'No hay datos para guardar')

    def load_filters(self):
        """Metodo que se encarga de cargar la info de los filtros guardados en el .json"""
        if os.path.exists(filters_json_path):
            self.filters = None
            saved_filters = app_json.Main(filters_json_path)
            self.filters = saved_filters.load()
            if not self.filters:
                QMessageBox.information(None, u'Atencion!', 'No hay datos guardados')
            else:
                self.reload_filters()


    def reload_filters(self):
        """Metodo que se encarga de setear los combos/filtros en base a la info levantada del .json"""
        for key in self.filters:
            filtro = self.filters[key]
            if key == 'combo_Status_Filt':
                index = self.ui.combo_Status_Filt.findText(filtro)
                self.ui.combo_Status_Filt.setCurrentIndex(index)
            elif key == 'combo_Supervisor_Filt':
                index = self.ui.combo_Supervisor_Filt.findText(filtro)
                self.ui.combo_Supervisor_Filt.setCurrentIndex(index)
            elif key == 'combo_Asignado_Filtra':
                index = self.ui.combo_Asignado_Filtra.findText(filtro)
                self.ui.combo_Asignado_Filtra.setCurrentIndex(index)
            elif key == 'combo_Proyecto_Filtra':
                index = self.ui.combo_Proyecto_Filtra.findText(filtro)
                self.ui.combo_Proyecto_Filtra.setCurrentIndex(index)
            elif key == 'combo_Escena_Filtra':
                index = self.ui.combo_Escena_Filtra.findText(filtro)
                self.ui.combo_Escena_Filtra.setCurrentIndex(index)

    def update_progress_bar(self, progress):
        """LLama al metodo que actualiza la barra de progreso del modulo 'Progress_Bar'"""
        self.progress_bar_window.update_progress(progress)

    def set_maxim(self, maxim):
        """LLama al metodo que setea el valor maximo de la barra de progreso del modulo 'Progress_Bar'"""
        self.progress_bar_window.set_max_value(maxim)

    def show_bar(self):
        """Muestra la barra de progreso durante la carga de planos"""
        self.progress_bar_window.show()

    def close_progress_bar(self):
        """Cierra la barra de prograso cuando finaliza la carga de planos. En caso de no encontrar planos que cargar
        Muestra un mensaje"""
        if self.progress_bar_window.get_progress() == -1 or self.ui.Seq_Shot_TaskTable.rowCount == 0:
            self.progress_bar_window.object.estado.setText('No se encontraron tareas')

        else:
            self.progress_bar_window.object.estado.setText('Finalizado!')
        self.progress_bar_window.repaint()
        time.sleep(1)
        self.ui.setEnabled(True)
        self.progress_bar_window.cerrar()

    def clean_filters(self):
        """Lleva los filtros/combos a cero y refresca la tabla.
        En caso de estar seleccionada la vista de coordinacion, entra en vista de coordinacion"""
        self.turn_filters_to_cero()
        if sobjects.coordinadorView:
            self.turn_to_coordinadorView()
        else:
            self.refresh()

    def turn_filters_to_cero(self):
        """Setea los filtros/combos en cero y limpia la lista que contenia los filtros seleccionados hasta el momento"""
        self.ui.combo_Status_Filt.setCurrentIndex(0)
        self.ui.combo_Supervisor_Filt.setCurrentIndex(0)
        self.ui.combo_Asignado_Filtra.setCurrentIndex(0)
        self.ui.combo_Proyecto_Filtra.setCurrentIndex(0)
        self.ui.combo_Episodio_Filtra.setCurrentIndex(0)
        self.ui.combo_Escena_Filtra.setCurrentIndex(0)
        self.saved_filters_list = []

    def checkSupervisorLogin(self):
        """Chequea si al seleccionar la vista de supervisor, el logueado es un supervisor"""
        for supervisor in supervisor_list:
            if self.server.login == supervisor:
                return True
        return False

    def checkCoordinadorLogin(self):
        """Chequea si al seleccionar la vista de coordinacion, el logueado es un coordinador"""
        for coordinador in coordinador_list:
            if self.server.login == coordinador:
                return True
        return False

    def supervisorSelect(self, state):
        """Chequea si se ha activado el checkBox de supervision. En caso afimativo: lleva los filtros a cero, setea la
        variable 'supervisorView' del modulo 'sobjects' a 'True' y deshabilita el checkbox de coordinacion

        state: Devuelve el estaco del checkbox: activo = 2, no activo = 0"""
        if state == 2:
            self.turn_filters_to_cero()
            sobjects.supervisorView = True
            self.ui.CoordinacionCheckBox.setEnabled(False)
        else:
            self.turn_filters_to_cero()
            sobjects.supervisorView = False
            self.ui.CoordinacionCheckBox.setEnabled(True)
        self.refresh()


    def addNotes(self):
        """Agrega Notas y suma la cantidad de notas totales en la tabla"""
        self.note = generateNote.new(self.selected_task, self.server, self.refresh)
        if self.note:
            table = self.currentTable
            row = table.currentRow()
            itemWidget = table.item(row, 6)#TODO: cambiar nnumero 6 por la ubicacion de la columna "notas"
            cantidad_de_notas = itemWidget.text()
            if cantidad_de_notas == 'None':
                cantidad_de_notas = 0
                cantidad_de_notas = int(cantidad_de_notas) + 1
            nueva_cantidad = QTableWidgetItem()
            nueva_cantidad.setText(str(cantidad_de_notas))
            table.setItem(row, 6, nueva_cantidad)

    def makeModifCombos(self):
        """Genera los ComboBox de modificacion"""
        self.makeSupervisorModifCombo()
        self.makeAssignedModifCombo()
        self.makeStatusModifCombo()

    def makeStatusModifCombo(self):
        """Llena de datos el combo box de status"""
        self.ui.combo_Status_Modif.clear()
        self.ui.combo_Status_Modif.addItems(status_list)

    def makeProjectComboInCoordinatorView(self):
        self.ui.combo_Proyecto_Filtra.clear()
        self.ui.combo_Proyecto_Filtra.addItem(None)
        search_type = ('sthpw/project')
        projects = self.server.query(search_type, filters=[], columns=["code"])
        for project in projects:
            project_name = str(project["code"])
            if project_name != 'sthpw' and project_name != 'admin':
                self.ui.combo_Proyecto_Filtra.addItem(project['code'])
        self.ui.combo_Proyecto_Filtra.setSizeAdjustPolicy(self.ui.combo_Proyecto_Filtra.AdjustToContents)

    def makeSupervisorModifCombo(self):
        self.ui.combo_Sup_Modif.clear()
        self.ui.combo_Sup_Modif.addItems(supervisor_list)

    def makeAssignedModifCombo(self):
        assigneds_list = []
        search_type = ('sthpw/login')
        assigneds_data = self.server.query(search_type, filters=None, columns=['code'])
        for assigned in assigneds_data:
            assigneds_list.append(assigned['code'])
        self.ui.combo_Asignado_Modif.clear()
        self.ui.combo_Asignado_Modif.addItems(assigneds_list)

    def cleanFilterCombos(self):
        """Este metodo se encarga de distribuir la limpieza de los comboBox determinados: Los limpia, agrega el
         elemento vacio y quedan listos para ser completados con la informacion conrrespondiente durante la carga
         de planos.
         En caso de que algun filtro este seleccionado, setea el mismo con el elemento correspondiente"""
        self.refreshProjectCombo()
        self.refreshSupervisorCombo()
        self.refreshAssignedCombo()
        self.refreshStatusCombo()
        self.refreshEscenaCombo()
        self.refreshEpisodioCombo()

    def refreshStatusCombo(self):
        self.check_selected_item_combo(self.ui.combo_Status_Filt)

    def refreshEpisodioCombo(self):#Generar los metodos de refresh independientemente de la generacion de los combos!!
        self.check_selected_item_combo(self.ui.combo_Episodio_Filtra)

    def refreshEscenaCombo(self):
        self.check_selected_item_combo(self.ui.combo_Escena_Filtra)

    def refreshProjectCombo(self):
        self.check_selected_item_combo(self.ui.combo_Proyecto_Filtra)

    def refreshSupervisorCombo(self):
        self.check_selected_item_combo(self.ui.combo_Supervisor_Filt)

    def refreshAssignedCombo(self):
        self.check_selected_item_combo(self.ui.combo_Asignado_Filtra)

    def check_selected_item_combo(self, combo):
        """Metodo que limpia, agrega elemento vacio o setea en el elemento actual seleccionado, los combos
         correspondientes"""
        current_filter = combo.currentText()
        combo.clear()
        combo.addItem(None)
        if current_filter:
            self.saved_filters_list.append(current_filter)
            combo.addItem(current_filter)

    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def proyecto_filtra_metod(self, index):
        self.ui.combo_Proyecto_Filtra.setCurrentIndex(index)

    def asignado_filtra_metod(self, index):
        self.ui.combo_Asignado_Filtra.setCurrentIndex(index)

    def escena_filtra_metod(self, index):
        self.ui.combo_Escena_Filtra.setCurrentIndex(index)

    def status_filter_metod(self, index):
        self.ui.combo_Status_Filt.setCurrentIndex(index)

    def supervisor_filter_metod(self, index):
        self.ui.combo_Supervisor_Filt.setCurrentIndex(index)

    def assigned_filter_metod(self, index):
        self.ui.combo_Asignado_Filtra.setCurrentIndex(index)

    def set_status(self, index):
        status_selected = self.ui.combo_Status_Modif.itemText(index)
        self.setSelectedCells('status', status_selected)

    def set_supervisor(self, index):
        sup_selected = self.ui.combo_Sup_Modif.itemText(index)
        self.setSelectedCells('supervisor', sup_selected)

    def set_assigned(self, index):
        assigned_select = self.ui.combo_Asignado_Modif.itemText(index)
        self.setSelectedCells('assigned', assigned_select)

    def setSelectedCells(self, column, selected):
        """Metodo que se encarga de cambiar las celdas seleccionados en grupo.
        Cambia en la DB los datos correspondientes a las tareas seleccionadas y modificadas"""
        tasks_codes = self.selected_tasks_codes()
        if tasks_codes:
            self.mensajeAlerta = QMessageBox.information(self, 'Warning', 'Desea realizar modificacion?', QMessageBox.Ok,
                                                         QMessageBox.Abort)
            if self.mensajeAlerta == QMessageBox.StandardButton.FirstButton:
                searchKeys = self.searchKeysConstructor(tasks_codes)
                for sk in searchKeys:
                    data = {column: selected}
                    self.server.update(sk, data)
                self.refresh()
        else:
            QMessageBox.information(self, 'Sin seleccion', 'Seleccione una tarea', QMessageBox.Ok)

    def searchKeysConstructor(self, tasks_codes):
        """:return: Todos las tasks_keys seleccionadas en la tabla"""
        searchKeys = []
        for a_task_code in tasks_codes:
            searchKey = sobjects.server.build_search_key('sthpw/task', a_task_code)
            searchKeys.append(searchKey)
        return searchKeys

    def selected_tasks_codes(self):
        """Devuelve una lista con los planos/tareas seleccionados"""
        table = self.currentTable
        selected_items = table.selectionModel().selectedRows()
        tasks = []
        for i in selected_items:
            row = i.row()
            column = len(table.columns) - 1
            task_code = str(table.item(row, column).text())  # Task code. EJ: TASK00018822
            # x = self.tasks[str(table.item(row, len(table.columns) - 1).text())]
            tasks.append(task_code)
        return tasks

    def to(self, func):
        if func in AutoLoader.__dict__:
            return partial(AutoLoader.__dict__[func], self)

    def relogin(self):
        """Reloguea"""
        self._server = sobjects.relogin()
        self.ui.loginName.setText('Login: %s' % self.server.login)
        self.refresh()

    @property
    def filter_app(self):
        return self.ui.filter_app.checkState() == Qt.Checked

#Metodo que maneja la apertura de los submenues*************************************************************************
    def on_context_menu(self, point):
        """Metodo que se encargade llamar a los submetodos que generan los submenues y a sus acciones"""
        if self.ui.Seq_Shot_TaskTable.currentRow() >= 0:
            self.search_lowres_path()
            self.generate_explore_menu()
            self.generate_open_menu()
            self.generate_supervise_menu()
            self.generate_note_menu()
            self.generate_lowres_versions()
            self.lowresExplorerMenu.triggered.connect(self.explore_lowres_version)
            self.lowresMenu.triggered.connect(self.open_lowres_version)
            self.popMenu.exec_(self.ui.Seq_Shot_TaskTable.mapToGlobal(point))

# ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *

    @staticmethod
    def snapshots(task):
        filters = (['search_code', task.search_code], ['project_code', task.project_code], ['process', task.process])
        columns = ['code', 'version', 'is_current', 'timestamp', 'project_code', 'process',
                   'search_code', 'context', 'search_type', 'login']

        return sobjects.Snapshots(filters=filters, columns=columns)

    @property
    def Clients(self):
        if not '_clients' in dir(self):
            self._clients = sobjects.Clients()
        return self._clients

    def get_shot_data(self, mytask):
        work = sobjects.get_work(mytask)
        client = self.Clients.first.code
        project = mytask.project_code
        seq = sobjects.Sequences(filters=[('code', work.secuencias_code), ], columns=['name', ],
                                 project=project).first.name
        shot = work.name
        task = mytask.process
        user = mytask.assigned
        startHandle = work.frame_in
        endHandle = work.frame_out
        dict = locals()
        dict.pop('mytask')
        dict.pop('work')
        return dict

    def export_shot_method(self):
        """Instancia la aplicacion de compresion de datos y le pasa como parametro una lista con la
        info. de las tareas seleccionadas"""
        # info_tasks_list = self.selected_tasks_info()
        self.compressor = ComApp.Main(self.selected_tasks_info())

        # new_folder = self.recolect_data(info_tasks_list)#Resolver metodo(Guardar archivos con sus rutas  en una carpeta nueva en c:/temp)
        # ComApp.comprimir(new_folder)
        # print info_tasks_list

    def selected_tasks_info(self):
        """Devuelve una lista con la informacion de las tareas seleccionadas de la tabla"""
        selected_tasks_list = []
        tasks_codes = self.selected_tasks_codes()
        for code in tasks_codes:
            task = self.tasks[str(code)]
            selected_tasks_list.append(task)
            # print task.first_version_path
        return selected_tasks_list

    def view_thumbnail(self):
        row = self.ui.Seq_Shot_TaskTable.currentRow()
        bitmap = self.ui.Seq_Shot_TaskTable.cellWidget(row, 0).bitmap
        self.ViewThumbnail = ImagePopup(bitmap)
        print ("           pasa por view thumbnail             ")

    def search_lowres_path(self):
        """Devuelve las versiones que contiene el lowres"""
        self.lowres_versions = self.context.search_lowres_path(self.selected_task)

    def generate_open_menu(self):
        """Genera el submenu de ejecucion de archivos por el soft correspondiente"""
        self.openMenu.clear()
        self.versionMenu = self.openMenu.addMenu('Versions')
        action0 = QAction('Media', self.ui.Seq_Shot_TaskTable)
        action1 = QAction('Fullres', self.ui.Seq_Shot_TaskTable)
        self.lowresMenu = self.openMenu.addMenu('Lowres')

        self.openMenu.addAction(action0)
        self.openMenu.addAction(action1)

        action0.triggered.connect(self.open_media)
        action1.triggered.connect(self.open_fullres)

        self.generate_version_items()
        self.versionMenu.triggered.connect(self.open_version)

    def generate_explore_menu(self):
        """Genera el submenu de exploracion"""
        self.actions = {}
        self.exploreMenu.clear()
        self.lowresExplorerMenu = self.exploreMenu.addMenu('Explore Lowres')
        action0 = QAction('Explore Versions', self.ui.Seq_Shot_TaskTable)
        action2 = QAction('Explore Media', self.ui.Seq_Shot_TaskTable)
        action3 = QAction('Explore FullRes', self.ui.Seq_Shot_TaskTable)

        self.exploreMenu.addAction(action0)
        self.exploreMenu.addAction(action2)
        self.exploreMenu.addAction(action3)

        action0.triggered.connect(self.explore_versions)
        action2.triggered.connect(self.explore_media)
        action3.triggered.connect(self.explore_fullres)

    def generate_note_menu(self):
        """Genera el submenu de notas: vista y agregado"""
        self.noteMenu.clear()
        action1 = QAction('Ver Notas', self.ui.Seq_Shot_TaskTable)
        action2 = QAction('Agregar Notas', self.ui.Seq_Shot_TaskTable)

        self.noteMenu.addAction(action1)
        self.noteMenu.addAction(action2)

        action1.triggered.connect(self.showNotes)
        action2.triggered.connect(self.addNotes)
        # self.generate_lowres_versions()

    def generate_supervise_menu(self):
        """Genera el submenu de supervision"""
        self.superviseMenu.clear()
        self.kinoveaMenu = self.superviseMenu.addMenu('Abrir Kinovea')
        self.superviseOpenMenu = self.superviseMenu.addMenu('Open')
        self.kinoveaLowresMenu = self.kinoveaMenu.addMenu('Lowres')
        self.openLowresMenu = self.superviseOpenMenu.addMenu('Lowres')
        actionfullres = QAction('Fullres', self.ui.Seq_Shot_TaskTable)
        actionfullresOpen = QAction('Fullres', self.ui.Seq_Shot_TaskTable)
        self.kinoveaMenu.addAction(actionfullres)
        self.superviseOpenMenu.addAction(actionfullresOpen)
        self.kinoveaMenu.triggered.connect(self.start_process_kinoveaOpen)
        self.openLowresMenu.triggered.connect(self.supervise_open_lowres_version)
        actionfullresOpen.triggered.connect(self.supervise_open_fullres)


    def generate_lowres_versions(self):
        """Generea y agraga las versiones al submenu de lowress en ambas opciones: open y explorer"""
        self.versions = []
        if self.lowres_versions and self.lowres_versions['dir']:
            for version in self.lowres_versions['dir']:
                self.lowresMenu.addAction(version)
                self.lowresExplorerMenu.addAction(version)
                self.kinoveaLowresMenu.addAction(version)
                self.openLowresMenu.addAction(version)
                self.versions.append(version)
        elif self.lowres_versions:
            self.lowresExplorerMenu.addAction('Lowres')
            self.lowresMenu.addAction('Lowres')
            self.kinoveaLowresMenu.addAction('Lowres')
            self.openLowresMenu.addAction('Lowres')
        else:
            self.lowresExplorerMenu.addAction('Vacio')
            self.lowresMenu.addAction('Vacio')
            self.kinoveaLowresMenu.addAction('Vacio')
            self.openLowresMenu.addAction('Vacio')

    def generate_version_items(self):
        """Genera la lista de archivos del submenu versiones"""
        self.versionMenu.clear()
        self.versions_data = self.context.get_version_items(self.selected_task)
        if self.versions_data and self.versions_data['versiones']:
            for version in self.versions_data['versiones']:
                self.versionMenu.addAction(version)
        else:
            self.versionMenu.addAction('Vacio')

#///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def start_process_kinoveaOpen(self, action):
        """Metodo que se encarga de generar la apertura del archivo deseado mediante Kinovea:
        Llama a la app correspondiente en donde se genera el video, mediante el modulo proRessMini"""
        video = self.context.open_kinovea(self.selected_task, action)
        if video:
            print 'Open Kinovea'
            subprocess.Popen(programa['kinovea'] + video)
        else:
            QMessageBox.warning(None, u'Warning!', 'No hay nada para abrir')

    # ///////////////////////////////////////////////////////////////////////////////////////////////////////////////

    def open_version(self, action):
        """Abre el item seleccionado mediante el programa que corresponda"""
        self.context.open_version(action, self.versions_data)


    def load_versions(self, snapshot):
        self.context.Load(snapshot, is_current=False, version=snapshot.version)
        self.sobject = self.context.get_sobject_from_path(self.context.currentFile())
        self.set_status_colors()


    def open_media(self):
        path = Path(self.selected_task.first_version_path).mediaPath
        if os.path.exists(path):
            self.simple_open(path)
        else:
            QMessageBox.warning(None, u'Warning!', 'No existe Media')


    def open_fullres(self):
        self.fullres_path = self.context.get_fullres_path(self.selected_task)
        self.simple_open(self.fullres_path)


    def open_lowres_version(self, action):
        if self.lowres_versions and self.lowres_versions['dir']:
            path = os.path.join(self.lowres_versions['base'], action.text())
        elif self.lowres_versions:
            path = self.lowres_versions['base']
        if os.path.exists(path):
            self.simple_open(path)
        else:
                QMessageBox.warning(None, u'Lowres Error!', 'No existe Lowres')


    def supervise_open_lowres_version(self, action):
        if self.lowres_versions and self.lowres_versions['dir']:
            path = os.path.join(self.lowres_versions['base'], action.text())
        elif self.lowres_versions:
            path = self.lowres_versions['base']
        if os.path.exists(path):
            self.double_open(path)
        else:
            QMessageBox.warning(None, u'Lowres Error!', 'No existe Lowres')


    def supervise_open_fullres(self):
        self.fullres_path = self.context.get_fullres_path(self.selected_task)
        self.double_open(self.fullres_path)


    def double_open(self, path):
        """Metodo que se encarga de abrir en PdPlayer: fullress o lowress con la media correspondiente
        al mismo tiempo"""
        correct_path = self.giveMePath(path)
        media_dir = Path(self.selected_task.first_version_path).mediaPath
        media_files = os.listdir(media_dir)
        if media_files:
            media_dir = os.path.join(media_dir, media_files[0])
        final_path = media_dir + ' ' + correct_path
        try:
            for pdPlayer_path in programa['pdPlayer']:
                if os.path.exists(pdPlayer_path):
                    subprocess.Popen(pdPlayer_path + final_path)
                    break
            return
        except Exception, e:
            print e
            QMessageBox.warning(None, u'Error!', 'No se puede abrir el archivo. Compruebe que tenga instalado Pdplayer')


    def simple_open(self, path):
        """Abre en forma simple el archivo del submenu seleccionado"""
        if path:
            correct_path = self.giveMePath(path)
            for pdPlayer_path in programa['pdPlayer']:
                if os.path.exists(pdPlayer_path):
                    try:
                        subprocess.Popen(pdPlayer_path + correct_path)
                        break
                    except:
                        QMessageBox.warning(None, u'Error!',
                                            'No se puede abrir el archivo. Compruebe que tenga instalado Pdplayer')


    def giveMePath(self, path):
        """Devuelve la ruta completa de un archivo"""
        if os.listdir(path):
            quickTime_file = self.search_for_quicktime(path)
            if quickTime_file:
                path = os.path.join(path, quickTime_file)
                path = os.path.normpath(path)
                return path
            else:
                for file in os.listdir(path):
                    dir = os.path.join(path, file)
                    correct_path = os.path.normpath(dir)
                    return correct_path
        else:
            QMessageBox.warning(None, u'Vacio!', 'Directorio vacio')


    def search_for_quicktime(self, path):
        """El titulo lo dice: Chequea que en la ruta recibida haya un archivo .mov"""
        files = os.listdir(path)
        for file in files:
            if file.endswith('.mov'):
                return file
        return None

    def explore_versions(self):
        """Abre el directorio de la version seleccionada del submenu 'Explore'"""
        if self.versions_data:
            if os.path.exists(self.versions_data['path']):
                os.chdir(self.versions_data['path'])
                subprocess.Popen('explorer .')
            else:
                QMessageBox.warning(None, u'Warning!', 'No existe la direccion')
        else:
            QMessageBox.warning(None, u'Warning!', 'No existen versiones')

    def explore_media(self):
        """Abre el directorio de la media seleccionada del submenu 'Explore'"""
        media_dir = Path(self.selected_task.first_version_path).mediaPath
        try:
            os.chdir(media_dir)
            subprocess.Popen('explorer .')
            return
        except Exception, e:
            print e
            QMessageBox.warning(None, u'Warning!', 'No existe Media')

    def explore_lowres_version(self, action):
        """Abre el directorio de la version de lowress seleccionado del submenu 'Explore'"""
        if self.lowres_versions:
            if self.lowres_versions and self.lowres_versions['dir']:
                pre_path = os.path.join(self.lowres_versions['base'], action.text())
                lowres_version_dir = os.path.normpath(pre_path)
            else:
                lowres_version_dir = self.lowres_versions['base']

            if os.path.exists(lowres_version_dir):
                os.chdir(lowres_version_dir)
                subprocess.Popen('explorer .')

            else:
                print "El path %s no existe." % lowres_version_dir
        else:
            print "No existe Lowres!"

    def explore_lowres(self):
        if self.lowres_versions:
            if os.path.exists(self.lowres_versions['base']):
                os.chdir(self.lowres_versions['base'])
                subprocess.Popen('explorer .')
                return

            print "El path %s no existe." % self.lowres_versions['base']

    def explore_fullres(self):
        """Abre el directorio del fullress seleccionado del submenu 'Explore'"""
        self.context.explore_fullres(self.selected_task)

    def showNotes(self):
        self.notes = NotesView.Show(self.selected_task, self.server)

##################################################################################

    @property
    def tasks(self):
        """Obtiene y devuelve la info (en forma de diccionario) de los planos/tareas, o assets, correspondiente al
        usuario logueado, a la vista y los filtros seleccionados"""
        if not '_tasks' in dir(self):
            project = self.ui.combo_Proyecto_Filtra.currentText()
            self._tasks = sobjects.MyTasks(self.current_tab, project, self.filters)
        return self._tasks

    @property
    def server(self):
        if not '_server' in dir(self):
            self._server = sobjects.server
        return self._server

    @property
    def selected_task(self):
        """Devuelve la tarea seleccionada (solo una)"""
        table = self.currentTable
        row = table.currentRow()
        if row > -1:
            return self.tasks[str(table.item(row, len(table.columns) - 1).text())]

    @property
    def currentTable(self):
        """Devuelve la tabla en la cual nos encontramos parados"""
        try:
            category = ['shots', 'assets'][self.ui.tabWidget.currentIndex()]
            return self.tables[category]
        except IndexError:
            pass

    def refresh(self):
        """Refresca UI junto a los datos que la conforman: Mata los threads activos hasta el momento, elimina
        las tareas con las que se trabajaba al igual que el cliente.
        En caso de estar aactiva la vista de coordinacion y no haber filtros seleccionados no carga nada esperando
        que el usuario seleccione un proyecto. En caso contrario carga los datos nuievamente"""
        while self.threads:
            thread = self.threads.pop()
            del thread

        if '_tasks' in dir(self):
            del self._tasks
        if '_clients' in dir(self):
            del self._clients
        if not self.get_all_selected_filters() and sobjects.coordinadorView == True:
            self.make_tables()
            self.makeProjectComboInCoordinatorView()
        else:
            self.turn_enabled_combos()
            self.populate_task_table()

    # def open_progress_bar(self):
    #     self.ui_progess_bar.show()

#FUNCIONES DE BOTONES INFERIORES////////////////////////////////////////////////////////////////////////////////////
    def create_file(self):
        """Dependiendo de la app en la cual se ejecute RamonLoader, este metodo llama a la creacion de carpetaje
        y/o proyectos base"""
        try:
            self.context.Create(self.selected_task)
            self.set_status_colors()
        except:
            QMessageBox.warning(None, u'No Template',  'No existe template en el proyecto para la toma')

    def create_from_file(self):
        """Dependiendo de la app en la cual se ejecute RamonLoader, crea un proyecto en base a uno ya creado"""
        #try:
        self.context.CreateFrom(self.selected_task)
        self.set_status_colors()

        #except:
        #    QMessageBox.warning(None, u'No esta implementado.', 'Espere a que sea implementado, no sea impaciente')

    def load_file(self):
        """Dependiendo de la app en la cual se ejecute RamonLoader, abre la ultima version: Por ejemplo, en Nukex
        generaria el proyhecto de la ultima version guardada"""
        if self.selected_task:
            self.context.Load(self.selected_task)
            self.sobject = self.context.get_sobject_from_path(self.context.currentFile())
            self.set_status_colors()
        else:
            QMessageBox.warning(None, u'Sin seleccion!', 'Seleccione una tarea')

    def import_file(self):
        self.context.Import(self.selected_task)
        self.set_status_colors()

    def save_file(self):
        self.context.Save(self.current_snapshot)
        self.set_status_colors()

    def show_file(self):
        self.context.Show(self.selected_task)
# // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // // //


    def make_tables(self):
        """Arma las tablas inicializando en cero la cantidad de filas y columnas, agregando los encabezados a las
         columnas y ajustando el tamanio de las celdas a los contenidos de los encabezados"""
        for category, table in self.tables.items():
            table.clear()
            table.setRowCount(0)
            table.setColumnCount(0)

            if category == 'assets':
                self.tables[category].columns = ['image', 'name', 'proyecto', 'status', 'process', 'descripcion',
                                                 'notas', 'secuencia', 'supervisor', 'asignado', 'code']

            elif category == 'shots':
                self.tables[category].columns = ['image', 'name', 'proyecto', 'status', 'process', 'descripcion',
                                                 'notas', 'secuencia', 'episodio', 'supervisor', 'asignado', 'code']

            for index, column in enumerate(self.tables[category].columns):
                table.insertColumn(index)

            table.setHorizontalHeaderLabels(self.tables[category].columns)
            table.resizeColumnsToContents()

    # AJUSTA LAS CELDAS RESPECTO AL TAMANIO DE LAS IMAGENES
    def adjustTables(self):
        """Ajusta el tamanio de las celdas co0n respecto tamanio del contenido de todas las celdas"""
        for table in self.tables.values():
            VHeader = table.verticalHeader()
            HHeader = table.horizontalHeader()
            VHeader.setMinimumSectionSize(40)
            VHeader.hide()
            HHeader.setStretchLastSection(True)
            table.resizeColumnsToContents()
            table.resizeRowsToContents()

    def populate_explorer(self):
        """No implementado aun (Hecho por cesio)"""
        self.ui.ramon_tree.setColumnCount(1)

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Title', 'Summary'])
        rootItem = model.invisibleRootItem()

        # First top-level row and children
        item0 = [QStandardItem('Title0'), QStandardItem('Summary0')]
        item00 = [QStandardItem('Title00'), QStandardItem('Summary00')]
        item01 = [QStandardItem('Title01'), QStandardItem('Summary01')]
        rootItem.appendRow(item0)
        item0[0].appendRow(item00)
        item0[0].appendRow(item01)

        # Second top-level item and its children
        item1 = [QStandardItem('Title1'), QStandardItem('Summary1')]
        item10 = [QStandardItem('Title10'), QStandardItem('Summary10')]
        item11 = [QStandardItem('Title11'), QStandardItem('Summary11')]
        item12 = [QStandardItem('Title12'), QStandardItem('Summary12')]
        rootItem.appendRow(item1)
        item1[0].appendRow(item10)
        item1[0].appendRow(item11)
        item1[0].appendRow(item12)

        # Children of item11 (third level items)
        item110 = [QStandardItem('Title110'), QStandardItem('Summary110')]
        item111 = [QStandardItem('Title111'), QStandardItem('Summary111')]
        item11[0].appendRow(item110)
        item11[0].appendRow(item111)

        self.ui.ramon_tree.setModel(model)
        # treeView.show()

        '''
        items = []
        item = QTreeWidgetItem('Hola')
        self.ui.ramon_tree.insertTopLevelItem(item)
        print item
        for i in range(10):
            items.append(QTreeWidgetItem(None, QStringList(QString("item: %1").arg(i))))
            
        self.ui.ramon_tree.insertTopLevelItems(None, items)
        '''

    def populate_task_table(self):
        """Es uno de los metodos mas importantes ya que se encarga de conectar los signals del QThread 'AddTaskRow',
         de la barra de progreso, armar y ajustar la tabla, leer filtros y llamar al comienzo de la ingesta de planos"""
        self.saved_filters_list = []
        self.filters = self.get_all_selected_filters()
        self.cleanFilterCombos()
        self.tab_index = self.ui.tabWidget.currentIndex()
        self.current_tab = self.ui.tabWidget.tabText(self.tab_index)
        self.make_tables()
        self.threads = []
        self.myTasks = AddTaskRow(self.tasks, self.tables, self.filters)
        self.myTasks.taskData.connect(self.add_task_row)
        self.myTasks.adjustTables.connect(self.adjustTables)
        # self.myTasks.progress_values.connect(self.update_progress_bar)
        self.myTasks.set_max.connect(self.set_maxim)
        self.myTasks.open_progress_bar.connect(self.show_bar)
        self.myTasks.close_progess_bar.connect(self.close_progress_bar)
        self.progress_bar_window.object.estado.setText('Cargando...')
        self.ui.setEnabled(False)
        self.myTasks.start()

    def get_all_selected_filters(self):
        """Recolecta todos los filtros y devuelve un diccionario con ellos"""
        filters = {}
        for combo in comboBox_analog_column:
            widget = getattr(self.ui, combo)
            filter = widget.currentText()
            if filter:
                filters[combo] = filter
        return filters


    def populate_app_context(self):
        """CREA EL COMBO SUPERIOR DE app, LO LLENA DE ITEMS Y AGREGA FUNCIONALIDAD"""
        self.ui.app_context_combo.clear()
        self.ui.app_context_combo.addItems(list(context.listApps()))
        self.ui.app_context_combo.currentIndexChanged.connect(self.setContext)

        if self.context:
            context_name = self.context.__name__.split('.')[-1]
            index = self.ui.app_context_combo.findText(context_name)
            self.ui.app_context_combo.setCurrentIndex(index)

    def setContext(self, index):
        appName = self.ui.app_context_combo.itemText(index)
        self.context = context.app(appName)

    # def populate_status_context(self):
    #     self.table.clearSelection

    # ACA AGREGUE GRAFICAS, NUEVAMENTE ABAJO Y EN SOBJECT.PY Nacho
    def add_task_row(self, rawdata, progress):
        """Otro metodo de los mas importantes:
        -Este es llamado por el signal de 'AddTaskRow()'. Recibe la data() con el plano administrado y completa
        la tabla en base a esa data()
        -identifica a que tabla corresponde el plano a cargar
        .En caso de encontrarse la vista de coordinacion activa ,cargara solo los combos de informacion o las
        tablas segun corresponda"""
        if 'task' in rawdata:
            task = rawdata.pop('task')
            if task.search_code.startswith('PLANOS'):
                table = self.tables['shots']
            elif task.search_code.startswith('ASSETS_3D'):
                table = self.tables['assets']
            elif task.search_code.startswith('MATTE_PAINTING'):
                table = self.tables['assets']
            elif task.search_code.startswith('CONCEPTS'):
                table = self.tables['assets']
            elif task.search_code.startswith('GRAFICAS'):
                table = self.tables['assets']
            else:
                return

            self.cargar(table, rawdata, progress)

    def cargar(self, table, rawdata, progress):
        """Se encarga de ir completando la tabla de datos segun el plano administrado"""
        if rawdata:
            row = table.rowCount()
            table.insertRow(row)

            for index, data in enumerate(rawdata.items()):
                key, value = data
                self.putInfoToCombos(key, value)
                column = table.columns.index(key)

                if key == 'image':
                    func = partial(self.LoadImagetoTable, table, column, row)
                    image = LoadImageFromUrl(value.get('value'), 60, 40)
                    image.recibeImage.connect(func)
                    image.start()
                    self.threads.append(image)
                    continue

                self.putInfoToCombos(key, value)
                self.update_progress_bar(progress + 1)
                item = QTableWidgetItem()
                item.setText(unicode(value.get('value')))
                table.setItem(row, column, item)
                # if key == 'code':
                #     table.setColumnWidth(1) #Modificar el tamanio de la columna code
                # print 'cargado: ', value.get('value')
            self.set_status_colors(rawdata['name']['value'])

    def putInfoToCombos(self, key, value):
        """Identifica a que combo debe agregar info"""
        if key == 'secuencia':
            self.getIntoCombo(value, self.ui.combo_Escena_Filtra)
        elif key == 'proyecto':# and sobjects.coordinadorView == False:
            self.getIntoCombo(value, self.ui.combo_Proyecto_Filtra)
        elif key == 'episodio':
            self.getIntoCombo(value, self.ui.combo_Episodio_Filtra)
        elif key == 'asignado':
            self.getIntoCombo(value, self.ui.combo_Asignado_Filtra)
        elif key == 'status':
            self.getIntoCombo(value, self.ui.combo_Status_Filt)
        elif key == 'supervisor':
            self.getIntoCombo(value, self.ui.combo_Supervisor_Filt)

    def getIntoCombo(self, value, combo):
        """Agrega la info al comboBox especificado"""
        filtro = str(value['value'])
        index = combo.findText(filtro)
        if index >= 0:
            if filtro in self.saved_filters_list:
                combo.setCurrentIndex(combo.count()-1)
        else:
            combo.addItem(value['value'])
            combo.setSizeAdjustPolicy(combo.AdjustToContents)

    def LoadImagetoTable(self, table, column, row, bitmap):
        try:
            if bitmap:
                image = QLabel()
                image.setScaledContents(True)
                pixmap = QPixmap()
                pixmap.loadFromData(bitmap)
                image.bitmap = pixmap
                image.setPixmap(pixmap.scaled(60, 40))
                table.setCellWidget(row, column, image)
                table.setRowHeight(row, 40)

        except:
            item = QTableWidgetItem()
            item.setText('No Image')
            table.setItem(row, column, item)

    def set_status_colors(self, name=None):
        if not name and self.selected_task:
            name = self.selected_task.code

        table = self.currentTable
        if table:
            column = table.columns.index('name')
            for item in table.findItems(name, Qt.MatchExactly):
                if item.row() == column and name == item.text():
                    status = self.get_status()
                    if status == 'Actualizado':
                        item.setForeground(QBrush(QColor(0, 150, 0)))
                    elif status == 'Sin version':
                        item.setForeground(QBrush(QColor(150, 0, 0)))
                    else:
                        item.setForeground(QBrush(QColor(150, 150, 0)))
                else:
                    item.setForeground(QBrush(QColor(150, 150, 150)))
            table.clearSelection()
            # -----------------------------------------------------------------------------------

    @property
    def current_snapshot(self):
        if os.path.isfile(self.context.currentFile()):
            local_md5 = get_md5(self.context.currentFile())

            for snapshot in self.sobject.snapshots:
                if snapshot.is_current:
                    return snapshot

    def get_status(self):
        try:
            if os.path.isfile(self.context.currentFile()):
                local_md5 = get_md5(self.context.currentFile())
                if self.sobject:
                    for snapshot in self.sobject.snapshots:
                        if local_md5 == snapshot.main_md5:
                            if snapshot.is_current:
                                return 'Actualizado'
                            else:
                                return snapshot.version
            return 'Sin Version'

        except AttributeError:
            return "Sin version"

class NoTemplate(Exception):
    pass

if __name__ == "__main__":
    with GetApp():
        app = context.app()
        form = AutoLoader(app)
        form.show()

