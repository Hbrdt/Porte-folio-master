from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingParameterDistance)
from qgis import processing


class ZoneHabitationAlgorithm(QgsProcessingAlgorithm):
    """
    Retourne les objets d'une couche à proximité d'une autre couche.
    """
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT = 'OUTPUT'  # couche en sortie
    SOURCE = 'SOURCE'  # couche qui sera intersectée:
    GARE = 'GARE_SNCF'  # couche qui servira à créer le buffer 
    METRO = 'METRO'  # couche qui servira à créer le buffer 
    PISCINES = 'PISCINES'  # couche qui servira à créer le buffer 
    ESPACES_VERTS = 'ESPACES_VERTS'  # couche qui servira à créer le buffer 
    
    
    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ProximiteAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. 
        """
        return 'Zone_habitation'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Zone idéale')
    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Parigoooooooo AH oui et au fait il faut que toutes les couches soient dans la même projection parce que flemme de dev un truc de plus la bise :)')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Scripts PyQGIS')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'scriptspyqgis'

    def initAlgorithm(self, config=None):
        """
        Initialisation de l'algorithme: définition des
        paramètres en entrée et en sortie
        """

        # Données source
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.SOURCE,
                self.tr('Couche d\'intérêt'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        # Données superposées GARES
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.GARES,
                self.tr('Couche tampon'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
            
        # Distance du tampon 
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST1',
                self.tr('Distance du tampon'),
                defaultValue = 1000.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='GARES'
            )
        )
        
        # Données superposées METRO
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.METRO,
                self.tr('Couche sur laquelle sera faite le tampon'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
            
        # Distance du tampon 
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST2',
                self.tr('Distance du tampon'),
                defaultValue = 1000.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='METRO'
            )
        )
        
        # Données superposées PISCINES
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.PISCINES,
                self.tr('Couche sur laquelle sera faite le tampon'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
            
        # Distance du tampon
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST3',
                self.tr('Distance du tampon'),
                defaultValue = 1000.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='PISCINES'
            )
        )
        # Données superposées ESPACES_VERTS
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.ESPACES_VERTS,
                self.tr('Couche sur laquelle sera faite le tampon'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
            
        # Distance du tampon
        self.addParameter(
            QgsProcessingParameterDistance(
                'BUFFERDIST4',
                self.tr('Distance du tampon'),
                defaultValue = 1000.0,
                # Make distance units match the INPUT layer units:
                parentParameterName='ESPACES_VERTS'
            )
        )
        # Récupération de la destination.
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT,
                self.tr('Sortie')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # récupération des paramètres
        source = self.parameterAsSource(parameters, self.SOURCE, context)
        superposition = self.parameterAsSource(parameters, self.SUPERPOSITION, context)
        outputFile = self.parameterAsOutputLayer(parameters,self.OUTPUT, context)
        bufferdist = self.parameterAsDouble(parameters, 'BUFFERDIST', context)

        # Vérification qu'il y a bien deux couches en entrée
        # des erreurs sont levées si une couche est manquante
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SOURCE))
        if superposition is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.SUPERPOSITION))

        # Il est possible d'afficher des informations
        # à destination de l'utilisateur
        feedback.pushInfo('Source CRS is {}'.format(source.sourceCrs().authid()))
        feedback.pushInfo('Superposition CRS is {}'.format(superposition.sourceCrs().authid()))

        # Vérification que les couches ont un SRC compatibles
        if source.sourceCrs().authid() != superposition.sourceCrs().authid():
            # Si SRC différents, QGIS lève une exception et arrête l'algorithme.
            raise QgsProcessingException(
                    self.tr('les couches doivent être dans le même système de référence de coordonnées.')
                    )
                    
        # Calcul du tampon            
        tampon = processing.run(
            "native:buffer",{
                'INPUT': parameters['SUPERPOSITION'],
                'DISTANCE' : bufferdist,
                'SEGMENTS' :5,
                'END CAP STYLE' : 0,
                'JOIN STYLE': 0,
                'MITER LIMIT' :2,
                'DISSOLVE' : False,
                'OUTPUT' : 'TEMPORARY_OUTPUT'
                },
            context=context,
            feedback=feedback)
            
        ## Intersection du tampon et de la couche source
        intersection = processing.run(
                "native:intersection", 
                {'INPUT': parameters['SOURCE'],
                'OVERLAY': tampon['OUTPUT'],
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':outputFile})['OUTPUT']

        #Intersection des métros et des gares 

        metro_gares = processing.run(
            "native:intersection", 
                {'INPUT':buffer_gares['OUTPUT'],
                'OVERLAY':buffer_metro['OUTPUT'],
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']

        Inters1 = "intersection metro gares ok"
        print(Inters1)
        # #Intersection précédente et les espaces verts

        metro_gares_espaces_verts = processing.run(
            "native:intersection", 
                {'INPUT':metro_gares,
                'OVERLAY':buffer_espaces_verts['OUTPUT'],
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
        
        Inters2 = "intersection metro gares espces verts ok"
        print(Inters2)

        # #Intersection finale avec les piscines 

        metro_gares_espaces_verts_piscines = processing.run(
            "native:intersection", 
                {'INPUT':metro_gares_espaces_verts,
                'OVERLAY':buffer_piscines['OUTPUT'],
                'INPUT_FIELDS':[],
                'OVERLAY_FIELDS':[],
                'OUTPUT':'TEMPORARY_OUTPUT'})['OUTPUT']
        
        Inters3 = "intersection finale ok"
        print(Inters3)
        # Return the results of the algorithm. In this case our only result is
        # the intersection.
        return {self.OUTPUT: intersection}
