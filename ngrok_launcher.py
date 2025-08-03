import subprocess
import time
import requests
import json

# Étape 1 : Lancer ngrok sur le port 8000
print("🔌 Démarrage de ngrok...")
ngrok_process = subprocess.Popen(["ngrok", "http", "8000"])

# Étape 2 : Attendre que l'interface web soit disponible
time.sleep(3)  # laisser à ngrok le temps de démarrer

# Étape 3 : Obtenir le lien public via l'API de Ngrok
try:
    response = requests.get("http://127.0.0.1:4040/api/tunnels")
    tunnels = response.json()["tunnels"]

    public_url = None
    for tunnel in tunnels:
        if tunnel["proto"] == "https":
            public_url = tunnel["public_url"]
            break

    if public_url:
        print(f"🌍 URL publique Ngrok : {public_url}")
    else:
        print("❌ Impossible de récupérer l'URL publique Ngrok (aucun tunnel HTTPS trouvé).")

except requests.exceptions.ConnectionError:
    print("❌ Impossible de se connecter à l'interface API de Ngrok. Le processus est-il lancé correctement ?")

except Exception as e:
    print(f"❌ Erreur : {e}")

print("🔁 Ngrok est actif. Appuyez sur Ctrl+C pour arrêter.")
try:
    ngrok_process.wait()
except KeyboardInterrupt:
    print("\n⛔ Arrêt de ngrok...")
    ngrok_process.terminate()
