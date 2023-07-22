import arcpy
from datetime import datetime, timedelta

def print_message(msg):
    print(msg)
    arcpy.AddMessage(msg)


arcpy.env.overwriteOutput = True
arcpy.env.workspace = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb"



# Couche d'entrée & Variable

Intervention = arcpy.GetParameterAsText(0)
Intentions_Travaux = arcpy.GetParameterAsText(1)
En_attente_de_signature_STV = arcpy.GetParameterAsText(2)
Coordination_avec_autres_concess = arcpy.GetParameterAsText(3)
DVD = arcpy.GetParameterAsText(4)
SUBDI = arcpy.GetParameterAsText(5)
Distance = arcpy.GetParameterAsText(6)
intersection = arcpy.GetParameterAsText(7)
##Ecart_0_3mois = arcpy.GetParameterAsText(7)
##Ecart_3_6mois = arcpy.GetParameterAsText(8)
##Ecart_6_12mois = arcpy.GetParameterAsText(9)
##Ecart_12mois_plus = arcpy.GetParameterAsText(10)
#unite_mesure = "15 meters"

# Modifier titre de champ
ancien_nom_champ = "Date_debut"
nouveau_nom_champ = "Date_debut2"
ancien_nom_champ1 = "Date_fin"
nouveau_nom_champ1 = "Date_fin2"


champs_agregation = ["emprise_statut", "date_debut", "date_fin", "maitre_ouvrage", "projet_cite_id", "numero_affaire"]
nom_champ = "Coactivite" # Nom du champ entier à créer
etat_champ = "Etat_Chantier_CITE"

#expression = 'DateDiff($feature.date_debut, $feature.date_fin, "month")' # Définir l'expression Arcade pour calculer l'écart de mois entre deux dates

# Donnees_sorties
Donnee_en_sortie1 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\PGTVX_Enedis_merged"
Donnee_en_sortie2 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ville_merged"
Fusion = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ville_merged_agrege"
Fusion1 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\PGTVX_Enedis_merged_agrege"
zone_tampon = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ville_merged__agrege_Buffer"
# intersection = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\intersection_PGTVX_Ville" #Activé lorsque l'intersection parameter est désactivité

# Fusionner les Trois(03) couches en Une seule
# Fusionner les chantiers ENEDIS
arcpy.Merge_management([Intervention, Intentions_Travaux, En_attente_de_signature_STV,
                       Coordination_avec_autres_concess],
                       Donnee_en_sortie1)

# Fusionner les chantiers de la Ville
arcpy.Merge_management([DVD, SUBDI],
                       Donnee_en_sortie2)


# Agrégation des entités en fonction des attributs spécifiés
arcpy.management.Dissolve(Donnee_en_sortie2, Fusion,
                          champs_agregation)

# Renommer le champ
arcpy.AlterField_management(Fusion, ancien_nom_champ, nouveau_nom_champ, nouveau_nom_champ)
arcpy.AlterField_management(Fusion, ancien_nom_champ1, nouveau_nom_champ1, nouveau_nom_champ1)


arcpy.management.Dissolve(Donnee_en_sortie1, Fusion1,
                          champs_agregation)


# Créer la zone tampon
arcpy.Buffer_analysis(Fusion, zone_tampon, Distance)


# Intersecter les couches
arcpy.Intersect_analysis([Fusion1, zone_tampon], intersection)

### Utiliser la fonction AddField pour ajouter le champ à la classe d'entités
arcpy.AddField_management(intersection, nom_champ, "TEXT")


##### Définir l'expression Arcade pour calculer l'écart de mois entre deux dates
###expression = 'DateDiff($feature.date_debut, $feature.date_fin, "month")'

### Définir les noms des champs de date à utiliser
date_field1 = "Date_debut"
date_field2 = "Date_debut2"
date_field3 = "Date_fin"
date_field4 = "Date_fin2"


with arcpy.da.UpdateCursor(intersection, [date_field1, date_field2, nom_champ]) as cursor:
    for row in cursor:
        # Calculez l'écart de mois en utilisant la méthode .month de l'objet date
        ecart = (row[1].year - row[0].year) * 12 + (row[1].month - row[0].month)
        # Supprimez le caractère "-" du résultat en utilisant la méthode str.replace()
        ecart_str = str(ecart).replace("-", "")
        # Convertissez le résultat en entier et stockez-le dans le champ "ecart_de_mois"
        row[2] = int(ecart_str)
        cursor.updateRow(row)


# Parcourir les lignes de la table contenant les données des chantiers
with arcpy.da.UpdateCursor(intersection, [date_field1, date_field2, date_field3, date_field4, nom_champ]) as cursor:
    for row in cursor:
        date_field1 = row[0]
        date_field3 = row[1]
        date_field2 = row[2]
        date_field4 = row[3]
        nom_champ = row[4]
        
        # Comparer les dates de début et de fin pour les chantiers Enedis et ville
        if date_field2 > date_field1:
            row[4] = str(nom_champ) + " mois de coactivité, Les chantiers Enedis passe en premier"
        elif date_field2 < date_field1:
            row[4] = str(nom_champ) + " mois de coactivité, Les chantiers ville passe en premier"
        elif date_field1 > date_field4:
            row[4] = "Attention, chantier Ville programmé " + str(nom_champ) + " mois avant Enedis"
        else:
            row[4] = "Pas d'alerte, chantier Enedis terminé avant la Ville"
        
        # Mettre à jour la ligne
        cursor.updateRow(row)


print_message("- Script complet !")





### Créer le champ si celui-ci n'existe pas déjà
##if not arcpy.ListFields(intersection, etat_champ):
##    arcpy.AddField_management(intersection, etat_champ, "TEXT")
##
### Parcourir les enregistrements de la couche et mettre à jour le champ en fonction de la condition si
##with arcpy.da.UpdateCursor(intersection, [etat_champ]) as cursor:
##    for row in cursor:
##        date_field3 = row[1]
##        if date_field3 <= (datetime.now() - timedelta(days=1)):
##            row[0] = "Chantier Enedis terminé"
##        elif date_field3 >= datetime.now():
##            row[0] = "Chantier Enedis en cours"
##        else:
##            row[0] = ""
##        cursor.updateRow(row)

##
### Ajouter le champ à la classe d'entités si elle n'existe pas encore
##
##if etat_champ not in [f.name for f in arcpy.ListFields(intersection)]:
##    arcpy.AddField_management(intersection, etat_champ, "TEXT")
##
### Récupérer la date d'hier et d'aujourd'hui
##today = datetime.now()
##yesterday = today - timedelta(days=1)
##
### Mettre à jour les valeurs du champ en fonction de la date de fin du chantier
##with arcpy.da.UpdateCursor(intersection, [date_field3, etat_champ]) as cursor:
##    for row in cursor:
##        if row[0] is not None:
##            date_field3 = datetime.strptime(row[0], '%Y-%m-%d')
##            if date_field3 <= yesterday:
##                row[1] = "Chantier Enedis terminé"
##            elif date_field3 >= today:
##                row[1] = "Chantier Enedis en cours"
##            else:
##                row[1] = "Chantier Enedis planifié"
##            cursor.updateRow(row)




### Parcourir les lignes de la table contenant les données des chantiers Enedis
##with arcpy.da.UpdateCursor(intersection, [date_field3, etat_champ]) as cursor:
##    for row in cursor:
##        date_field3 = row[0]
##        
##        # Comparer la date de fin avec la date d'aujourd'hui et celle d'hier pour déterminer l'état du chantier
##        if date_field3 <= yesterday:
##            row[1] = "Chantier Enedis terminé"
##        elif date_field3 >= now:
##            row[1] = "Chantier Enedis en cours"
##        else:
##            row[1] = "Chantier Enedis à venir"
##        
##        # Mettre à jour la ligne
##        cursor.updateRow(row)
        


### Process: Sélectionner (Sélectionner) (analysis)
### Sélectionnez les entités avec les valeurs d'écart de mois 
##arcpy.Select_analysis(intersection, Ecart_0_3mois, "Ecart_mois IN (1, 2, 3)")
##arcpy.Select_analysis(intersection, Ecart_3_6mois, "Ecart_mois IN (4, 5, 7, 6)")
##arcpy.Select_analysis(intersection, Ecart_6_12mois, "Ecart_mois IN (7, 12, 11, 10, 9, 8)")
##arcpy.Select_analysis(intersection, Ecart_12mois_plus, "Ecart_mois IN (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 46, 33)")
##
##
### Spécifier le nom et le chemin de la nouvelle couche
####Ecart1 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_0_3mois"
####Ecart2 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_3_6mois"
####Ecart3 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_6_12mois"
####Ecart4 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_12mois_plus"
##
####arcpy.Select_analysis(intersection, Ecart1, "Ecart_mois IN (1, 2, 3)")
####arcpy.Select_analysis(intersection, Ecart2, "Ecart_mois IN (4, 5, 6)")
####arcpy.Select_analysis(intersection, Ecart3, "Ecart_mois IN (7, 12, 11, 10, 9, 8)")
####arcpy.Select_analysis(intersection, Ecart4, "Ecart_mois IN (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 46, 33)")
##


print_message("- Script complet !")
