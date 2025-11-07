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
# Fonctions auxiliaires pour l'algorithme
##############################################################

# Cache global pour les distances et les temps d'arrivée (optimisation performance)
_distance_cache = {}
_sommet_temps = {}
_sommet_voisins = {}

def get_distance(sommet1, sommet2, sigma_list=None):
    """
    Récupère la distance entre deux sommets (version optimisée avec cache).
    La distance est stockée dans le dictionnaire du sommet arrivé en dernier.
    """
    if sommet1 == sommet2:
        return 0

    # Vérifier le cache d'abord
    cache_key = (sommet1, sommet2) if sommet1 < sommet2 else (sommet2, sommet1)
    if cache_key in _distance_cache:
        return _distance_cache[cache_key]

    # Si pas dans le cache, calculer et mettre en cache
    time1 = _sommet_temps.get(sommet1)
    time2 = _sommet_temps.get(sommet2)

    if time1 is None or time2 is None:
        return float('inf')

    # Le sommet arrivé en dernier contient la distance
    if time1 >= time2:
        outer_key = sommet1
        inner_key = sommet2
    else:
        outer_key = sommet2
        inner_key = sommet1

    # Chercher dans les voisins du sommet
    if outer_key in _sommet_voisins and inner_key in _sommet_voisins[outer_key]:
        distance = _sommet_voisins[outer_key][inner_key]
        _distance_cache[cache_key] = distance
        return distance

    return float('inf')


def _update_cache(sommet_dict, temps):
    """
    Met à jour le cache avec un nouveau sommet.
    """
    sommet = list(sommet_dict.keys())[0]
    voisins = sommet_dict[sommet]

    _sommet_temps[sommet] = temps
    _sommet_voisins[sommet] = voisins


def calcul_cout_insertion(sommet, position, tour, sigma_list=None):
    """
    Calcule le coût d'insertion d'un sommet à une position donnée dans le tour (version optimisée).

    Args:
        sommet: le sommet à insérer
        position: la position où insérer (entre position et position+1)
        tour: le tour actuel
        sigma_list: non utilisé (conservé pour compatibilité)

    Returns:
        Le coût d'insertion (peut être négatif si ça améliore le tour)
    """
    if len(tour) < 2:
        return 0

    sommet_avant = tour[position]
    sommet_apres = tour[(position + 1) % len(tour)]

    # Coût actuel entre sommet_avant et sommet_apres
    cout_actuel = get_distance(sommet_avant, sommet_apres)

    # Nouveau coût avec le sommet inséré
    nouveau_cout = get_distance(sommet_avant, sommet) + \
                   get_distance(sommet, sommet_apres)

    return nouveau_cout - cout_actuel


def trouver_meilleure_position(sommet, tour, sigma_list=None):
    """
    Trouve la meilleure position pour insérer un sommet dans le tour (version optimisée).
    Respecte la contrainte: un sommet arrivant au temps t ne peut pas
    être placé avant la position t dans le tour.

    Returns:
        La position optimale d'insertion
    """
    if len(tour) <= 1:
        return len(tour)

    # Trouver le temps d'arrivée du sommet (depuis le cache)
    temps_arrivee = _sommet_temps.get(sommet, 0)

    meilleur_cout = float('inf')
    meilleure_position = max(1, temps_arrivee)

    # Essayer toutes les positions possibles >= temps_arrivee
    # (contrainte: position >= temps d'arrivée)
    position_min = temps_arrivee

    for i in range(len(tour)):
        # On peut insérer après la position i, donc la nouvelle position sera i+1
        nouvelle_position = i + 1

        # Vérifier la contrainte temporelle
        if nouvelle_position < position_min:
            continue

        cout = calcul_cout_insertion(sommet, i, tour)
        if cout < meilleur_cout:
            meilleur_cout = cout
            meilleure_position = i

    return meilleure_position


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
    # Algorithme: Cheapest Insertion (version optimisée)
    # À chaque appel, on reçoit un nouveau sommet à traiter
    # On l'insère à la position qui minimise l'augmentation du tour
    ###################################################################################

    # Récupérer le sommet et son temps d'arrivée
    sommet_dict, temps_actuel = next_sommet
    sommet_nom = list(sommet_dict.keys())[0]

    # Réinitialiser le cache au début de chaque test (quand on reçoit le premier sommet A)
    if len(sol_online) == 0 and sommet_nom == 'A':
        global _distance_cache, _sommet_temps, _sommet_voisins
        _distance_cache = {}
        _sommet_temps = {}
        _sommet_voisins = {}

    # Mettre à jour le cache pour ce nouveau sommet (optimisation performance)
    _update_cache(sommet_dict, temps_actuel)

    # Ajouter le nouveau sommet à la liste des sommets découverts
    sommets_decouverts.append(next_sommet)

    # Initialisation: si le tour est vide et que c'est 'A', on démarre le tour
    if len(sol_online) == 0 and sommet_nom == 'A':
        sol_online.append('A')
        return it, sommets_decouverts, sol_online

    # Si c'est un autre sommet que A, on l'insère dans le tour
    if sommet_nom != 'A':
        # Trouver la meilleure position pour insérer ce sommet
        meilleure_position = trouver_meilleure_position(sommet_nom, sol_online)

        # Insérer le sommet à la meilleure position
        sol_online.insert(meilleure_position + 1, sommet_nom)

    return it, sommets_decouverts, sol_online # retour nécessaire pour ingestion

##############################################################
#### LISEZ LE README et NE PAS MODIFIER LE CODE SUIVANT ####
##############################################################
if __name__=="__main__":

    input_dir = os.path.abspath(sys.argv[1])
    output_dir = os.path.abspath(sys.argv[2])
    
    # un repertoire des graphes en entree doit être passé en parametre 1
    if not os.path.isdir(input_dir):
        print(input_dir, "doesn't exist")
        exit()

    # un repertoire pour enregistrer les dominants doit être passé en parametre 2
    if not os.path.isdir(output_dir):
        print(output_dir, "doesn't exist")
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
