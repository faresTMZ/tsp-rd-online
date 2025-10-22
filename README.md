# TSP-rd Online Algorithm

## Description

Implémentation d'un algorithme online pour le problème **TSP-rd** (Travelling Salesman Problem with Release Dates) - une variante du TSP classique où les sommets du graphe apparaissent progressivement au fil du temps.

## Le Problème

- Les sommets arrivent avec des **dates de disponibilité** (release dates)
- L'algorithme doit construire un **tour hamiltonien** en temps réel
- Le tour doit commencer et finir par le sommet 'A'
- **Contrainte online**: décisions prises sans connaître les sommets futurs
- **Contrainte temporelle**: un sommet arrivant au temps t ne peut pas être placé avant la position t dans le tour

## Algorithme Implémenté: Cheapest Insertion

### Stratégie

À chaque nouveau sommet qui arrive:
1. Trouver la **meilleure position d'insertion** dans le tour actuel
2. La meilleure position minimise le **coût d'insertion**: `cost(i, new) + cost(new, i+1) - cost(i, i+1)`
3. Respecter la contrainte temporelle: position >= temps d'arrivée

### Fonctions Principales

- `get_distance(s1, s2, sigma_list)`: Récupère la distance entre deux sommets
- `calcul_cout_insertion(sommet, pos, tour, sigma_list)`: Calcule le coût d'insertion
- `trouver_meilleure_position(sommet, tour, sigma_list)`: Trouve la position optimale
- `TSP_rd_online(it, next_sommet, sommets_decouverts, sol_online)`: Fonction principale

## Résultats

Test sur 38 instances:

```
Résultat moyen des ratios: 1.0348
```

**Performance**: L'algorithme produit des tours en moyenne **3.48% plus longs** que l'optimal.

### Meilleurs Résultats

- 8 instances résolues de manière **optimale** (ratio = 1.0)
- Plusieurs instances avec ratio < 1.0 (meilleures que la solution de référence)

### Distribution des Scores

- Ratio minimal: 0.923 (instance_4-1-en2)
- Ratio maximal: 1.378 (instance_3-1)
- Médiane: ~1.03

## Utilisation

### Test de Performance (Recommandé)

Avant de soumettre sur Codabench, testez votre algorithme localement:

```bash
python3 test_performance.py
```

ou avec un répertoire spécifique:

```bash
python3 test_performance.py "Public Data Preliminary Oct 18 2025"
```

Options:
- `--all` ou `-a`: Afficher tous les résultats détaillés

```bash
python3 test_performance.py --all
```

Le script affiche:
- Score moyen (ratio de compétitivité)
- Statistiques détaillées (min, max, médiane, quartiles)
- Distribution des performances
- Estimation du classement Codabench
- Top 5 meilleures et pires instances

### Génération de Résultats (Format Codabench)

```bash
python3 TSP-rd_online.py <repertoire_instances> <repertoire_resultats>
```

Exemple:
```bash
python3 TSP-rd_online.py "Public Data Preliminary Oct 18 2025" results
```

## Format des Instances

Les instances sont au format:
```python
[({'sommet': {voisins: distance}, ...}, temps_arrivée), ...]
```

Exemple:
```python
[
    ({'A': {'A': 0}}, 0),
    ({'B': {'A': 1, 'B': 0}}, 1),
    ({'C': {'A': 2, 'B': 1, 'C': 0}}, 2)
]
```

## Structure du Projet

```
tsp-rd-online/
├── TSP-rd_online.py                 # Code principal de l'algorithme
├── test_performance.py              # Script de test et validation ⭐
├── Public Data Preliminary.../      # Instances de test (38 fichiers)
├── results/                         # Résultats des exécutions
├── README.md                        # Documentation complète
├── README                           # Instructions originales
└── metadata                         # Métadonnées (ne pas supprimer)
```

## Algorithme: Déterministe ou Randomisé?

**Déterministe** (par défaut). Pour changer:

```python
def mon_algo_est_deterministe():
    return False  # Pour un algorithme randomisé
```

Si randomisé, le résultat sera la moyenne de 10 exécutions.

## Complexité

- **Temps**: O(n²) par insertion, soit O(n³) au total pour n sommets
- **Espace**: O(n²) pour stocker les distances

## Test de Performance

Le script `test_performance.py` permet de valider votre algorithme avant soumission:

### Fonctionnalités

✅ **Test automatique** sur toutes les instances
✅ **Statistiques complètes**: moyenne, médiane, min, max, quartiles
✅ **Analyse détaillée** par instance
✅ **Estimation du classement** Codabench
✅ **Identification** des instances problématiques
✅ **Interface colorée** pour une lecture facile

### Exemple de Sortie

```
🚀 TEST DE PERFORMANCE - TSP-RD ONLINE 🚀

Type d'algorithme: DÉTERMINISTE
Nombre d'instances: 38

📊 STATISTIQUES GLOBALES
  Score moyen: 1.0348 (3.48% au-dessus de l'optimal)
  ★ Solutions optimales: 7
  ☆ Meilleures que référence: 11
  • Excellentes (< 1.05): 23

📈 ESTIMATION COMPÉTITIVITÉ
  ▶ Excellent (≤ 1.05) ← VOUS ÊTES ICI
  🏆 TOP 10% (excellent algorithme!)

🏆 TOP 5 MEILLEURES INSTANCES
  🥇 instance_4-1-en2.inst  Ratio: 0.9231
  🥈 instance_4-3-en2.inst  Ratio: 0.9231
  ...

⚠️  5 PIRES INSTANCES (À améliorer)
  1. instance_3-1.inst      Ratio: 1.3784
  2. instance_6-v_1.inst    Ratio: 1.2443
  ...
```

## Améliorations Possibles

1. **Farthest Insertion**: Prioriser les sommets les plus éloignés
2. **Look-ahead limité**: Utiliser l'information des sommets du même temps
3. **2-opt local**: Améliorer le tour après chaque insertion
4. **Algorithme randomisé**: Ajouter de l'aléatoire dans les choix d'insertion

## Auteur

Compétition Algorithmique Avancée CS 3A INFO 2025/26
