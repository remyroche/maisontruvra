# Run backend_code_scanner.py, best_practices_audit.py and security_audit.py

#!/bin/bash

# Script pour exécuter tous les audits de qualité et de sécurité du backend.

# --- Fonction pour afficher les en-têtes de section en couleur ---
print_header() {
    echo ""
    echo "========================================================================"
    echo "  $1"
    echo "========================================================================"
    echo ""
}

# --- Début du processus d'audit ---
echo "Lancement des audits automatisés du code backend..."

# --- Audit 1: Scanner de code (Syntaxe et Importations Circulaires) ---
print_header "ANALYSE 1: Vérification de la syntaxe et des importations circulaires"
if [ -f "backend_code_scanner.py" ]; then
    python3 backend_code_scanner.py
else
    echo "[ERREUR] Le script backend_code_scanner.py n'a pas été trouvé."
fi

# --- Audit 2: Audit des meilleures pratiques ---
print_header "ANALYSE 2: Audit des meilleures pratiques de codage"
if [ -f "best_practices_audit.py" ]; then
    python3 best_practices_audit.py
else
    echo "[ERREUR] Le script best_practices_audit.py n'a pas été trouvé."
fi

# --- Audit 3: Audit de sécurité ---
print_header "ANALYSE 3: Audit de sécurité du code"
if [ -f "security_audit.py" ]; then
    python3 security_audit.py
else
    echo "[ERREUR] Le script security_audit.py n'a pas été trouvé."
fi

# --- Fin ---
print_header "Toutes les analyses sont terminées."

