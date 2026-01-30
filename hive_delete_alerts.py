import requests
from concurrent.futures import ThreadPoolExecutor
import time

# --- CONFIGURATION ---
API_URL = "http://192.168.20.4:9000"
API_KEY = "CLE_API"
THREADS = 10      # Vitesse x10
BATCH_SIZE = 500  # Sécurité pour la RAM 
# ---------------------

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {API_KEY}"})

def delete_alert(alert_id):
    try:
        url = f"{API_URL}/api/alert/{alert_id}?force=1"
        r = session.delete(url, timeout=5)
        return r.status_code in [200, 204, 404]
    except:
        return False

def run_cleanup():
    while True:
        print(f"[*] Récupération d'un lot de {BATCH_SIZE} alertes...")
        # On demande un petit lot pour ne pas faire crasher Java
        resp = session.get(f"{API_URL}/api/alert?range=0-{BATCH_SIZE}")
        
        if resp.status_code != 200:
            print("[!] Erreur API, pause de 10s...")
            time.sleep(10)
            continue
            
        alerts = resp.json()
        if not alerts:
            print("[+] Plus aucune alerte. Travail terminé !")
            break

        ids = [a['id'] for a in alerts]
        print(f"[*] Suppression de {len(ids)} alertes en cours...")

        # Exécution parallèle sur le lot actuel
        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            executor.map(delete_alert, ids)
        
        print(f"[✓] Lot traité. Nettoyage de la RAM...")
        time.sleep(1) # Pause ElasticSearch

if __name__ == "__main__":
    run_cleanup()
