import requests
import sys

# --- CONFIGURATION ---
API_URL = "http://192.168.20.4:9000"
API_KEY = "CLE_API"
# ---------------------

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def get_all_alert_ids():
    print(f"[*] Récupération de la liste des alertes sur {API_URL}...")
    # On demande toutes les alertes (range=all)
    url = f"{API_URL}/api/alert?range=all"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        alerts = response.json()
        return [a['id'] for a in alerts]
    except Exception as e:
        print(f"[!] Erreur lors de la récupération : {e}")
        return []

def delete_alerts(ids):
    total = len(ids)
    print(f"[*] {total} alertes trouvées. Début de la suppression...")
    
    count = 0
    for alert_id in ids:
        # On ajoute ?force=1 comme tu l'as trouvé
        del_url = f"{API_URL}/api/alert/{alert_id}?force=1"
        try:
            res = requests.delete(del_url, headers=headers)
            if res.status_code in [200, 204]:
                count += 1
                if count % 100 == 0:
                    print(f"[>] Progression : {count}/{total} supprimées...")
            else:
                print(f"[!] Échec pour {alert_id}: {res.status_code}")
        except Exception as e:
            print(f"[!] Erreur réseau pour {alert_id}: {e}")

    print(f"\n[+] Terminé ! {count} alertes supprimées.")

if __name__ == "__main__":
    ids = get_all_alert_ids()
    if ids:
        confirm = input(f"!!! ATTENTION : Supprimer {len(ids)} alertes ? (y/n) : ")
        if confirm.lower() == 'y':
            delete_alerts(ids)
        else:
            print("Opération annulée.")
    else:
        print("Aucune alerte trouvée.")
