#!/usr/bin/env python3
import subprocess
import os
import sys
import time

MODULES = [
    ("201_sols_vivants", ".dev/maraichage/supports/version HR/Version 169 Sols Vivants.pdf"),
    ("301_realiser_les_planches_de_cultures", ".dev/maraichage/supports/version HR/Version 169 Planches.pdf"),
    ("302_mettre_en_place_lirrigation", ".dev/maraichage/supports/version HR/Version 169 Irrigation.pdf"),
    ("303_realiser_un_compost", ".dev/maraichage/supports/version HR/Version 169 Compost.pdf"),
    ("304_mettre_en_place_les_cultures", ".dev/maraichage/supports/version HR/M04.1 Mettre en place les cultures.pdf"),
    ("305_produire_des_jeunes_plants", ".dev/maraichage/supports/version HR/M6.1. Choisir parmi les techniques de pépinière.pdf"),
    ("306_recolter_conserver_conditionner", ".dev/maraichage/supports/version HR/Récolter Conserver Conditionner.pdf"),
    ("401_proteger_la_sante_des_plantes", ".dev/maraichage/supports/version HR/Santé des plantes.pdf"),
    ("402_planifier_les_cultures", ".dev/maraichage/supports/version HR/Alterner les cultures.pdf"),
    ("403_design_dune_micro_ferme", ".dev/maraichage/supports/version HR/Les principes de design d'une micro-ferme.pdf"),
    ("101_fondamentaux_maraichage_sol_vivant", ".dev/maraichage/supports/Intro - Les fondamentaux du maraîchage bio-intensif en sol vivant.pdf"),
]

def git_sync_and_deploy(module_id):
    print(f"\n>>> Synchronisation Git & Déploiement pour {module_id}...")
    try:
        subprocess.run(["git", "add", f"public/assets/images/maraichage/{module_id}/"], check=True)
        # Check if there are changes to commit
        res = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if res.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"feat(maraichage): illustrations aquarelle terminees pour {module_id}"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            subprocess.run(["git", "checkout", "prod"], check=True)
            subprocess.run(["git", "merge", "main"], check=True)
            subprocess.run(["git", "push", "origin", "prod"], check=True)
            subprocess.run(["git", "checkout", "main"], check=True)
            print(f"    ✓ Git sync réussi pour {module_id}")
        else:
            print(f"    (Aucune nouvelle image à commiter pour {module_id})")
    except Exception as e:
        print(f"    ❌ Erreur lors du push git pour {module_id}: {e}")

def main():
    print("=== DÉMARRAGE DU BATCH GLOBAL MARAÎCHAGE ===")
    for mod_id, pdf_path in MODULES:
        print(f"\n==========================================")
        print(f"DÉBUT DU MODULE : {mod_id}")
        print(f"==========================================")
        
        cmd = ["./scripts/generate_maraichage_images.py", mod_id, pdf_path]
        try:
            subprocess.run(cmd, check=True)
            git_sync_and_deploy(mod_id)
        except Exception as e:
            print(f"❌ Erreur lors de l'exécution du module {mod_id}: {e}")
            time.sleep(5)
            
    print("\n🎉 TOUS LES MODULES DU CURSUS MARAÎCHAGE ONT ÉTÉ TRAITÉS ET SYNCHRONISÉS !")

if __name__ == "__main__":
    main()
