import requests
from bs4 import BeautifulSoup
import csv

def scrape_page(url, write_header=False):
    # Faire une requête HTTP pour obtenir le contenu de la page
    response = requests.get(url)

    # Vérifier si la requête a réussi
    if response.status_code == 200:
        # Parser le contenu HTML de la page
        soup = BeautifulSoup(response.content, 'html.parser')
        table = soup.find('table', class_='ad-list')

        if table:
            # Ouvrir un fichier CSV en mode écriture avec un encodage spécifique
            mode = 'a' if not write_header else 'w'
            with open('donnees.csv', mode, newline='', encoding='utf-8-sig') as csvfile:
                # Créer un objet writer pour écrire dans le fichier CSV
                csvwriter = csv.writer(csvfile)

                # Si write_header est True, écrire l'en-tête
                if write_header:
                    # Parcourir les lignes du tableau pour récupérer l'en-tête
                    header_row = []
                    for header_cell in table.find('tr').find_all(['th']):
                        header_row.append(header_cell.get_text(strip=True))
                    # Écrire l'en-tête dans le fichier CSV
                    csvwriter.writerow(header_row)

                # Parcourir les lignes du tableau
                for row in table.find_all('tr')[1:]:  # Commencer à partir de la deuxième ligne pour éviter l'en-tête
                    # Créer une liste pour stocker les données de chaque ligne
                    row_data = []

                    # Parcourir les cellules de chaque ligne
                    for cell in row.find_all(['td', 'th']):
                        # Si la cellule contient une liste d'aircraft-tree
                        if cell.find('ul', class_='aircraft-tree'):
                            # Extraire le TC Holder de la 5e colonne
                            tc_holder_element = cell.find('li', class_='tc_holder')
                            tc_holder_text = tc_holder_element.contents[0].strip()
                            # Ajouter TC Holder dans une colonne
                            row_data.append(tc_holder_text) # row_data = [a,b, tc_holder_text]
                            # Extraire les types de la 5e colonne
                            types = [li.get_text(strip=True) for li in cell.find_all('li', class_='type')] #types = [A319 A320]
                            # Ajouter les types dans une colonne (séparés par des virgules)
                            row_data.append(', '.join(types)) # row_data = [a,b, tc_holder_text, "A319, A320"]
                        # Si la cellule contient une liste d'attachments
                        elif cell.find('ul', class_='attachments-small'):
                            # Extraire les liens des fichiers
                            file_links = [a['href'] for a in cell.find_all('a')]
                            # Ajouter les liens comme colonnes séparées
                            row_data.extend(file_links)
                        else:
                            # Ajouter le texte de la cellule à la liste
                            row_data.append(cell.get_text(strip=True))

                    # Écrire la liste dans le fichier CSV
                    csvwriter.writerow(row_data)

            print(f"Les données de la page {url} ont été écrites dans le fichier CSV.")
        else:
            print(f"Aucun tableau avec la classe 'ad-list' trouvé sur la page {url}.")
    else:
        print(f"Erreur lors de la requête : {response.status_code}")

# Demander à l'utilisateur le nombre de pages à charger
num_pages = int(input("Combien de pages souhaitez-vous charger? "))
base_url = 'https://ad.easa.europa.eu/page-'

# Générer dynamiquement les URL en fonction du nombre spécifié
pages_urls = [f'{base_url}{i}' for i in range(1, num_pages + 1)] # [https://ad.easa.europa.eu/page-1 https://ad.easa.europa.eu/page-2 https://ad.easa.europa.eu/page-3]

# Appeler la fonction scrape_page pour chaque URL
for i, page_url in enumerate(pages_urls):
    scrape_page(page_url, write_header=(i == 0))  # Écrire l'en-tête uniquement pour la première page