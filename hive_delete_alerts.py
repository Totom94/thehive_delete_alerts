import requests
import time

# --- CONFIGURATION ---
API_URL = "http://127.0.0.1:9000" 
API_KEY = "CLE_API"
BATCH_SIZE = 10  # On descend à 10 pour que l'API réponde instantanément
# ---------------------

session = requests.Session()
session.headers.update({"Authorization": f"Bearer {API_KEY}"})

def run_cleanup():
    print("[*] Mode survie activé. Suppression par petits lots...")
    total = 0
    
    while True:
        try:
            # On demande une liste minuscule pour ne pas faire ramer Elasticsearch
            resp = session.get(f"{API_URL}/api/alert?range=0-{BATCH_SIZE}", timeout=20)
            
            if resp.status_code != 200:
                print(f"[!] Erreur {resp.status_code}. Repos 5s...")
                time.sleep(5)
                continue
                
            alerts = resp.json()
            if not alerts:
                print("[+] Plus rien ! Félicitations.")
                break

            for a in alerts:
                alert_id = a['id']
                del_resp = session.delete(f"{API_URL}/api/alert/{alert_id}?force=1", timeout=10)
                if del_resp.status_code in [200, 204]:
                    total += 1
                    if total % 50 == 0:
                        print(f"[V] {total} alertes supprimées...")
                else:
                    print(f"[!] Echec sur {alert_id}: {del_resp.status_code}")

        except Exception as e:
            print(f"[-] Connexion perdue ({e}). On insiste dans 5s...")
            time.sleep(5)

if __name__ == "__main__":
    run_cleanup()
