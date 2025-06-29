import os
import ast
import logging
import traceback
from collections import defaultdict

# Configure le logging pour afficher les informations de manière claire
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

# Le répertoire à analyser
BACKEND_DIR = 'backend'

class DependencyVisitor(ast.NodeVisitor):
    """
    Un visiteur d'AST qui parcourt le code pour trouver toutes les instructions
    d'importation et construire les dépendances d'un module.
    """
    def __init__(self, current_module_path):
        self.dependencies = set()
        self.current_module_path = current_module_path
        # Convertit le chemin du fichier en un nom de module Python (ex: 'backend/services/user_service.py' -> 'backend.services.user_service')
        self.current_module_name = self._path_to_module(current_module_path)

    def _path_to_module(self, path):
        """Convertit un chemin de fichier en nom de module Python."""
        path = os.path.splitext(path)[0]
        return path.replace(os.path.sep, '.')

    def visit_Import(self, node):
        """Visite les instructions 'import module'."""
        for alias in node.names:
            self.dependencies.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        """Visite les instructions 'from module import ...'."""
        # Résout le nom du module importé (ex: ..utils -> backend.utils)
        module_name = node.module
        if node.level > 0:
            # Gère les importations relatives (ex: 'from . import base')
            # Construit le chemin absolu à partir du chemin relatif
            parts = self.current_module_name.split('.')
            base_path = '.'.join(parts[:-(node.level)])
            if module_name:
                module_name = f"{base_path}.{module_name}"
            else:
                module_name = base_path
        
        if module_name:
            self.dependencies.add(module_name)
        self.generic_visit(node)

def find_python_files(directory):
    """Trouve tous les fichiers .py dans un répertoire et ses sous-dossiers."""
    python_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    return python_files

def check_syntax(file_path):
    """Vérifie la syntaxe d'un fichier Python en utilisant AST."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
            ast.parse(source_code, filename=file_path)
        return True, None
    except SyntaxError as e:
        return False, f"Erreur de syntaxe dans {file_path} à la ligne {e.lineno}: {e.msg}"
    except Exception as e:
        return False, f"Erreur inattendue lors de l'analyse de {file_path}: {e}\n{traceback.format_exc()}"

def find_circular_imports(dependency_graph):
    """
    Trouve les importations circulaires dans un graphe de dépendances en utilisant
    un algorithme de parcours en profondeur (DFS).
    """
    cycles = []
    # `path` suit la pile de récursion actuelle, `visited` suit tous les nœuds déjà visités.
    path = set()
    visited = set()

    def visit(node):
        if node in visited:
            return
        
        path.add(node)
        visited.add(node)
        
        for neighbour in dependency_graph.get(node, []):
            if neighbour in path:
                # Cycle détecté !
                try:
                    # Tente de trouver le début du cycle pour un affichage plus clair
                    cycle_start_index = list(path).index(neighbour)
                    cycle = list(path)[cycle_start_index:] + [neighbour]
                    # Normalise le cycle pour éviter les doublons (ex: A->B->A et B->A->B)
                    sorted_cycle = tuple(sorted(cycle[:-1]))
                    if sorted_cycle not in [tuple(sorted(c[:-1])) for c in cycles]:
                        cycles.append(cycle)
                except ValueError: # Au cas où
                     cycles.append(list(path) + [neighbour])

            visit(neighbour)
        
        path.remove(node)

    for node in list(dependency_graph.keys()):
        visit(node)
        
    return cycles

def main():
    """Fonction principale pour exécuter l'analyseur de code."""
    logging.info(f"Début de l'analyse du répertoire '{BACKEND_DIR}'...")
    
    python_files = find_python_files(BACKEND_DIR)
    if not python_files:
        logging.warning("Aucun fichier Python n'a été trouvé.")
        return

    # --- Étape 1: Vérification de la syntaxe ---
    logging.info("\n" + "="*20 + " ÉTAPE 1: VÉRIFICATION DE LA SYNTAXE " + "="*20)
    syntax_errors = []
    for file_path in python_files:
        is_valid, error_msg = check_syntax(file_path)
        if not is_valid:
            syntax_errors.append(error_msg)
            
    if syntax_errors:
        logging.error(f"{len(syntax_errors)} erreur(s) de syntaxe trouvée(s) :")
        for error in syntax_errors:
            logging.error(f"  - {error}")
    else:
        logging.info("Aucune erreur de syntaxe détectée. Tous les fichiers sont valides.")

    # --- Étape 2: Analyse des dépendances et recherche de cycles ---
    logging.info("\n" + "="*20 + " ÉTAPE 2: DÉTECTION DES IMPORTATIONS CIRCULAIRES " + "="*20)
    dependency_graph = defaultdict(set)
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                tree = ast.parse(source, filename=file_path)
                visitor = DependencyVisitor(file_path)
                visitor.visit(tree)
                
                module_name = visitor._path_to_module(file_path)
                # Filtre pour ne garder que les dépendances internes au projet
                internal_deps = {dep for dep in visitor.dependencies if dep.startswith(BACKEND_DIR)}
                if internal_deps:
                    dependency_graph[module_name].update(internal_deps)
        except Exception as e:
            logging.error(f"Impossible d'analyser les dépendances pour {file_path}: {e}")
            
    circular_imports = find_circular_imports(dependency_graph)

    if circular_imports:
        logging.error(f"{len(circular_imports)} importation(s) circulaire(s) détectée(s) :")
        for i, cycle in enumerate(circular_imports):
            logging.error(f"  Cycle {i+1}: {' -> '.join(cycle)}")
    else:
        logging.info("Aucune importation circulaire détectée.")

    logging.info("\n" + "="*20 + " ANALYSE TERMINÉE " + "="*20)


if __name__ == '__main__':
    main()

