#!/usr/bin/env python3
"""
Script de test de performance pour l'algorithme TSP-rd online.
Permet d'estimer le score avant soumission sur Codabench.

Usage:
    python3 test_performance.py [repertoire_instances]

    Si aucun répertoire n'est spécifié, utilise "Public Data Preliminary Oct 18 2025"
"""

import sys
import os
import ast
import time
from collections import defaultdict

# Importer seulement les fonctions nécessaires de TSP-rd_online.py
import importlib.util
spec = importlib.util.spec_from_file_location("tsp_module", "TSP-rd_online.py")
tsp_module = importlib.util.module_from_spec(spec)

# Charger uniquement les définitions de fonctions (pas le main)
with open('TSP-rd_online.py', 'r') as f:
    code = f.read().split('if __name__=="__main__"')[0]
    exec(code, tsp_module.__dict__)

# Importer les fonctions
TSP_rd_online = tsp_module.TSP_rd_online
mon_algo_est_deterministe = tsp_module.mon_algo_est_deterministe


# Versions locales des fonctions verify_solution et longueur_tour qui prennent sigma en paramètre
def verify_solution_local(sol_online, sigma):
    """Version locale de verify_solution qui prend sigma en paramètre"""
    if len(sol_online) != len(sigma):
        raise ValueError("Solution trop longue ou trop courte")
    sommets_de_sequence = [list(tup[0].keys())[0] for tup in sigma]
    if set(sol_online) != set(sommets_de_sequence):
        raise ValueError("Solution comprte des sommets differents du graphe")
    if sol_online[0] != 'A':
        raise ValueError("La solution doit commencer par le sommet 'A'")
    for i in range(len(sol_online) - 1):
        sommet = sol_online[i]
        sommet_est_arrive = next((tup[1] for tup in sigma if list(tup[0].keys())[0] == sommet), None)
        if sommet_est_arrive is None:
            raise ValueError(f"Sommet {sommet} non trouvé dans le graphe.")
        if sommet_est_arrive > i:
            raise ValueError(f"Sommet {sommet} est arrivé après son temps d'apparition dans la solution.")
    return True


def longueur_tour_local(sol_online, sigma):
    """Version locale de longueur_tour qui prend sigma en paramètre"""
    longueur = 0
    for i in range(len(sol_online) - 1):
        depart = sol_online[i]
        arrivee = sol_online[i + 1]
        depart_time = next((tup[1] for tup in sigma if list(tup[0].keys())[0] == depart), None)
        arrivee_time = next((tup[1] for tup in sigma if list(tup[0].keys())[0] == arrivee), None)
        if depart_time >= arrivee_time:
            outer_key = depart
            inner_key = arrivee
        else:
            outer_key = arrivee
            inner_key = depart

        for item, _ in sigma:
            if outer_key in item:
                inner_dict = item[outer_key]
                if inner_key in inner_dict:
                    longueur += inner_dict[inner_key]

    # Retour vers A
    depart = sol_online[-1]
    arrivee = sol_online[0]
    for item, _ in sigma:
        if depart in item:
            inner_dict = item[depart]
            if arrivee in inner_dict:
                longueur += inner_dict[arrivee]
    return longueur


class Colors:
    """Couleurs ANSI pour le terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'


def print_header(text):
    """Affiche un en-tête formaté"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 70}{Colors.RESET}\n")


def print_section(text):
    """Affiche une section"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'-' * len(text)}{Colors.RESET}")


def test_instance(instance_path):
    """
    Teste une instance et retourne les résultats.

    Returns:
        dict: {
            'success': bool,
            'tour': list,
            'length': int,
            'exact': int,
            'ratio': float,
            'error': str (si échec)
        }
    """
    result = {
        'success': False,
        'tour': [],
        'length': 0,
        'exact': 0,
        'ratio': float('inf'),
        'error': None
    }

    try:
        # Charger l'instance
        with open(instance_path, 'r') as f:
            lines = f.readlines()

        sigma = ast.literal_eval(lines[1])
        exact_solution = float(lines[4].strip())

        # Exécuter l'algorithme
        it = iter(sigma)
        sol_online = []
        sommets_decouverts = []

        while True:
            try:
                next_sommet = next(it)
                it, sommets_decouverts, sol_online = TSP_rd_online(
                    it, next_sommet, sommets_decouverts, sol_online
                )
            except StopIteration:
                break

        # Vérifier la solution
        verify_solution_local(sol_online, sigma)
        longueur = longueur_tour_local(sol_online, sigma)
        ratio = longueur / exact_solution

        result['success'] = True
        result['tour'] = sol_online
        result['length'] = longueur
        result['exact'] = exact_solution
        result['ratio'] = ratio

    except Exception as e:
        result['error'] = str(e)

    return result


def analyze_results(results):
    """Analyse les résultats et retourne des statistiques détaillées"""
    ratios = [r['ratio'] for r in results.values() if r['success']]

    if not ratios:
        return None

    ratios_sorted = sorted(ratios)
    n = len(ratios)

    stats = {
        'total_instances': len(results),
        'successful': len(ratios),
        'failed': len(results) - len(ratios),
        'mean': sum(ratios) / n,
        'median': ratios_sorted[n // 2] if n % 2 == 1 else (ratios_sorted[n // 2 - 1] + ratios_sorted[n // 2]) / 2,
        'min': min(ratios),
        'max': max(ratios),
        'optimal_count': sum(1 for r in ratios if abs(r - 1.0) < 0.001),
        'better_than_ref': sum(1 for r in ratios if r < 1.0)
    }

    # Quartiles
    stats['q1'] = ratios_sorted[n // 4]
    stats['q3'] = ratios_sorted[3 * n // 4]

    # Catégorisation
    stats['excellent'] = sum(1 for r in ratios if r < 1.05)  # < 5% au-dessus
    stats['good'] = sum(1 for r in ratios if 1.05 <= r < 1.15)
    stats['acceptable'] = sum(1 for r in ratios if 1.15 <= r < 1.3)
    stats['poor'] = sum(1 for r in ratios if r >= 1.3)

    return stats


def print_statistics(stats):
    """Affiche les statistiques de manière formatée"""
    print_section("📊 STATISTIQUES GLOBALES")

    print(f"\n{Colors.BOLD}Instances:{Colors.RESET}")
    print(f"  Total: {stats['total_instances']}")
    print(f"  {Colors.GREEN}✓ Réussies: {stats['successful']}{Colors.RESET}")
    if stats['failed'] > 0:
        print(f"  {Colors.RED}✗ Échouées: {stats['failed']}{Colors.RESET}")

    print(f"\n{Colors.BOLD}Ratio de compétitivité:{Colors.RESET}")

    # Score moyen avec couleur
    mean_color = Colors.GREEN if stats['mean'] < 1.1 else Colors.YELLOW if stats['mean'] < 1.3 else Colors.RED
    print(f"  {Colors.BOLD}{mean_color}Score moyen: {stats['mean']:.4f}{Colors.RESET} ({(stats['mean'] - 1) * 100:.2f}% au-dessus de l'optimal)")

    print(f"  Médiane: {stats['median']:.4f}")
    print(f"  {Colors.GREEN}Minimum: {stats['min']:.4f}{Colors.RESET}")
    print(f"  {Colors.RED}Maximum: {stats['max']:.4f}{Colors.RESET}")
    print(f"  Q1: {stats['q1']:.4f}, Q3: {stats['q3']:.4f}")

    print(f"\n{Colors.BOLD}Distribution des performances:{Colors.RESET}")
    print(f"  {Colors.GREEN}★ Solutions optimales (ratio = 1.0): {stats['optimal_count']}{Colors.RESET}")
    print(f"  {Colors.CYAN}☆ Meilleures que référence (ratio < 1.0): {stats['better_than_ref']}{Colors.RESET}")
    print(f"  {Colors.GREEN}• Excellentes (ratio < 1.05): {stats['excellent']}{Colors.RESET}")
    print(f"  {Colors.BLUE}• Bonnes (1.05 ≤ ratio < 1.15): {stats['good']}{Colors.RESET}")
    print(f"  {Colors.YELLOW}• Acceptables (1.15 ≤ ratio < 1.3): {stats['acceptable']}{Colors.RESET}")
    print(f"  {Colors.RED}• Faibles (ratio ≥ 1.3): {stats['poor']}{Colors.RESET}")


def print_detailed_results(results, show_all=False, show_worst=5, show_best=5):
    """Affiche les résultats détaillés par instance"""

    # Trier par ratio
    sorted_results = sorted(
        [(name, r) for name, r in results.items() if r['success']],
        key=lambda x: x[1]['ratio']
    )

    if show_best > 0:
        print_section(f"🏆 TOP {show_best} MEILLEURES INSTANCES")
        for i, (name, result) in enumerate(sorted_results[:show_best], 1):
            ratio = result['ratio']
            color = Colors.GREEN if ratio <= 1.0 else Colors.CYAN
            medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else f"{i}."
            print(f"{medal} {color}{name:<30}{Colors.RESET} Ratio: {ratio:.4f} (Longueur: {result['length']}, Optimal: {int(result['exact'])})")

    if show_worst > 0:
        print_section(f"⚠️  {show_worst} PIRES INSTANCES (À améliorer)")
        for i, (name, result) in enumerate(reversed(sorted_results[-show_worst:]), 1):
            ratio = result['ratio']
            color = Colors.RED if ratio > 1.3 else Colors.YELLOW
            print(f"{i}. {color}{name:<30}{Colors.RESET} Ratio: {ratio:.4f} (Longueur: {result['length']}, Optimal: {int(result['exact'])})")

    if show_all:
        print_section("📋 TOUS LES RÉSULTATS")
        for name, result in sorted_results:
            if result['success']:
                ratio = result['ratio']
                if ratio <= 1.0:
                    color = Colors.GREEN
                    symbol = "★"
                elif ratio < 1.05:
                    color = Colors.CYAN
                    symbol = "◆"
                elif ratio < 1.15:
                    color = Colors.BLUE
                    symbol = "●"
                elif ratio < 1.3:
                    color = Colors.YELLOW
                    symbol = "○"
                else:
                    color = Colors.RED
                    symbol = "✗"

                print(f"{symbol} {color}{name:<30}{Colors.RESET} Ratio: {ratio:.4f} (Tour: {result['length']}, Opt: {int(result['exact'])})")

    # Instances échouées
    failed = [(name, r) for name, r in results.items() if not r['success']]
    if failed:
        print_section(f"❌ INSTANCES ÉCHOUÉES ({len(failed)})")
        for name, result in failed:
            print(f"{Colors.RED}✗ {name}: {result['error']}{Colors.RESET}")


def print_comparison_table(stats):
    """Affiche un tableau de comparaison avec des benchmarks"""
    print_section("📈 ESTIMATION COMPÉTITIVITÉ")

    mean = stats['mean']

    benchmarks = [
        (1.0, "Optimal (théoriquement impossible en online)", Colors.GREEN),
        (1.05, "Excellent", Colors.GREEN),
        (1.10, "Très bon", Colors.CYAN),
        (1.20, "Bon", Colors.BLUE),
        (1.30, "Acceptable", Colors.YELLOW),
        (1.50, "Faible", Colors.RED),
    ]

    print(f"\n{Colors.BOLD}Votre score: {mean:.4f}{Colors.RESET}\n")

    for threshold, label, color in benchmarks:
        if mean <= threshold:
            print(f"{color}▶ {label:40} (≤ {threshold:.2f}) ← VOUS ÊTES ICI{Colors.RESET}")
            break
        else:
            print(f"  {label:40} (≤ {threshold:.2f})")

    print(f"\n{Colors.BOLD}Estimation classement Codabench:{Colors.RESET}")
    if mean < 1.05:
        print(f"  {Colors.GREEN}{Colors.BOLD}🏆 TOP 10% (excellent algorithme!){Colors.RESET}")
    elif mean < 1.15:
        print(f"  {Colors.CYAN}🎯 TOP 30% (très bon algorithme){Colors.RESET}")
    elif mean < 1.30:
        print(f"  {Colors.BLUE}✓ TOP 50% (bon algorithme){Colors.RESET}")
    else:
        print(f"  {Colors.YELLOW}→ Peut être amélioré{Colors.RESET}")


def main():
    """Fonction principale"""

    # Parser les arguments
    show_all = '--all' in sys.argv or '-a' in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith('-')]

    # Répertoire des instances
    if len(args) > 0:
        input_dir = args[0]
    else:
        input_dir = "Public Data Preliminary Oct 18 2025"

    if not os.path.isdir(input_dir):
        print(f"{Colors.RED}Erreur: Le répertoire '{input_dir}' n'existe pas{Colors.RESET}")
        sys.exit(1)

    # En-tête
    print_header("🚀 TEST DE PERFORMANCE - TSP-RD ONLINE 🚀")

    algo_type = "DÉTERMINISTE" if mon_algo_est_deterministe() else "RANDOMISÉ"
    print(f"{Colors.BOLD}Type d'algorithme:{Colors.RESET} {algo_type}")
    print(f"{Colors.BOLD}Répertoire:{Colors.RESET} {input_dir}")

    # Lister les instances
    instances = sorted([f for f in os.listdir(input_dir) if f.endswith('.inst')])
    print(f"{Colors.BOLD}Nombre d'instances:{Colors.RESET} {len(instances)}")

    # Tester toutes les instances
    print_section("⚙️  EXÉCUTION DES TESTS")

    results = {}
    start_time = time.time()

    for i, instance_file in enumerate(instances, 1):
        instance_path = os.path.join(input_dir, instance_file)
        print(f"[{i}/{len(instances)}] Testing {instance_file}...", end=' ')

        result = test_instance(instance_path)
        results[instance_file] = result

        if result['success']:
            ratio = result['ratio']
            if ratio <= 1.0:
                print(f"{Colors.GREEN}✓ {ratio:.4f}{Colors.RESET}")
            elif ratio < 1.15:
                print(f"{Colors.CYAN}✓ {ratio:.4f}{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}✓ {ratio:.4f}{Colors.RESET}")
        else:
            print(f"{Colors.RED}✗ {result['error']}{Colors.RESET}")

    elapsed_time = time.time() - start_time
    print(f"\n{Colors.BOLD}Temps d'exécution:{Colors.RESET} {elapsed_time:.2f} secondes")

    # Analyser les résultats
    stats = analyze_results(results)

    if stats is None:
        print(f"\n{Colors.RED}Aucune instance n'a été résolue avec succès!{Colors.RESET}")
        sys.exit(1)

    # Afficher les statistiques
    print_statistics(stats)
    print_comparison_table(stats)
    print_detailed_results(results, show_all=show_all, show_worst=5, show_best=5)

    # Résumé final
    print_header("📝 RÉSUMÉ")

    print(f"{Colors.BOLD}Score final estimé: {Colors.GREEN}{Colors.BOLD}{stats['mean']:.4f}{Colors.RESET}")
    print(f"Écart-type: {((stats['max'] - stats['min']) / 2):.4f}")
    print(f"\nCe score est une {Colors.BOLD}estimation{Colors.RESET} basée sur les instances de test locales.")
    print(f"Le score Codabench peut varier selon les instances utilisées.\n")

    # Conseils
    if stats['poor'] > 0:
        print(f"{Colors.YELLOW}💡 Conseil: {stats['poor']} instances ont un ratio ≥ 1.3.{Colors.RESET}")
        print(f"   Analysez ces cas pour améliorer votre algorithme.\n")

    if stats['mean'] < 1.1:
        print(f"{Colors.GREEN}🎉 Excellent travail! Votre algorithme est très compétitif!{Colors.RESET}\n")

    print(f"{Colors.BOLD}Pour voir tous les résultats détaillés:{Colors.RESET}")
    print(f"  python3 test_performance.py --all\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test interrompu par l'utilisateur{Colors.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Erreur fatale: {e}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
