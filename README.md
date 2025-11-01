1.	Titre du Projet
Voisins Solidaires est une application d'entraide entre voisins permettant de  publier des annonces d’aide, de consulter celles des autres et de renforcer les liens de proximité grâce à une plateforme simple et conviviale
 
2.	Description du projet
Voisins Solidaires est un projet universitaire développé dans le cadre du DU Data Analytics – Sorbonne Université. Il offre aux utilisateurs la possibilité de :  
•	Publier et consulter des annonces de services  
•	Envoyer et recevoir des demandes relatives aux services
•	Gérer leurs profils et leurs interactions avec les voisins  

3.	Fonctionnalités principales
•	Inscription / Connexion sécurisée (mot de passe chiffré)
•	Publication de services (titre, catégorie, description etc)
•	Recherche des services disponibles
•	Gestion des demandes envoyées et reçues
•	Gestion des Profils utilisateurs 

4.	Technologies utilisées
•	Python  : Langage principal du projet.
•	Streamlit : Création de l’interface web interactive.
•	SQLite : Gestion de la base de données locale.
•	bcrypt : Sécurisation des mots de passe.
•	pandas : Manipulation et affichage des données.
5.	Installation et exécution sur Visual Studio Code
•	Télécharger et installer Python sur l’ordinateur
•	Télécharger et installer Visual Studio Code
•	Installer l’extension Python sur VS Code
•	Télécharger le dossier du projet et ouvrir dans VS Code 
•	Lancer l’application dans VS Code avec la commande streamlit run voisins_sol.py
•	Lien direct pour lancer l’appli : Streamlit ouvre l’application automatiquement dans le navigateur (http://localhost:8501)
6.	Auteurs
•	WilGuy DOISY
•	Fadimatou VEPOUYOUM
Projet universitaire – Sorbonne Université (DU Data Analytics)
7.	Licence
Projet universitaire à usage non commercial.
8.	 Améliorations futures possibles
L'application Voisins Solidaires constitue une base solide, mais plusieurs axes de développement pourraient enrichir l'expérience utilisateur et étendre ses fonctionnalités.
a. Géolocalisation et Cartographie
Actuellement, l'application utilise l'adresse textuelle pour le profil utilisateur, mais ne l'exploite pas pour la recherche.
Recherche par distance : Permettre aux utilisateurs de rechercher des services dans un rayon (par exemple, 1 km, 5 km) autour de leur adresse ou de leur position actuelle.
Affichage sur carte : Intégrer une carte (via Streamlit Folium ou équivalent) pour visualiser les services disponibles dans le quartier.
Validation des adresses : Utiliser une API de géocodage pour normaliser et valider les adresses saisies.
b.  Communication et Notifications
Les échanges se font actuellement hors plateforme (via email/téléphone affichés après la demande).
Système de messagerie interne : Mettre en place un outil de chat ou de messagerie privé dans l'application pour que le demandeur et le proposeur puissent discuter sans partager leurs contacts personnels immédiatement.
Notifications en temps réel : Envoyer des notifications (via Streamlit toast ou e-mail/SMS) lorsqu'une demande est reçue, acceptée, ou refusée.
 c.  Améliorations techniques et UX
Téléchargement d'images : Permettre aux utilisateurs d'ajouter une photo à leurs annonces de service ou une photo de profil (nécessite de gérer le stockage des fichiers, par exemple via S3 ou dans un dossier spécifique).
Sécurité des mots de passe : Imposer des règles de complexité des mots de passe plus strictes (minuscules, majuscules, chiffres, symboles).
Séparation des rôles : Ajouter des fonctionnalités spécifiques pour un administrateur (modérer les annonces, gérer les utilisateurs).
