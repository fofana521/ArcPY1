import arcpy
from datetime import datetime

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
Distance = arcpy.GetParameterAsText(4)
Ecart_0_3mois = arcpy.GetParameterAsText(5)
Ecart_3_6mois = arcpy.GetParameterAsText(6)
Ecart_6_12mois = arcpy.GetParameterAsText(7)
Ecart_12mois_plus = arcpy.GetParameterAsText(8)
#unite_mesure = "15 meters"
ancien_nom_champ = "Date_debut"
nouveau_nom_champ = "Date_debut2"
champs_agregation = ["emprise_statut", "date_debut", "maitre_ouvrage", "projet_cite_id", "numero_affaire"]
nom_champ = "Ecart_mois" # Nom du champ entier à créer
expression = 'DateDiff($feature.date_debut, $feature.date_fin, "month")' # Définir l'expression Arcade pour calculer l'écart de mois entre deux dates

# Donnees_sorties
Donnee_en_sortie1 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\PGTVX_merged"
Fusion = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Intervention_agrege"
Fusion1 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\PGTVX_merged_agrege"
zone_tampon = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Intervention_agrege_Buffer"
intersection = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\intersection"

# Fusionner les Trois(03) couches en Une seule
arcpy.Merge_management([Intentions_Travaux, En_attente_de_signature_STV,
                       Coordination_avec_autres_concess],
                       Donnee_en_sortie1)


# Agrégation des entités en fonction des attributs spécifiés
arcpy.management.Dissolve(Intervention, Fusion,
                          champs_agregation)

# Renommer le champ
arcpy.AlterField_management(Fusion, ancien_nom_champ, nouveau_nom_champ, nouveau_nom_champ)


arcpy.management.Dissolve(Donnee_en_sortie1, Fusion1,
                          champs_agregation)


# Créer la zone tampon
arcpy.Buffer_analysis(Fusion, zone_tampon, Distance)


# Intersecter les couches
arcpy.Intersect_analysis([Fusion1, zone_tampon], intersection)

# Utiliser la fonction AddField pour ajouter le champ à la classe d'entités
arcpy.AddField_management(intersection, nom_champ, "SHORT")

### Définir l'expression Arcade pour calculer l'écart de mois entre deux dates
#expression = 'DateDiff($feature.date_debut, $feature.date_fin, "month")'

# Définir les noms des champs de date à utiliser
date_field1 = "Date_debut"
date_field2 = "Date_debut2"


with arcpy.da.UpdateCursor(intersection, [date_field1, date_field2, nom_champ]) as cursor:
    for row in cursor:
        # Calculez l'écart de mois en utilisant la méthode .month de l'objet date
        ecart = (row[1].year - row[0].year) * 12 + (row[1].month - row[0].month)
        # Supprimez le caractère "-" du résultat en utilisant la méthode str.replace()
        ecart_str = str(ecart).replace("-", "")
        # Convertissez le résultat en entier et stockez-le dans le champ "ecart_de_mois"
        row[2] = int(ecart_str)
        cursor.updateRow(row)


# Process: Sélectionner (Sélectionner) (analysis)
# Sélectionnez les entités avec les valeurs d'écart de mois 
arcpy.Select_analysis(intersection, Ecart_0_3mois, "Ecart_mois IN (1, 2, 3)")
arcpy.Select_analysis(intersection, Ecart_3_6mois, "Ecart_mois IN (4, 5, 6)")
arcpy.Select_analysis(intersection, Ecart_6_12mois, "Ecart_mois IN (7, 12, 11, 10, 9, 8)")
arcpy.Select_analysis(intersection, Ecart_12mois_plus, "Ecart_mois IN (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 46, 33)")


# Spécifier le nom et le chemin de la nouvelle couche
##Ecart1 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_0_3mois"
##Ecart2 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_3_6mois"
##Ecart3 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_6_12mois"
##Ecart4 = r"C:\Users\ene10dr4\Documents\ArcGIS\Projects\web_outil_test\web_outil_test.gdb\Ecart_12mois_plus"

##arcpy.Select_analysis(intersection, Ecart1, "Ecart_mois IN (1, 2, 3)")
##arcpy.Select_analysis(intersection, Ecart2, "Ecart_mois IN (4, 5, 7, 6)")
##arcpy.Select_analysis(intersection, Ecart3, "Ecart_mois IN (7, 12, 11, 10, 9, 8)")
##arcpy.Select_analysis(intersection, Ecart4, "Ecart_mois IN (13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 46, 33)")



print_message("- Script complet !")
