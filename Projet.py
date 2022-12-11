#----------------------------------------------------------------------------------------------------------------------------------------------------------
# Created by : HUOT-MARCHAND Antoine
# Modified by : MARTINS Naimé, GENOUD-DUVILLARET Benoît
# Last-modification : 11/12/2022
# Version : 2.0
#----------------------------------------------------------------------------------------------------------------------------------------------------------
# Drawing application for autonomous cars machine learning.
#----------------------------------------------------------------------------------------------------------------------------------------------------------


import sys
import math
import os
import numpy as np

from PyQt5.QtCore import Qt, QSize, QRect, QPoint
from PyQt5.QtGui import QPainter, QPen, QPixmap, QImage, QColor, QCursor
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout, QDesktopWidget, QCheckBox
from pyqt5_tools.examples.exampleqmlitem import QtCore
from skimage import morphology, color, io
from qimage2ndarray import array2qimage


# fr : La classe Canvas a été créée afin de constituer un espace de dessin customisable.
# en : The Canvas class was created to provide a customizable drawing space.
class Canvas(QLabel):
    
    if (os.path.exists("points.txt")) : os.remove("points.txt")
    if (os.path.exists("dilatedN&BCircuitMIA.png")) : os.remove("dilatedN&BCircuitMIA.png")
    
    
    def __init__(self):
        QWidget.__init__(self)
        # fr : pixmap est un format de fichier graphique. On initialise ici le fond de notre canvas avec l'image du
        # circuit "circuitMIA.png". Il est donc possible de changer le fond avec vos propres images.
        # en : pixmap is a graphics file format. Here we initialize the background of our canvas with the image of
        # the circuit "circuitMIA.png". It is therefore possible to change the background with your own images.
        self.my_pixmap = QPixmap("circuitMIA.png")
        
        # fr :  Les objets QPixmaps peuvent être convertit en objets QImages. Ces objets QImages sont très utiles
        # pour récupérer des informations concernants des images.
        # en : QPixmaps objects can be converted into QImages objects. These QImages objects are very useful
        # to retrieve information about images.
        self.my_qimage = QPixmap.toImage(self.my_pixmap)
        
        # fr : On met la dilatation des bords du circuit à 10.
        # En : We set the dilation of the edges of the circuit to 10.
        self.dilation = 10
        # fr : On convertit notre image de départ en une image noir et blanc dont les bords du circuit on été dilatés
        # en : We convert our starting image to a grayscale image with dilated borders 
        self.my_dilatedimage = morphology.erosion(io.imread('circuitMIA.png', as_gray = True), morphology.disk(self.dilation))
        self.my_dilatedimage = np.where(self.my_dilatedimage>=0.5, 1, 0)
        # fr : On sauvegarde le circuit dilaté noir et blanc.
        # en : The dilated black and white circuit is saved.
        io.imsave('dilatedN&BCircuitMIA.png',self.my_dilatedimage)
        self.my_qdilatedimage = array2qimage(self.my_dilatedimage)
        
        self.setPixmap(self.my_pixmap)
        # fr : PreviousPoint est la variable dans laquelle on va stocker les coordonnées du précédent point acquis
        # lors du tracé de la trajectoire.
        # en : PreviousPoint is the variable in which we will store the coordinates of the previous point acquired
        # when tracing the trajectory.
        self.previousPoint = None
        # fr : On initialise la variable color avec du noir. Celle-ci servira à définir la couleur du tracé.
        # en : We initialize the color variable with black. This will be used to define the color of the plot.
        self.color = Qt.black
        # fr : La variable isDrawing permet de savoir si le dessin est en cours ou en attente. Lorsqu'il est en cours la
        # variable est à 1 sinon elle est à 0.
        # en : The isDrawing variable lets you know if the drawing is in progress or pending. When it is in progress
        # the variable is at 1 otherwise it is at 0.
        self.isDrawing = 0
        self.isDrawingStarted = False
        # fr : Permet d'activer le traqueur de la souris.
        # en : Enables the mouse tracker.
        self.setMouseTracking(True)
        # fr : On initialise une intervalle de 30 points. Cela permettra de réaliser les mesures tous les 30 points.
        # en : We initialize an interval of 30 points. This will allow measurements to be taken every 30 points.
        self.point_interval = 30
        # fr : La variable current_interval est une sorte de compteur permettant de savoir à quel point de l'intervalle
        # nous sommes. On l'initialise à 29 de façon à ce que le premier point du tracé soit pris en compte.
        # en : The current_interval variable is a kind of counter to know at what point of the interval we are. It is
        # initialized to 29 so that the first point of the plot is taken into account.
        self.current_interval = 29
        # fr : Le rapport de distance écran-réel est d'environ 100 pixels/m.
        # en : The screen-to-real distance ratio is about 100 pixels/m.
        self.distance_ratio = 100
        # fr : Variable contenant la distance entre deux points mesurés.
        # en : Variable containing the distance between two measured points.
        self.current_distance = 0
        # fr : Variable contenant la distance entre deux points mesurés selon l'axe des x.
        # en : Variable containing the distance between two points measured along the x axis.
        self.current_distance_x = 0
        # fr : Variable contenant la distance entre deux points mesurés selon l'axe des y.
        # en : Variable containing the distance between two points measured along the y axis.
        self.current_distance_y = 0
        
        
        # fr : Variable contenant la position de départ de la voiture selon l'axe des x.
        # en : Variable containing the starting position of the car along the x axis.
        self.start_x = 0
        # fr : Variable contenant la position de départ de la voiture selon l'axe des y.
        # en : Variable containing the starting position of the car along the y axis.
        self.start_y = 0
        # fr : Variable contenant l'angle de départ de la voiture selon l'axe des abscisses.
        # en : Variable containing the departure angle of the car along the abscissa axis.
        self.start_angle = 0

        # fr : entraxe correspondant à l'empattement (ou entraxe) de la voiture. C'est à dire la distance entre les
        # roues arrières et avants de la voiture.
        # en : center distance corresponding to the wheelbase (or center distance) of the car. That is to say the
        # distance between the rear and front wheels of the car.
        self.entraxe = 0.3355
        # fr : xpos est un tableau qui va contenir les positions selon l'axe des x de tous les points acquis.
        # en : xpos is an array that will contain the positions along the x axis of all acquired points.
        self.xpos = np.empty(0)
        # fr : ypos est un tableau qui va contenir les positions selon l'axe des y de tous les points acquis.
        # en : ypos is an array that will contain the positions along the y axis of all acquired points.
        self.ypos = np.empty(0)
        # fr : speed est un tableau qui va contenir les différentes vitesses à utiliser pour chaque commande donnée à la
        # voiture.
        # en : speed is an array that will contain the different speeds to use for each command given to the car.
        self.speed = np.empty(0)
        # fr : La variable change permet de changer l'état du painter (mode dessiner/effacer). Cette fonction n'est
        # néanmoins pas encore bien implémentée.
        # en : The variable change allows to change the state of the painter (draw/erase mode). However,
        # this function is not yet well implemented.
        self.change = 0
        # fr : all_points est un tableau qui va contenir tous les points du tracé.
        # en : all_points is an array that will contain all the points of drawing.
        self.all_points = np.empty(0)
        # fr : Dernier point tracé
        # en : Last point traced
        self.very_last_point = QPoint(-1,-1)
        
        # fr : on cree un compteur qui permet de garder une trace du nombre de fichier trajectoire et points nous
        # avons cree.
        # en : we create a counter that keeps track of the number of trajectory files and points we have created.
        self.compteur = 0
        
        self.afficheur= -1
        
        # fr : indique si un tracé est valide, i.e si on a pas touché les bords du canvas.
        # en : indicates if a drawing is valid, i.e if we have not touched the edges of the canvas.
        self.valid_circuit = False

    
    # fr : méthode permettant de calculer la courbure c selon la position de tous les points mesurés.
    # en : method to calculate the curvature c according to the position of all the measured points.
    def calcul_curvature(self, x_value, y_value):
        # fr : On calcule ici les valeurs du tableau x_t, dont les éléments correspondent aux dérivés premières des
        # éléments du tableau xvalue passé en paramètre.
        # en : Here we calculate the values of the array x_t, whose elements correspond to the first derivatives of
        # the elements of the array xvalue passed as a parameter.
        x_t = np.gradient(x_value)
        # fr : On calcule ici les valeurs du tableau y_t, dont les éléments correspondent aux dérivés premières des
        # éléments du tableau yvalue passé en paramètre.
        # en : Here we calculate the values of the array y_t, whose elements correspond to the first derivatives of
        # the elements of the array yvalue passed as a parameter.
        y_t = np.gradient(y_value)
        # fr : On calcule ici les valeurs du tableau xx_t, dont les éléments correspondent aux dérivés secondes des
        # éléments du tableau xvalue passé en paramètre et donc aux dérivés premières des éléments de x_t calculé
        # précédemment.
        # en : Here we calculate the values of the xx_t array, whose elements correspond to the second derivatives of
        # the elements of the xvalue array passed as a parameter and therefore to the first derivatives of the
        # elements of x_t calculated previously.
        xx_t = np.gradient(x_t)
        # fr : On calcule ici les valeurs du tableau yy_t, dont les éléments correspondent aux dérivés secondes des
        # éléments du tableau yvalue passé en paramètre et donc aux dérivés premières des éléments de y_t calculé
        # précédemment.
        # en : Here we calculate the values of the yy_t array, whose elements correspond to the second derivatives of
        # the elements of the xvalue array passed as a parameter and therefore to the first derivatives of the
        # elements of y_t calculated previously.
        yy_t = np.gradient(y_t)

        # fr : On calcule ici les valeurs du tableau speed à l'aide des tableaux x_t et y_t calculés auparavant.
        # en : We calculate here the values of the speed array using the x_t and y_t arrays calculated before.
        self.speed = np.sqrt(x_t * x_t + y_t * y_t)

        # fr : On calcule ici les valeurs du tableau curvature_val qui correspond à la courbure c en tout point
        # mesurés.
        # en : We calculate here the values of the table curvature_val which corresponds to the curvature c
        # at all measured points.
        curvature_val = (xx_t * y_t - x_t * yy_t) / self.speed ** 3

        return curvature_val


    # fr : La méthode curv_to_angle permet de calculer l'angle de braquage nécessaire pour commander les angles auxquels
    # les roues de la voiture devront tourner à chaque commande.
    # en : The curv_to_angle method is used to calculate the steering angle needed to command the angles at which the
    # wheels of the car will have to turn with each command.
    def curv_to_angle(self, c):
        # fr : En effet, angle = arctan(L/R). Or R = 1/c donc angle = arctan(L*c)
        # en : Indeed, angle = arctan(L/R). But R = 1/c so angle = arctan(L*c)
        if -1 < self.entraxe * c < 1:
            return math.atan(self.entraxe * c)


    def diff(self, a, b):
        return b - a


    # fr : Cette méthode permet de calculer le coefficient directeur d'une droite défnie par deux points.
    # en : This method makes it possible to calculate the directing coefficient of a straight line defined by two
    # points.
    def calculateCoefficent(self, xA, yA, xB, yB):
        # fr : Par rapport à la formule d'origine, yA et yB sont inversés puisque le repère est tel que l'axe y pointe
        # vers le bas.
        # en : Compared to the original formula, yA and yB are reversed since the mark is such that the y axis points
        # down.
        if xA != xB:
            coeff = (yA - yB) / (xB - xA)
        else:
            coeff = 0
        return coeff
    
    
    # fr : La méthode validate_circuit est appelée lorsque l'utilisateur a fini de tracer la trajectoire voulue et
    # clique sur le bouton "VALID CIRCUIT". On génère alors le fichier de commande adapté.
    # en : The validate_circuit method is called when the user has finished tracing the desired trajectory and clicks
    # on the "VALID CIRCUIT" button. One then generates the adapted command file.
    def validate_circuit(self):
        
        if(self.valid_circuit) :
            # fr : On augmente le compteur de fichier "trajectoires.txt"
            # en : We increase the "trajectories.txt" file counter
            self.compteur +=1

            nom_fichier_trajectoire= "trajectoire"+str(self.compteur)+".txt"
            nom_fichier_points = "points"+str(self.compteur)+".txt"
            # fr : si le fichier existe déjà, on le supprime, sinon on le cree et et le cureur est placé à la fin
            # du fichier.
            # en : if the file already exists, we delete it, otherwise we create it and the cursor is
            # placed at the end of the file.
            if (os.path.exists(nom_fichier_trajectoire)) : os.remove(nom_fichier_trajectoire)
            self.fichier = open(nom_fichier_trajectoire, "a")
            
            # fr : On efface alors les précédentes commande et replace le curseur au début du fichier.
            # en : The previous commands are then erased and the cursor is replaced at the beginning of the file.
            self.fichier.truncate(0)
            self.fichier.seek(0)

            # fr : on calcule alors le tableau des courbures pour chaque point mesuré. (appel à calcul_curvature).
            # en : the array of curvatures is then calculated for each point measured. (call to calcul_curvature).
            curvature_array = self.calcul_curvature(self.xpos, self.ypos)
            # print("curvature array \n", curvature_array)

            # fr : On construit le tableaux des angles à appliquer. (appel à curv_to_angle).
            # en : We build the table of angles to apply. (call to curv_to_angle).
            angle_array = np.array([self.curv_to_angle(xi) for xi in curvature_array])
            # print("angle array : \n", angle_array)

            # fr : On calcule ici les 3 coefficients directeur des trois premières droites traçables.
            # en : We calculate here the 3 directing coefficients of the first three traceable lines.
            coeffd1 = self.calculateCoefficent(self.start_x, self.start_y, self.xpos[1], self.ypos[1])
            coeffd2 = self.calculateCoefficent(self.start_x, self.start_y, self.xpos[2], self.ypos[2])
            coeffd3 = self.calculateCoefficent(self.xpos[1], self.ypos[1], self.xpos[2], self.ypos[2])

            # fr : Puis on calcule le coefficient moyen pour minimiser l'incertitude.
            # en : Then the average coefficient is calculated to minimize the uncertainty.
            coeff_moyen = (coeffd1 + coeffd2 + coeffd3) / 3

            # fr : on calcule ici l'angle d'orientation de départ de la voiture. Pour plus de précision (section III.2 du
            # rapport).
            # en : here we calculate the starting orientation angle of the car. For more details (section III.2 of the
            # report).
            if self.diff(self.start_x, self.xpos[1]) > 0:
                self.start_angle = math.atan(coeff_moyen)
            else:
                self.start_angle = math.pi + math.atan(coeff_moyen)

            # fr : Calcul de la position de départ selon y (différence à cause du changement de repère entre l'interface
            # et le logiciel de simulation).
            # en : Calculation of the starting position according to y (difference due to the change of frame between the
            # interface and the simulation software).
            self.start_y = 4.67 - self.start_y

            # fr : Écriture de la première ligne de commande (initialisation de la position de la voiture).
            # en : Writing the first command line (initializing the position of the car).
            self.fichier.write("{0:.3f}".format(self.start_x))
            self.fichier.write(",{0:.3f}".format(self.start_y))
            self.fichier.write(",{0:.8f}\n".format(self.start_angle))

            # fr : Écriture des lignes de commande suivantes (avec une précision assez grande car impact important).
            # en : Writing of the following command lines (with a rather high precision because significant impact).
            for i in range(0, len(self.speed)):
                self.fichier.write("{0:.8f}".format(self.speed[i]) 
                                   + ",{0:.8f}\n".format(angle_array[i]))
            self.fichier.close()
            

            # fr : On ecrit l'ensemble des points du tracé dans le fichier points.txt.
            # en : We write all the points of the plot in the file points.txt.
            if (os.path.exists(nom_fichier_points)) : os.remove(nom_fichier_points)
            self.fichier_point = open(nom_fichier_points,"a")
            for i in range(0, len(self.all_points) - 2):
                self.fichier_point.write(str(self.all_points[i].x())
                                        +","
                                        +str(self.all_points[i].y())
                                        +"\n")
            self.fichier_point.write(str(self.all_points[len(self.all_points) - 1].x()) + "," 
                                     + str(self.all_points[len(self.all_points) - 1].y()))
            self.fichier_point.close()
            
            # fr : On reinitialise les variable previousPoint et all_points.
            # en : We reset the previousPoint and all_points variables.
            self.previousPoint = None
            self.all_points= np.empty(0)
       
    
    # fr : La méthode clear_circuit, permet d'effacer le précédent tracé et de réinitialiser les différents paramètres
    # permettant de construire le fichier de commande.
    # en : The clear_circuit method makes it possible to erase the preceding layout and to reinitialize the various
    # parameters making it possible to build the command file.
    def clear_circuit(self):
        # fr : Ici on réinitialise l'image de fond du Canvas avec la même image du circuit qu'à l'origine. Cela permet
        # aussi d'effacer les différents tracés par la même occasion.
        # en : Here we reset the background image of the Canvas with the same image of the circuit as originally.
        # This also makes it possible to erase the different traces at the same time.
        self.my_pixmap = QPixmap("circuitMIA.png")
        self.setPixmap(self.my_pixmap)
        self.update()

        # fr : Les tableaux contenant la posiition des points acquis et la vitesse sont donc vidés.
        # en : The tables containing the position of the acquired points and the speed are therefore emptied.
        self.xpos = np.empty(0)
        self.ypos = np.empty(0)
        self.speed = np.empty(0)

        # fr : Étant donné qu'un nouveau tracé sera effectué, le point précédemment acquis est remis à None.
        # On réinitialise tous les points du tracé effectué (pour ne pas influencer les tracés suivants).
        # en : Since a new plot will be made, the previously acquired point is reset to None. 
        # We reset all the points of the plot made (so as not to influence the following plots).
        self.previousPoint = None
        self.all_points = np.empty(0)
        self.very_last_point = QPoint(-1,-1)
         
         
    # fr : méthode servant à modifier la variable color avec la couleur passée en argument.
    # en : method used to modify the color variable with the color passed as an argument.
    def set_pen_color(self, c):
        self.color = QColor(c)


    # TODO fr : la méthode suivant est encore en cours d'écriture et ne fonctionne pas de la bonne manière à ce jour.
    # fr : Méthode permettant de changer l'état du painter (mode dessiner/effacer).
    # TODO en : the following method is still being written and does not work well so far.
    # en : Method to change the state of the painter (draw/erase mode).
    def changeEraseMode(self):
        # fr : Si le mode actuel est "dessiner", le mode devient "effacer" et inversement.
        # en : If the current mode is "draw", the mode becomes "erase" and vice versa.
        if(self.change != 1) :
            self.change = 1
        else :
            self.change = 0
            
        if (self.change == 1) :
            pixmap = self.pixmap()
            pixmap.fill(QtCore.Qt.transparent)
            painter = QPainter(pixmap)
            painter.setPen(QPen(QtCore.Qt.black, 2))
            painter.drawRect(pixmap.rect())
            painter.end()
            # cursor = QCursor(pixmap)
            # QApplication.setOverrideCursor(cursor)
        else:
            QApplication.restoreOverrideCursor()

        
    # fr : Méthode qui permet de retracer un trajectoires bien précise.
    # en : Method that allows to retrace a precise trajectory.
    def loadChosenTrajectory(self,index):
        
        # fr : On active le painter pour retracer la dernière trajectoire validée.
        # en : We active the painter to redraw the last valid trajectory.
        painter = QPainter(self.pixmap())
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(self.color)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)

        painter.begin(self)

        # fr : On récupère le contenu du fichier point.txt 
        # en : We retrieve the content of the point.txt file
        with open("points"+str(index+1)+".txt", "r") as f:
            data = f.read()

        # fr : On récupère les couples de coordonnées de la trajectoire
        # en : We retrieve the coordinate pairs of the trajectory
        line = data.split('\n')

        # fr : On retrace la trajectoire à l'aide de ses points.
        # en : We redraw the last trajectory with his points.
        for i in range(2, len(line) -2):
            couple1 = line[i].split(",")
            couple2 = line[i+1].split(",")
            pt1 = QPoint(int(couple1[0]), int(couple1[1]))
            pt2 = QPoint(int(couple2[0]), int(couple2[1]))

            painter.drawLine(pt1, pt2)

            self.update()

        painter.end()

        # fr : On vide le tableau all_points pour les prochains tracés.
        # en : We empty the all_points array for the next plots.
        self.all_points = np.empty(0)
        
        
    # fr : Méthode qui permet de retracer la dernière trajectoire validée.
    # en : Method that allows to retrace the last validated trajectory.
    def loadLastTrajectory(self):
        if(self.compteur != 0) :
            return self.loadChosenTrajectory(self.compteur-1)
    

    # fr : Méthode qui permet de retracer la dernière trajectoire validée.
    # en : Method that allows to retrace the last validated trajectory.
    def deleteTrajectory(self, index):        
        # fr : on supprime le fichier qui correspond a la trajectoire d indice index
        # et le fichier point correspondant
        # en : we delete the file corresponding to the trajectory of index index
        # and the corresponding point file
        os.remove("trajectoire"+str(index+1)+".txt")
        os.remove("points"+str(index+1)+".txt") 
        self.compteur -= 1


    # fr : L'événement mousePressEvent : Lorsqu'on maintient le clic sur la souris, le dessin est actif.
    # en : The mousePressEvent : When the mouse click is held down, the drawing is active.
    def mousePressEvent(self, event):
        self.isDrawing = 1
        
        # fr : Si un tracé a déjà été commencé
        if(self.very_last_point != QPoint(-1,-1)) : 
            self.cursor().setPos(self.mapToGlobal(self.very_last_point))
        

    # fr : L'événement mouseReleaseEvent : Lorsqu'on relache le clic de la souris, le dessin est en pause.
    # en : The mouseReleaseEvent : When the mouse click is released, the drawing is paused.
    def mouseReleaseEvent(self, event):
        self.isDrawing = 0
        self.setCursor(QCursor(Qt.ArrowCursor))
        self.very_last_point = event.pos()


    # fr : L'événement mouseMoveEvent : Lorsque le dessin est actif et que l'on bouge la souris, on effectue le tracé de
    # la trajectoire et on récolte des données..
    # en : The mouseMoveEvent : When the drawing is active and the mouse is moved, the trajectory is drawn and data
    # is collected.
    def mouseMoveEvent(self, event):
        # fr : On initialise les différents parmètres nécessaires au dessin (comme la couleur, l'épaisseur etc...).
        # en : We initialize the different parameters necessary for the drawing (such as the color, the thickness,
        # etc.).
        painter = QPainter(self.pixmap())
        pen = QPen()
        pen.setWidth(3)
        pen.setColor(self.color)
        pen.setStyle(Qt.SolidLine)
        painter.setPen(pen)

        # fr : Si le dessin est actif
        # en : if drawing is active
        if self.isDrawing == 1:
            self.setCursor(QCursor(Qt.CrossCursor))
            # fr : Si c'est le début du dessin (premier point à tracer).
            # en : if it is the beginning of the drawing (first point to draw);
            if self.previousPoint is None:
                # fr : On initialise la position de départ.
                # en : We initialize the starting position;
                self.start_x = event.x() / self.distance_ratio
                self.start_y = event.y() / self.distance_ratio
                #print("start_x :", self.start_x)
                #print("start_y :", self.start_y)
                # fr : le point de départ devient à présent le dernier point tracé.
                # en : the starting point now becomes the last point plotted.
                self.previousPoint = event.pos()
                
                self.valid_circuit = True
                
                return
            
            
            # fr : Si la couleur du terrain sous le tracé est la même que la couleur
            # du terrain au point de départ et que nous sommes en train de dessiner :
            # en : If the color of the land under the plot is the same as the color
             # of the terrain at the starting point and that we are drawing:
            if (self.my_qdilatedimage.pixel(event.pos()) == self.my_qdilatedimage.pixel(QPoint(self.start_x * self.distance_ratio, self.start_y * self.distance_ratio))) :
                
                
                # fr : On active le "painter" permettant le tracé.
                # en : We activate the "painter" allowing the drawing.
                if not painter.isActive():
                    painter.begin(self)

                # fr : On enregistre tous les points du tracé
                # en : We save all the drawing points.
                self.all_points = np.append(self.all_points, event.pos())
                
                # fr : On trace la droite entre le nouveau point acquis et le précédent.
                # en : The line is drawn between the new acquired point and the previous one.
                painter.drawLine(self.previousPoint, event.pos())
                painter.end()

                self.update()

                # fr : les distances en x et y sont incrémentés à chaque nouveau point mesuré.
                # en : the distances in x and y are incremented with each new measured point.
                self.current_distance_x += (event.x() - self.previousPoint.x()) / self.distance_ratio
                self.current_distance_y += (event.y() - self.previousPoint.y()) / self.distance_ratio

                # fr : Le point actuel devient notre dernier point tracé.
                # en : The current point becomes our last plotted point.
                self.previousPoint = event.pos()

                # fr : Notre intervalle courante augmente de 1 car on vient de mesurer un point de plus.
                # en : Our current interval increases by 1 because we have just measured one more point.
                self.current_interval += 1

                # fr : Si on a mesuré autant de points que l'intervalle voulue (30).
                # en : If we have measured as many points as the desired interval (30).
                if self.current_interval == self.point_interval:
                    # fr : On calcule la distance linéaire entre le premier et le dernier point de l'intervalle.
                    # en : We calculate the linear distance between the first and the last point of the interval.
                    self.current_distance = math.hypot(self.current_distance_x, self.current_distance_y)

                    # fr : La position du dernier point tracé est alors ajouté aux tableaux xpos et ypos.
                    # en : The position of the last plotted point is then added to the xpos and ypos arrays.
                    xB = event.x() / self.distance_ratio
                    yB = event.y() / self.distance_ratio
                    #print("xB = ", xB, " and yB = ", yB)
                    self.xpos = np.append(self.xpos, xB)
                    self.ypos = np.append(self.ypos, yB)

                    # fr : L'intervalle courante et les distances calculés sont alors remis à 0 afin de reparcourir une
                    # nouvelle intervalle de points.
                    # en : The current interval and the calculated distances are then reset to 0 in order to cover a new
                    # interval of points.
                    self.current_interval = 0
                    self.current_distance = 0
                    self.current_distance_x = 0
                    self.current_distance_y = 0
            
            # fr : Si la couleur du terrain sous le tracé n'est pas la même que la couleur
            # du terrain au point de départ ou que nous ne sommes pas en train de dessiner :
            # en : If the color of the terrain under the plot is not the same as the color
            # of the terrain at the starting point or that we are not drawing:
            else :
                self.isDrawing = 0
                # fr : On supprime l'objet painter afin de pouvoir réinitialiser le tracer
                # en: We delete the painter object in order to be able to reset the plotter
                #del painter
                # fr : On reinitialise le circuit : on efface tous les tracers présents.
                # en: We reset the circuit: we erase all the traces present.
                #self.clear_circuit()
                
                # fr : The circuit becomes invalid
                self.valid_circuit = False
                



# fr : Palette de couleurs avec les codes hexadécimaux associés.
# en : Color palette with associated hexadecimal codes.
COLORS = [
    # 17 undertones https://lospec.com/palette-list/17undertones
    '#000000', '#141923', '#414168', '#3a7fa7', '#35e3e3', '#8fd970', '#5ebb49',
    '#458352', '#dcd37b', '#fffee5', '#ffd035', '#cc9245', '#a15c3e', '#a42f3b',
    '#f45b7a', '#c24998', '#81588d', '#bcb0c2',
]



# fr : Classe permettant de définir la forme et les attributs des boutons servant à modifier la couleur du tracé.
# en : Class used to define the shape and attributes of the buttons used to modify the color of the plot.
class QPaletteButton(QPushButton):

    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QSize(24, 24))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color)
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))



# fr : Classe permettant de définir la forme et les attributs des différents boutons actionneurs.
# en : Class used to define the shape and attributes of the different action buttons.
class QButton(QPushButton):

    def __init__(self, color, text):
        super().__init__()
        self.setFixedSize(QSize(200, 30))
        self.setText(text)
        self.color = color
        self.setStyleSheet("QPushButton::hover{background-color: orange; border-style: outset; border-radius: 10px ;}"
                           "QPushButton{background-color: white; border-style: outset; border-radius: 10px ;}")
        self.setCursor(QCursor(QtCore.Qt.PointingHandCursor))



# fr : Classe MainWindow englobant les différents objets crés jusqu'ici.
# en : MainWindow class encompassing the various objects created so far.
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # fr : Titre de la fenêtre à adapter selon votre choix.
        # en : Title of the window to be adapted according to your choice.
        self.setWindowTitle("Circuit d'apprentissage pour véhicule autonome")
        self.setStyleSheet("background-color: purple;")

        # fr : Création du Canvas
        # en : Canvas' creation
        self.canvas = Canvas()

        # fr : Ajout et affichage du canvas dans la fenêtre principale.
        # en : Adding and displaying the canvas in the main window.
        widget = QWidget()
        self.layout = QVBoxLayout()
        widget.setLayout(self.layout)
        self.canvas_box = QHBoxLayout()
        self.canvas_box.addWidget(self.canvas)
        self.layout.addLayout(self.canvas_box)
        
        # fr : Creation de l'interface du choix de l'affichage des courbes
        # en : Creation of the interface for choosing the display of curves
        self.checkBoxs = QHBoxLayout()
        self.canvas_box.addLayout(self.checkBoxs)        
        self.listCheckBox=[]
        self.numero = []    
        self.courbes = QGridLayout()                 
        self.button_delete = QButton("#000000","Delete")

        # fr : Ajout et affichage de la palette de couleurs dans la fenêtre principale.
        # en : Added and displayed the color palette in the main window.
        palette = QHBoxLayout()
        self.add_palette_buttons(palette)
        self.layout.addLayout(palette)

        actions = QHBoxLayout()
        actions.setAlignment(Qt.AlignCenter)

        # fr : Ajout et affichage du bouton "CLEAR CIRCUIT" dans la fenêtre principale.
        # en : Addition and display of the "CLEAR CIRCUIT" button in the main window.
        clearButton = QButton("#000000", "CLEAR CIRCUIT")
        # fr : La méthode clear_circuit est appelée à chaque clic sur le bouton en question.
        # en : The clear_circuit method is called each time the button in question is clicked.
        clearButton.clicked.connect(self.canvas.clear_circuit)
        clearButton.clicked.connect(self.uncochedcheckBox)

        self.add_action_buttons(clearButton, actions)

        # fr : Ajout et affichage du bouton "VALID CIRCUIT" dans la fenêtre principale.
        # en : Addition and display of the "VALID CIRCUIT" button in the main window.
        validButton = QButton("#000000", "VALID CIRCUIT")
        # fr : La méthode validate_circuit est appelée à chaque clic sur le bouton en question.
        # en : The validate_circuit method is called each time the button in question is clicked.
        validButton.clicked.connect(self.canvas.validate_circuit)
        validButton.clicked.connect(self.addcheckBox)

        self.add_action_buttons(validButton, actions)

        # fr : Ajout et affichage du bouton "LOAD LAST TRAJECTORY" dans la fenêtre principale.
        # en : Addition and display of the "LOAD LAST TRAJECTORY" button in the main window.
        loadingButton = QButton("#000000", "LOAD LAST TRAJECTORY")
        # fr : La méthode loadLastTrajectory est appelée à chaque clic sur le bouton en question.
        # en : The loadLastTrajectory method is called each time the button in question is clicked.
        loadingButton.clicked.connect(self.canvas.loadLastTrajectory)

        self.add_action_buttons(loadingButton, actions)

        # TODO fr : le bouton suivant est encore en cours d'écriture et ne fonctionne pas de la bonne manière à ce jour.
        # TODO en : the following button is still being written and not working the right way so far.
        """eraseButton = QButton("#000000", "ACTIVE/DESACTIVE ERASER")
        eraseButton.clicked.connect(self.canvas.changeEraseMode)
        layout.addWidget(eraseButton)"""

        self.layout.addLayout(actions)
        self.setCentralWidget(widget)
        
        self.setGeometry(0,0,1300,480)
        self.geometry()
        
        qtRectangle = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())


    # fr : Méthode permettant de définir l'action des boutons de la palette de couleur.
    # en : Method to define the action of the buttons of the color palette.
    def add_palette_buttons(self, layout):
        
        for c in COLORS:
            b = QPaletteButton(c)
            # fr : La méthode set_pen_color est appelée à chaque clic sur le bouton en question.
            # en : The set_pen_color method is called each time the button in question is clicked.
            b.pressed.connect(lambda c=c: self.canvas.set_pen_color(c))
            layout.addWidget(b)


    # fr : Méthode permettant d'ajouter un bouton dans une zone prédéfinie.
    # en : Method to add a button in predefined zone by layout given.
    def add_action_buttons(self, button, layout):
            layout.addWidget(button)


    # fr : Méthode qui permet d'ajouter une checkbox lorsqu'on enregistre une courbe.
    # en : Method that adds a checkbox when saving a curve.
    def addcheckBox(self):
        if(self.canvas.valid_circuit): 
                self.button_delete.setParent(None)
                
                # fr : on numerote chacune des checkboxs en commençant par 0.
                # en : we number each of the checkboxes starting with 0.
                if (self.numero == []):
                    indice = 0
                else: 
                    indice = self.numero[-1]+1 
                
                self.numero.append(indice) 
                    
                                        
                # fr : on ajoute la case manquante par rapport à la courbe enregistree
                # en : we add the missing box in relation to the saved curve
                self.listCheckBox.append("courbe "+str(indice))
                
                # fr : On renomme les cases en fonction du numero.
                # en : We rename the boxes according to the number.
                for i in range(0, len(self.listCheckBox)):
                    self.listCheckBox[i] = "courbe"+str(self.numero[i]+1)
                    print(self.numero[i]+1)

                # fr : On associe les noms avec des cases a cocher.
                # en : We associate the names with checkboxes.
                for i, v in enumerate(self.listCheckBox):
                    self.listCheckBox[i] = QCheckBox(v)
                    self.listCheckBox[i].toggled.connect(self.checkboxChanged)
                    
                    self.courbes.addWidget(self.listCheckBox[i],i,0)
                    
                self.listCheckBox[indice].setChecked(True)
                self.checkBoxs.addLayout(self.courbes)                
                
                # fr : On ajoute les boutons suivant, appelés lorsqu'on valide un circuit.
                # en: We add the following buttons, called when we validate a circuit.
                self.button_delete = QButton("#000000","Delete")
                self.button_delete.clicked.connect(self.deletecheckBox)
                
                self.courbes.addWidget(self.button_delete)
                
                self.canvas.valid_circuit = False


    # fr : Méthode qui permet de supprimer une checkbox lorsqu'on supprime une courbe.
    # TODO adapter cette méthode pour la suppression de plusieurs courbes à la fois (On a remarquer des erreurs)
    # en : Method that delete a checkbox when deleting a curve.
    # TODO adapt this method for deleting multiple curves at once (error remarqued)
    def deletecheckBox(self):
        indice = []
        
        # fr : On ajoute au tableau d'indice les checkboxs à supprimer.
        # en : We add to the index array the checkboxes to delete.
        for i,v in enumerate(self.listCheckBox):
            if(v.checkState()):
                indice.append(self.listCheckBox.index(v))
                self.canvas.deleteTrajectory(self.listCheckBox.index(v))
                
                
        i = len(self.listCheckBox)-1
        
        # fr : On supprime les toutes les cases a cocher en partant de la fin jusqu'à la dernière checkbox supprimée.
        # en : We remove all the checkboxes starting from the end until the last checkbox removed.
        while (i>= indice[0]):
            self.listCheckBox[-1].deleteLater()
            self.listCheckBox.pop() 
            i-=1

        # fr : On supprime les numéros des checkboxs supprimée de la liste de toutes les checkboxs.
        # en : We delete the numbers of the deleted checkboxes from the list of all checkboxes.
        for j in reversed(indice):
            del self.numero[j]

        # fr : nommer les courbes apres la courbes supprimées
        # en : name the curves after the one deleted
        for j in range(indice[0], self.canvas.compteur):
            self.listCheckBox.append("courbe"+str(self.numero[j]+1))
        
        # fr : nommer les courbes avant la courbes supprimées
        # en : name the curves before the one deleted
        k=0
        while k<indice[0]:
            self.listCheckBox[k]="courbe"+str(self.numero[k]+1)
            k+=1

        # fr : supprimer les doublons dans la liste
        # en : delete the same numbers in the list
        for i in range(len(self.listCheckBox), len(self.numero)):
            del self.numero[-1]        
    
        # fr : On associe les noms avec des cases a cocher.
        # en : We associate the names with checkboxes.
        for j, v in enumerate(self.listCheckBox):
            self.listCheckBox[j] = QCheckBox(v)
            self.listCheckBox[j].toggled.connect(self.checkboxChanged)
            self.courbes.addWidget(self.listCheckBox[j],j,0)
        self.layout.addLayout(self.courbes)
        
        # fr : reglage de l affichage des boutons
        # en : boutons appearances
        if(self.canvas.compteur==0):
            self.button_delete.setParent(None)
        window.show()


    # fr : Méthode qui permet de decocher toutes les checkboxs lorsqu'on supprime une courbe.
    # en : Method which allows to uncheck all the checkboxes when deleting a curve.
    def uncochedcheckBox(self):
        for i , v in enumerate(self.listCheckBox):
            if(v.checkState()):
                v.setCheckState(False)


    # fr : Méthode qui permet d'afficher les coubres en fonction des checkboxs cochées.
    # en : Method used to display the curves according to the checked checkboxes.
    def checkboxChanged(self):
        self.canvas.clear_circuit()
        for i,v in enumerate(self.listCheckBox):
            if(v.checkState()):
                self.canvas.loadChosenTrajectory(self.listCheckBox.index(v))



app = QApplication.instance()
if not app:
    app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec_()