import requests
from concurrent.futures import ThreadPoolExecutor
import time

# --- CONFIGURATION ---
API_URL = "http://192.168.20.4:9000" 
API_KEY = "TA_CLE_API"
THREADS = 15       # On augmente un peu la pression
BATCH_SIZE = 500   
# ---------------------

session = requests.Session()
session.headers.update({
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
})

def delete_alert(alert_id):
    try:
        # Le paramètre force=1 est crucial pour bypasser les index lourds
        url = f"{API_URL}/api/alert/{alert_id}?force=1"
        r = session.delete(url, timeout=15)
        return r.status_code in [200, 204, 404]
    except Exception:
        return False

def run_cleanup():
    total_deleted = 0
    print(f"[*] Démarrage du nettoyage. Cible : lots de {BATCH_SIZE}")
    
    while True:
        # On utilise un filtre de tri pour stabiliser la récupération
        query = {
            "query": [{"_name": "listAlert"}],
            "sort": [{"_createdAt": "asc"}],
            "range": f"0-{BATCH_SIZE}"
        }
        
        try:
            resp = session.post(f"{API_URL}/api/v1/query", json=query, timeout=30)
            
            if resp.status_code != 200:
                print(f"[!] Erreur API {resp.status_code}. Cassandra sature ? Pause 15s...")
                time.sleep(15)
                continue
                
            alerts = resp.json()
            if not alerts or len(alerts) == 0:
                print("[+] Destination atteinte : 0 alertes trouvées. Nettoyage fini !")
                break

            ids = [a['id'] for a in alerts]
            current_batch_size = len(ids)
            print(f"[*] Suppression de {current_batch_size} alertes (Total supprimé : {total_deleted})...")

            with ThreadPoolExecutor(max_workers=THREADS) as executor:
                executor.map(delete_alert, ids)
            
            total_deleted += current_batch_size
            
            # Pause "respiration" pour Cassandra (Crucial vu tes logs précédents)
            # Sans cette pause, Cassandra va retomber en "Unhealthy"
            time.sleep(1) 
            
        except Exception as e:
            print(f"[!] Erreur de connexion : {e}. On réessaie dans 10s...")
            time.sleep(10)

if __name__ == "__main__":
    run_cleanup()
