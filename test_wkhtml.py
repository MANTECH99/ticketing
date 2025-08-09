import subprocess

def check_wkhtmltopdf():
    try:
        # Vérifier si wkhtmltopdf est accessible
        path = subprocess.check_output(["which", "wkhtmltopdf"]).decode().strip()
        print(f"wkhtmltopdf trouvé : {path}")

        # Tester une conversion simple
        test_html = "/tmp/test.html"
        test_pdf = "/tmp/test.pdf"

        with open(test_html, "w") as f:
            f.write("<h1>Hello PDF</h1><p>Ceci est un test depuis Railway</p>")

        subprocess.run(["wkhtmltopdf", test_html, test_pdf], check=True)
        print("✅ PDF généré avec succès :", test_pdf)
    except subprocess.CalledProcessError as e:
        print("❌ Erreur lors de l'exécution :", e)
    except FileNotFoundError:
        print("❌ wkhtmltopdf n'est pas installé dans ce conteneur.")

if __name__ == "__main__":
    check_wkhtmltopdf()
