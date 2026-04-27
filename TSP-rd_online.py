import sys, os, time
# pour lire un dictionnaire d'un fichier
import ast
# pour faire la statistique
import statistics, numpy
# pour verifier si une solution online traite toutes les tâches
import collections
# pour utiliser random, si besoin est
import random
import math

############ Student module ############

# -------------------------------------------------------------- #
# --- Fonctions utilitaires - n'y touchez pas, les enfants ! --- #
# -------------------------------------------------------------- #

def verify_solution(sol_online):
    if len(sol_online)!=len(sigma):
        raise ValueError("Solution trop longue ou trop courte")
    sommets_de_sequence = [list(tup[0].keys())[0] for tup in sigma]
    if set(sol_online)!=set(sommets_de_sequence):
        raise ValueError("Solution comprte des sommets differents du graphe")
    if sol_online[0] != 'A':
        raise ValueError("La solution doit commencer par le sommet 'A'")
    for i in range(len(sol_online)-1):
        sommet = sol_online[i]
        sommet_est_arrive = next((tup[1] for tup in sigma if list(tup[0].keys())[0] == sommet), None)
        # et encore si la chronologie est respectée
        if sommet_est_arrive is None :
            raise ValueError(f"Sommet {sommet} non trouvé dans le graphe.")
        if sommet_est_arrive > i:
            raise ValueError(f"Sommet {sommet} est arrivé après son temps d'apparition dans la solution.")
    
    return True


def longueur_tour(sol_online):
   # le calcul est direct ;
   # on suppose que la vérification de la chronologie est faite dans la fonction verify_solution(.)
    longueur = 0
    for i in range(len(sol_online)-1):
        depart = sol_online[i]
        arrivee = sol_online[i+1]
        # il faut comparer les temps d'apparition pour savoir où est la valeur
        depart_time = next((tup[1] for tup in sigma if list(tup[0].keys())[0] == depart), None)
        arrivee_time = next((tup[1] for tup in sigma if list(tup[0].keys())[0] == arrivee), None)
        if depart_time >= arrivee_time:
                outer_key = depart
                inner_key = arrivee
        else:
                outer_key = arrivee  
                inner_key = depart
            # on ajoute la longueur jusquà ce sommet à la solution

        for item, _ in sigma:
            if outer_key in item:
                inner_dict = item[outer_key]
                if inner_key in inner_dict:
                    longueur += inner_dict[inner_key]

    # on ajoute la longueur pour atteindre le dernier sommet
    depart = sol_online[-1]
    arrivee = sol_online[0]
    # ici, le sommet A n'a sûrement pas de voisins dans sigma, il faut faire à l'envers
    for item, _ in sigma:
        if depart in item:
            inner_dict = item[depart]
            if arrivee in inner_dict:
                longueur += inner_dict[arrivee]
    return longueur

def mon_algo_est_deterministe():
    # par défaut l'algo est considéré comme déterministe
    # changez response = False dans le cas contraire
    response = True #False #True 
    return response 


##############################################################
# La fonction à completer pour la compétition
##############################################################

def TSP_rd_online(it, next_sommet, sommets_decouverts, sol_online):
    """
        À faire:         
        - Écrire une fonction qui construit un tour hamiltonien au fur et à mesure de découverte du graphe en minimisant sa longueur
        le résultat est répertorié dans une variable globale sol_online, liste des sommets du graphe constituant un tour
        ATTENTION : le sommet du début du tour : toujours 'A', le seul sommet disponible à t=0
  
    """
    ###################################################################################
    # Complétez cette fonction : construisez un tour hamiltonien en minimisant sa longueur
    # au fur et à mesure de découverte du graphe ; l'algorithme avance en temps ;
    # il est possible que plusieurs sommets soient découverts au même moment ;
    # le tour est construit avec des sommets qui viennent d'être découverts et ceux qui ont déjà été découverts,
    #  mais ils ne sont pas encore intégrés dans la solution
    ###################################################################################
    # ATTENTION :
    #  Le tour doit commencer par le sommet 'A' et finir par le sommet 'A'.
    # Ce sommet est toujours le seul à apparaître dans la séquence.
    # ###################################################################################
    # ATTENTION !!!!
    # Il'itérateur it est attaché à la séquence de pouvoir lire les sommets arrivant à l'instant t ;
    # vous devrez retourner it pointant vers les sommets arrivant à l'instant t+1
    # pour que la fonction puisse continuer à fonctionner ;
    # ###################################################################################

    return it, sommets_decouverts, sol_online # retour nécessaire pour ingestion

##############################################################
#### LISEZ LE README et NE PAS MODIFIER LE CODE SUIVANT ####
##############################################################
if __name__=="__main__":

    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    
    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
        print(input_dir, "n'existe pas")
        exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
        print(output_dir, "n'existe pas")
        exit()       
	
    # fichier des reponses depose dans le output_dir et annote par date/heure
    output_filename = 'answers_{}.txt'.format(time.strftime("%d%b%Y_%H%M%S", time.localtime()))             
    output_file = open(os.path.join(output_dir, output_filename), 'w')

    # le bloc de lancement dégagé à l'exterieur pour ne pas le répeter pour deterministe/random
    def launching_sequence(it):    
        sol_online  = [] # initialisation de la solution online, au depart la liste est vide
        current_sol_length = 0 # initialisation de la longueur du tour pour vérifier 
        # si l'algo online construit la solution à la volée, sans attendre !
        sommets_decouverts = [] # initialisation de la liste des sommets découverts
        # qui ne sont pas encore incorporés dans la solution en construction, accompagnés de leur voisinage
        # la forme de cette liste est une liste de dictionnaires,
        # chaque dictionnaire contient un sommet (comme clé) et ses voisins avec les poids des arêtes
        # (la valeur, c'est la ligne de l'élément de sigma !)
        # Iterateur it déjà initialisé 

        while True:
            try:
                next_sommet = next(it) 
                it, sommets_decouverts, sol_online = TSP_rd_online(it, next_sommet, sommets_decouverts, sol_online)
                if current_sol_length >= len(sol_online):
                    raise ValueError("L'algorithme ne construit pas la solution à la volée !")
                current_sol_length = len(sol_online) # mise à jour de la longueur du tour en contruction
            except StopIteration:
                break
        return sol_online # retour nécessaire pour ingestion

    # Collecte des résultats
    scores = []
    
    for instance_filename in sorted(os.listdir(input_dir)):
        
        # C'est une partie pour inserer dans ingestion.py !!!!!
        # importer l'instance depuis le fichier (attention code non robuste)
        # le code repris de Safouan - refaire pour m'affanchir des numéros explicites
        instance_file = open(os.path.join(input_dir, instance_filename), "r")
        lines = instance_file.readlines()
        
        str_lu_sigma = lines[1]
        sigma = ast.literal_eval(str_lu_sigma)
        exact_solution = lines[4]

        it = iter(sigma)

        # lancement conditionelle de votre algorithme
        # N.B. il est lancé par la fonction launching_sequence(it) 
        if mon_algo_est_deterministe():
            print("lancement d'un algo deterministe")  
            solution_online = launching_sequence(it) 
            verify_solution(solution_online)
            solution_eleve = longueur_tour(solution_online)
        else:
            print("lancement d'un algo randomisé")
            runs = 10
            sample = numpy.empty(runs)
            for r in range(runs):
                # pour l'algo randomisé, il faut rattacher it à chaque passage de la boucle collectant les résultats
                it = iter(sigma)
                solution_online = launching_sequence(it)  
                verify_solution(solution_online)  
                sample[r] = longueur_tour(solution_online)
            solution_eleve = numpy.mean(sample)


        best_ratio = solution_eleve/float(exact_solution)
        scores.append(best_ratio)
        # ajout au rapport
        output_file.write(instance_filename + ': score: {}\n'.format(best_ratio))

    output_file.write("Résultat moyen des ratios:" + str(sum(scores)/len(scores)))

    output_file.close()
