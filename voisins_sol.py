"""
Projet python
DU Sorbonne Data Analytics
Présenté par: WilGuy DOISY et Fadimatou VEPOUYOUM

APPLICATION VOISINS SOLIDAIRES
==============================
Plateforme d'entraide de quartier pour partager des services et du matériel

STRUCTURE DU MENU :
- Accueil : Page d'accueil et présentation
- S'inscrire : Création de compte utilisateur
- Se connecter : Authentification
- Mot de passe oublié : Réinitialisation du mot de passe 
- Proposer un service : Création d'annonces
- Trouver un service : Recherche et consultation des services
- Mon compte : Gestion du profil et des services
"""

import streamlit as st
import sqlite3
import bcrypt  # type: ignore
import pandas as pd
from datetime import datetime

# ==================== CONFIGURATION DE L'APPLICATION ====================

st.set_page_config(
    page_title="Voisins Solidaires",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styles CSS personnalisés pour masquer la barre latérale Streamlit et définir un fond
st.markdown("""
    <style>  
        [data-testid="stSidebar"], [data-testid="collapsedControl"] {display: none;}
        .stApp {background-color: #B3E5FC;}
        .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, 
        .stMarkdown h4 a, .stMarkdown h5 a, .stMarkdown h6 a {display: none !important;}

        /* 1. Largeur de page */
        .block-container { 
            #max-width: 90% !important; 
            margin: auto !important; 
        }
        /* 2. Couleur des titres de h1-h6 */
        h1, h2, h3, h4, h5, h6 { 
            color: #0020CA !important; 
        }
        /* 3. Couleur du texte paragraphes, listes, captions */
        .stMarkdown p, .stMarkdown li, .stMarkdown { 
             color: #000000 !important; 
        }
        .stCaption {
            color: #000000 !important;
        }
        /* 4. Texte des formulaires labels  */
        label { 
            color: #000000 !important; 
        }
        
        /* 5. Le fond des textes input  */
        [data-testid="stTextInput"] input, 
        [data-testid="stTextArea"] textarea,
        [data-testid="stNumberInput"] input,
        [data-testid="stDateInput"] input {
            background-color: #f0f0f0 !important;
            color: #000000 !important; 
        }
        /* 6. Selectbox  */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            background-color: #f0f0f0 !important;
        }
        /* 7. Texte dans le Selectbox */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div > div {
             color: #000000 !important;
        }
        
    </style>
""", unsafe_allow_html=True)

# ==================== GESTION DE LA BASE DE DONNÉES SQLITE3====================

def init_database():
    """
    Initialise la base de données SQLite avec les 3 tables nécessaires.
    Utilise 'with sqlite3.connect' pour garantir la fermeture de la connexion.
    """
    with sqlite3.connect('voisins.db') as conn:
        c = conn.cursor()
        
        # Table utilisateurs - Gère les inscriptions et les connexions
        c.execute('''CREATE TABLE IF NOT EXISTS utilisateurs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mot_de_passe TEXT NOT NULL,
            adresse TEXT,
            telephone TEXT,
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )''')
        
        # Table services - pour "proposer un service" et "trouver un service"
        c.execute('''CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titre TEXT NOT NULL,
            categorie TEXT NOT NULL,
            description TEXT NOT NULL,
            type_service TEXT NOT NULL,
            prix REAL,
            utilisateur_id INTEGER,
            disponible INTEGER DEFAULT 1,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (utilisateur_id) REFERENCES utilisateurs (id)
        )''')
        
        # Table demandes - Gère les demandes de service dans "Mon compte"
        c.execute('''CREATE TABLE IF NOT EXISTS demandes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_id INTEGER,
            demandeur_id INTEGER,
            date_demande TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_souhaitee TEXT,
            statut TEXT DEFAULT 'en_attente', -- Statuts possibles: en_attente, acceptee, refusee
            message TEXT,
            FOREIGN KEY (service_id) REFERENCES services (id),
            FOREIGN KEY (demandeur_id) REFERENCES utilisateurs (id)
        )''')
        
        conn.commit()

# Gestion des mots de passe cryptés avec bcrypt
def hash_password(password):
    salt = bcrypt.gensalt()
    # Le hash est encodé en utf-8 pour le stockage en TEXT dans SQLite
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# ---------- FONCTIONS POUR "S'INSCRIRE" ----------

def creer_utilisateur(nom, prenom, email, mot_de_passe, adresse, telephone): #Crée un nouveau compte utilisateur dans la base de données.
    
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO utilisateurs (nom, prenom, email, mot_de_passe, adresse, telephone)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (nom, prenom, email, hash_password(mot_de_passe), adresse, telephone))
            conn.commit()
        return True, "Inscription réussie !"
    except sqlite3.IntegrityError:
        return False, "Cet email est déjà utilisé."
    except Exception as e:
        return False, f"Erreur : {str(e)}"

# ---------- FONCTIONS POUR "SE CONNECTER" ----------

def verifier_connexion(email, mot_de_passe):
    """
    Vérifie les identifiants de connexion avec bcrypt.
    Retourne les données utilisateur si la connexion est réussie, sinon None.
    """
    user_hash = None
    # 1. Récupérer le hash stocké
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            c.execute('SELECT mot_de_passe FROM utilisateurs WHERE email = ?', (email,))
            result = c.fetchone()
            if result:
                user_hash = result[0]
    except Exception:
        return None # Erreur de connexion DB

    if user_hash:
        try:
            # 2. Comparer le mot de passe fourni avec le hash stocké
            if bcrypt.checkpw(mot_de_passe.encode('utf-8'), user_hash.encode('utf-8')):
                # 3. Si OK, récupérer l'utilisateur complet
                with sqlite3.connect('voisins.db') as conn:
                    c = conn.cursor()
                    c.execute('SELECT * FROM utilisateurs WHERE email = ?', (email,))
                    user = c.fetchone()
                    return user
        except ValueError:
            return None # Hash invalide
    return None

# ---------- FONCTION POUR RÉINITIALISER LE MOT DE PASSE ----------

def reinitialiser_mot_de_passe(email, telephone, nouveau_mot_de_passe): # Vérifie l'email et le téléphone pour l'identité, puis met à jour le mot de passe haché.
  
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            
            # 1. Vérifier si l'utilisateur existe et si le téléphone correspond
            c.execute('SELECT id FROM utilisateurs WHERE email = ? AND telephone = ?', (email, telephone))
            user_id = c.fetchone()
            
            if user_id:
                # 2. Hacher le nouveau mot de passe
                nouveau_hash = hash_password(nouveau_mot_de_passe)
                
                # 3. Mettre à jour le mot de passe
                c.execute('UPDATE utilisateurs SET mot_de_passe = ? WHERE id = ?', (nouveau_hash, user_id[0]))
                conn.commit()
                return True, "Votre mot de passe a été réinitialisé avec succès !"
            else:
                return False, "Email ou numéro de téléphone non reconnu."
    except Exception as e:
        return False, f"Erreur lors de la réinitialisation : {str(e)}"

# ---------- FONCTIONS POUR "PROPOSER UN SERVICE" ----------

def creer_service(titre, categorie, description, type_service, prix, utilisateur_id):
    # Crée une nouvelle annonce de service.
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO services (titre, categorie, description, type_service, prix, utilisateur_id)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (titre, categorie, description, type_service, prix, utilisateur_id))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erreur DB : {e}")
        return False

# ---------- FONCTIONS POUR "TROUVER UN SERVICE" ----------

def obtenir_services(categorie=None, type_service=None):
    with sqlite3.connect('voisins.db') as conn:
        # Jointure avec la table utilisateurs pour afficher le nom du proposant
        query = '''SELECT s.*, u.prenom, u.nom, u.email, u.telephone 
                   FROM services s JOIN utilisateurs u ON s.utilisateur_id = u.id 
                   WHERE s.disponible = 1''' # N'affiche que les services marqués 'disponible'
        params = []
        
        # Appliquer les filtres de recherche
        if categorie and categorie != "Toutes":
            query += ' AND s.categorie = ?'
            params.append(categorie)
        if type_service and type_service != "Tous":
            query += ' AND s.type_service = ?'
            params.append(type_service)
        
        query += ' ORDER BY s.date_creation DESC'
        df = pd.read_sql_query(query, conn, params=params)
        return df

# Crée une demande de réservation pour un service.
def creer_demande(service_id, demandeur_id, date_souhaitee, message):
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO demandes (service_id, demandeur_id, date_souhaitee, message)
                         VALUES (?, ?, ?, ?)''',
                      (service_id, demandeur_id, date_souhaitee, message))
            conn.commit()
        return True
    except Exception as e:
        st.error(f"Erreur lors de la création de la demande: {e}")
        return False

# ---------- FONCTIONS POUR "MON COMPTE" ----------

def obtenir_mes_services(utilisateur_id):
    # Récupère les services proposés par l'utilisateur connecté.
    with sqlite3.connect('voisins.db') as conn:
        df = pd.read_sql_query(
            'SELECT * FROM services WHERE utilisateur_id = ? ORDER BY date_creation DESC',
            conn, params=(utilisateur_id,)
        )
        return df

def mettre_a_jour_disponibilite_service(service_id, disponible):
    # Met à jour la disponibilité d'un service (0=non disponible, 1=disponible).
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            c.execute('''UPDATE services SET disponible = ? WHERE id = ?''', 
                      (disponible, service_id))
            conn.commit()
        return True
    except Exception:
        return False

def obtenir_demandes_recues(utilisateur_id):
    # Récupère les demandes reçues pour les services de l'utilisateur (celui qui propose).
    with sqlite3.connect('voisins.db') as conn:
        query = '''SELECT d.*, s.titre, u.prenom, u.nom, u.email, u.telephone
                   FROM demandes d
                   JOIN services s ON d.service_id = s.id
                   JOIN utilisateurs u ON d.demandeur_id = u.id
                   WHERE s.utilisateur_id = ?
                   ORDER BY d.date_demande DESC'''
        df = pd.read_sql_query(query, conn, params=(utilisateur_id,))
        return df

def obtenir_mes_demandes_initiees(demandeur_id):
    """
    Récupère les demandes faites par l'utilisateur (en tant que demandeur).
    """
    with sqlite3.connect('voisins.db') as conn:
        query = '''SELECT d.*, s.titre, u.prenom, u.nom, u.email, u.telephone
                   FROM demandes d
                   JOIN services s ON d.service_id = s.id
                   JOIN utilisateurs u ON s.utilisateur_id = u.id
                   WHERE d.demandeur_id = ?
                   ORDER BY d.date_demande DESC'''
        df = pd.read_sql_query(query, conn, params=(demandeur_id,))
        return df

def mettre_a_jour_statut_demande(demande_id, nouveau_statut):
    """Met à jour le statut d'une demande de service (en_attente, acceptee, refusee)."""
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            c.execute('''UPDATE demandes SET statut = ? WHERE id = ?''', 
                      (nouveau_statut, demande_id))
            conn.commit()
        return True
    except Exception as e:
        return False

def mettre_a_jour_utilisateur(user_id, nom, prenom, email, adresse, telephone):
   # Met à jour les informations de profil de l'utilisateur.
    try:
        with sqlite3.connect('voisins.db') as conn:
            c = conn.cursor()
            c.execute('''UPDATE utilisateurs 
                         SET nom = ?, prenom = ?, adresse = ?, telephone = ?
                         WHERE id = ?''',
                      (nom, prenom, adresse, telephone, user_id))
            conn.commit()
        return True, "Profil mis à jour avec succès !"
    except sqlite3.IntegrityError:
        return False, "Cet email est déjà utilisé par un autre compte."
    except Exception as e:
        return False, f"Erreur de mise à jour : {str(e)}"

# ==================== CONSTANTES DE L'APPLICATION ====================

# Catégories de services disponibles
CATEGORIES = ["Jardinage", "Bricolage", "Courses", "Garde d'enfants", 
              "Garde d'animaux", "Aide aux devoirs", "Covoiturage", "Aide à domicile", "Autre"]

# Types de services proposés
TYPES_SERVICE = ["Service gratuit", "Location payante", "Service rémunéré", "Échange"]

# ==================== PAGES DE L'APPLICATION ====================

# ========== PAGE : ACCUEIL ==========

def page_accueil():
    # Page d'accueil présentant la plateforme et ses fonctionnalités
    col_gauche, col_centre, col_droite = st.columns([1, 3, 1])
    
    with col_centre:
        st.markdown("<h1 style='text-align: center; color: #0020CA;'>🏘️ Voisins Solidaires</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #0020CA;'>Partagez, Échangez, Entraidez-vous !</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <div style='text-align: center;'>
        Redécouvrez le plaisir de la vie de quartier ! Voisins Solidaires vous connecte 
        avec vos voisins pour partager des outils, échanger des services et créer du lien. 
        Économisez, simplifiez-vous la vie et tissez des liens authentiques à deux pas de chez vous.
        <br><br>
        Besoin d'une perceuse pour quelques heures ? <br>Envie de proposer vos talents de 
        bricolage ? <br>À la recherche d'une aide pour les devoirs ou la garde de votre animal ? <br>
        Plus besoin d'acheter du matériel que vous n'utiliserez qu'une fois par an. 
        Plus besoin de chercher loin pour trouver de l'aide. 
        <br>
        <strong>Vos voisins sont là ! Ensemble, on est plus forts et la vie est plus simple.</strong>
        </div><br>
        """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<h3 style='text-align: center;'> Outils & Équipements </h3>", unsafe_allow_html=True)
        st.write("Prêtez ou empruntez du matériel de jardinage, bricolage, et plus encore.")
    with col2:
        st.markdown("<h3 style='text-align: center;'> Services </h3>", unsafe_allow_html=True)
        st.write("Courses, garde d'enfants, aide aux devoirs, promenade d'animaux...")
    with col3:
        st.markdown("<h3 style='text-align: center;'> Solidarité </h3>", unsafe_allow_html=True)
        st.write("Créez du lien avec vos voisins et construisez une communauté entraide.")
    
    st.markdown("---")
    
    col_gauche_content, col_droite_content = st.columns(2)
    
    with col_gauche_content:
        with st.container(border=True): # Utilisation de st.container pour encadrer et structurer l'information
             st.markdown("""
             ### Comment ça marche ?                     
            1. **Inscrivez-vous** gratuitement en quelques clics 
            2. **Proposez vos services** ou ce que vous pouvez prêter
            3. **Trouvez** ce dont vous avez besoin près de chez vous 
            4. **Contactez** vos voisins directement 
            5. **Partagez** et économisez ensemble ! 
            
            """)
    
    with col_droite_content:
        with st.container(border=True):  # Utilisation de st.container pour encadrer et structurer l'information
            st.markdown("""
            ### Catégories disponibles
            - 🌱 Jardinage (tondeuse, taille-haie, outils...)
            - 🔧 Bricolage (perceuse, échelle, outils...)
            - 🛒 Courses et commissions
            - 👶 Garde d'enfants
            - 🐕 Garde d'animaux
            - 📚 Aide aux devoirs
            - 🚗 Covoiturage
            - 🏠 Aide à domicile
            """)
    
    if not st.session_state.get('utilisateur'):
        st.markdown("---")
        col_g_btn, col_c_btn, col_d_btn = st.columns([1, 1, 1])
        with col_c_btn:
            st.info("👉 Cliquez ci-dessous pour commencer !")
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📝 S'inscrire", use_container_width=True):
                    st.session_state.page_navigation = "S'inscrire"
                    st.rerun()
            with col_btn2:
                if st.button("🔐 Se connecter", use_container_width=True):
                    st.session_state.page_navigation = "Se connecter"
                    st.rerun()

# ========== PAGE : S'INSCRIRE  ==========

def page_inscription():
    """Formulaire d'inscription pour créer un nouveau compte utilisateur."""
    st.title("📝 Inscription")

    with st.container(border=True): # Utilisation de st.container pour encadrer et structurer l'information
        with st.form("formulaire_inscription"):
            col1, col2 = st.columns(2)
            with col1:
                nom = st.text_input("Nom *")
                prenom = st.text_input("Prénom *")
                email = st.text_input("Email *")
            with col2:
                mot_de_passe = st.text_input("Mot de passe *", type="password")
                confirmation = st.text_input("Confirmer le mot de passe *", type="password")
                telephone = st.text_input("Téléphone")
            
            adresse = st.text_area("Adresse")
            submitted = st.form_submit_button("S'inscrire")
            
            if submitted:
                if not all([nom, prenom, email, mot_de_passe, confirmation]):
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                elif mot_de_passe != confirmation:
                    st.error("Les mots de passe ne correspondent pas")
                elif len(mot_de_passe) < 6:
                    st.error("Le mot de passe doit contenir au moins 6 caractères")
                else:
                    success, message = creer_utilisateur(nom, prenom, email, mot_de_passe, adresse, telephone)
                    if success:
                        st.success(message)
                        st.info("Vous pouvez maintenant vous connecter !")
                    else:
                        st.error(message)

# ========== PAGE : SE CONNECTER ==========

def page_connexion():
    """Formulaire d'authentification et lien vers 'Mot de passe oublié'."""
    st.title("🔐 Connexion")
    with st.container(border=True):   # Utilisation de st.container pour encadrer le formulaire
        with st.form("formulaire_connexion"):
            email = st.text_input("Email")
            mot_de_passe = st.text_input("Mot de passe", type="password")
            submitted = st.form_submit_button("Se connecter")
            
            if submitted:
                user = verifier_connexion(email, mot_de_passe)
                if user:
                    # Stockage des données utilisateur dans l'état de session
                    st.session_state.utilisateur = {
                        'id': user[0], 'nom': user[1], 'prenom': user[2],
                        'email': user[3], 'adresse': user[5], 'telephone': user[6]
                    }
                    st.success(f"Bienvenue {user[2]} {user[1]} !")
                    st.session_state.page_navigation = "Mon compte"  # Rédirection vers la page "Mon compte" après connexion
                    st.rerun()
                else:
                    st.error("Email ou mot de passe incorrect")
                
    # Bouton pour naviguer vers la page de réinitialisation
    if st.button("Mot de passe oublié ?"):
        st.session_state.page_navigation = "Mot de passe oublié"
        st.rerun()

# ========== PAGE : MOT DE PASSE OUBLIÉ  ==========

def page_mot_de_passe_oublie():
    """Page de réinitialisation du mot de passe."""
    st.title("❓ Mot de passe oublié")
    st.info("Veuillez fournir votre email et votre numéro de téléphone pour vérification.")
    
    with st.container(border=True): # Utilisation de st.container pour encadrer le formulaire
        with st.form("formulaire_reinitialisation"):
            email = st.text_input("Votre Email")
            telephone = st.text_input("Votre Téléphone")
            nouveau_mot_de_passe = st.text_input("Nouveau mot de passe", type="password")
            confirmation = st.text_input("Confirmer le nouveau mot de passe", type="password")
            
            submitted = st.form_submit_button("Réinitialiser le mot de passe")
            
            if submitted:
                if not all([email, telephone, nouveau_mot_de_passe, confirmation]):
                    st.error("Veuillez remplir tous les champs.")
                elif nouveau_mot_de_passe != confirmation:
                    st.error("Les mots de passe ne correspondent pas.")
                elif len(nouveau_mot_de_passe) < 6:
                    st.error("Le mot de passe doit contenir au moins 6 caractères.")
                else:
                    success, message = reinitialiser_mot_de_passe(email, telephone, nouveau_mot_de_passe)
                    if success:
                        st.success(message)
                        # Offre un bouton pour revenir à la connexion
                        if st.button("Retour à la connexion"):
                            st.session_state.page_navigation = "Se connecter"
                            st.rerun()
                    else:
                        st.error(message)

# ========== PAGE : PROPOSER UN SERVICE  ==========

def page_proposer_service():
    """Formulaire pour créer une nouvelle annonce de service."""
    st.title("➕ Proposer un service")
    
    if not st.session_state.get('utilisateur'):
        st.warning("Vous devez être connecté pour proposer un service")
        return
    
    with st.container(border=True):
        with st.form("formulaire_service"):
            titre = st.text_input("Titre de l'annonce *")
            categorie = st.selectbox("Catégorie *", CATEGORIES)
            type_service = st.selectbox("Type de service *", TYPES_SERVICE)
            
            prix = 0.0
            if type_service in ["Location payante", "Service rémunéré"]:
                prix = st.number_input("Prix (€/heure ou €/jour)", min_value=0.0, step=0.5)
            
            description = st.text_area("Description détaillée *", height=150)
            submitted = st.form_submit_button("Publier le service")
            
            if submitted:
                if not all([titre, categorie, description]):
                    st.error("Veuillez remplir tous les champs obligatoires (*)")
                else:
                    if creer_service(titre, categorie, description, type_service, 
                                    prix, st.session_state.utilisateur['id']):
                        st.success("Service publié avec succès !")
                        st.balloons()
                    else:
                        st.error("Erreur lors de la publication")

# ========== PAGE : TROUVER UN SERVICE  ==========

def page_trouver_service():
    """Page de recherche et consultation des services disponibles."""
    st.title("🔍 Trouver un service")
    
    # Filtres de recherche
    with st.container(border=True):
        st.subheader("Filtres")
        col1, col2 = st.columns(2)
        with col1:
            categorie_filtre = st.selectbox("Catégorie", ["Toutes"] + CATEGORIES)
        with col2:
            type_filtre = st.selectbox("Type", ["Tous"] + TYPES_SERVICE)
    
    st.markdown("---")
    
    services = obtenir_services(categorie_filtre, type_filtre)
    
    if len(services) == 0:
        st.info("Aucun service disponible pour le moment")
        return
    
    st.markdown(f"**{len(services)} service(s) trouvé(s)**")
    
    for _, service in services.iterrows():
        with st.container(border=True):
            # Utilisation d'un expander pour afficher les détails du service
            with st.expander(f"📌 {service['titre']} - {service['categorie']}"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Type :** {service['type_service']}")
                    if service['prix'] > 0:
                        st.markdown(f"**Prix :** {service['prix']} €")
                    st.markdown(f"**Description :**")
                    st.write(service['description'])
                    st.markdown(f"**Proposé par :** {service['prenom']} {service['nom']}")
                    st.caption(f"Publié le {service['date_creation'][:10]}")
                
                with col2:
                    # Affichage du formulaire de demande si l'utilisateur est connecté et n'est pas l'auteur
                    if st.session_state.get('utilisateur'):
                        if st.session_state.utilisateur['id'] != service['utilisateur_id']:
                            st.markdown("**Contact**")
                            st.write(f"📧 {service['email']}")
                            if service['telephone']:
                                st.write(f"📞 {service['telephone']}")
                            
                            # Formulaire pour envoyer une demande de contact/réservation
                            with st.form(f"demande_{service['id']}"):
                                date_souhaitee = st.date_input("Date souhaitée")
                                message = st.text_area("Message", height=100)
                                
                                if st.form_submit_button("Envoyer une demande"):
                                    creer_demande(service['id'], st.session_state.utilisateur['id'],
                                                str(date_souhaitee), message)
                                    st.success("Demande envoyée !")
                    else:
                        st.info("Connectez-vous pour contacter le voisin")
        st.markdown("---") # Séparation visuelle entre les containers

# ========== PAGE : MON COMPTE  ==========

def page_mon_compte():
    """Page de gestion du compte utilisateur (services, demandes, profil)."""
    st.title("👤 Mon Compte")
    
    if not st.session_state.get('utilisateur'):
        st.warning("Vous devez être connecté")
        return
    
    user = st.session_state.utilisateur

    st.markdown(f"<h3 style='color: #0020CA;'>Bienvenue {user['prenom']} {user['nom']}</h3>", unsafe_allow_html=True)
    
    # Utilisation de 4 onglets pour afficher (Mes services", "Demandes reçues", "Demandes envoyées", "Mes informations")
    tab1, tab2, tab3, tab4 = st.tabs(["Mes services", "Demandes reçues", "Demandes envoyées", "Mes informations"])
    
    with tab1: # Gestion des services proposés
        st.subheader("Services que je propose")
        mes_services = obtenir_mes_services(user['id'])
        
        if len(mes_services) == 0:
            st.info("Vous n'avez pas encore proposé de service")
        else:
            for _, service in mes_services.iterrows():
                
                with st.container(border=True):
                    col_title, col_toggle = st.columns([4, 1])
                    is_dispo = service['disponible'] == 1
                    
                    with col_toggle:
                        # Case à cocher pour activer ou désactiver la disponibilité du service
                        if st.checkbox("Disponible", value=is_dispo, key=f"dispo_{service['id']}", help="Active ou désactive votre annonce"):
                            if not is_dispo:
                                if mettre_a_jour_disponibilite_service(service['id'], 1):
                                    st.success("Service réactivé!")
                                    st.rerun()
                        else:
                            if is_dispo:
                                if mettre_a_jour_disponibilite_service(service['id'], 0):
                                    st.warning("Service désactivé!")
                                    st.rerun()

                    with col_title:
                        st.markdown(f"**{service['titre']} - {'✅ Actif' if is_dispo else '❌ Inactif'}**")

                    with st.expander("Détails"):
                        st.write(f"**Catégorie :** {service['categorie']}")
                        st.write(f"**Type :** {service['type_service']}")
                        if service['prix'] > 0:
                            st.write(f"**Prix :** {service['prix']} €")
                    st.write(f"**Description :** {service['description']}")
                    st.caption(f"Créé le {service['date_creation'][:10]}")
    
                st.markdown("---") # Séparation

    with tab2: # Gestion des demandes reçues
        st.subheader("Demandes reçues pour mes services")
        demandes = obtenir_demandes_recues(user['id'])
        
        if len(demandes) == 0:
            st.info("Aucune demande reçue")
        else:
            for _, demande in demandes.iterrows():
                with st.container(border=True):
                    # Affichage des informations du demandeur
                    with st.expander(f"Demande pour '{demande['titre']}' - {demande['date_demande'][:10]}"):
                        st.write(f"**Demandeur :** {demande['prenom']} {demande['nom']}")
                        st.write(f"**Email :** {demande['email']}")
                        st.write(f"**Téléphone :** {demande['telephone']}")
                        st.write(f"**Date souhaitée :** {demande['date_souhaitee']}")
                        st.write(f"**Message :**")
                        st.info(demande['message'])
                        
                        statut_affiche = demande['statut'].replace('_', ' ').capitalize()
                        
                        if demande['statut'] == 'acceptee':
                            st.success(f"**Statut :** {statut_affiche}")
                        elif demande['statut'] == 'refusee':
                            st.error(f"**Statut :** {statut_affiche}")
                        else:
                            st.warning(f"**Statut :** {statut_affiche}")
                        
                        # Boutons d'action uniquement si en_attente
                        if demande['statut'] == 'en_attente':
                            col_accept, col_reject, _ = st.columns([1, 1, 3])
                            with col_accept:
                                if st.button("Accepter", key=f"accept_{demande['id']}", type="primary"):
                                    if mettre_a_jour_statut_demande(demande['id'], 'acceptee'):
                                        st.success("Demande acceptée ! Rafraîchissement...")
                                        st.rerun()
                            with col_reject:
                                if st.button("Refuser", key=f"reject_{demande['id']}", type="secondary"):
                                    if mettre_a_jour_statut_demande(demande['id'], 'refusee'):
                                        st.warning("Demande refusée. Rafraîchissement...")
                                        st.rerun()
                st.markdown("---") # Séparation

    with tab3: # Gestion des demandes envoyées par l'utilisateur
        st.subheader("Mes demandes de service envoyées")
        mes_demandes_envoyees = obtenir_mes_demandes_initiees(user['id'])

        if len(mes_demandes_envoyees) == 0:
            st.info("Vous n'avez envoyé aucune demande de service pour le moment.")
        else:
            for _, demande in mes_demandes_envoyees.iterrows():
                with st.container(border=True):
                    statut = demande['statut']
                    statut_affiche = statut.replace('_', ' ').capitalize()
                    
                    with st.expander(f"Demande pour '{demande['titre']}' - Statut: {statut_affiche}"):
                        st.write(f"**Proposé par :** {demande['prenom']} {demande['nom']}")
                        st.write(f"**Email du Proposeur :** {demande['email']}")
                        if demande['telephone']:
                            st.write(f"**Téléphone du Proposeur :** {demande['telephone']}")
                        
                        # Affichage du statut avec couleur
                        if statut == 'acceptee':
                            st.success(f"✅ **Statut :** {statut_affiche} - Vous pouvez contacter le voisin.")
                        elif statut == 'refusee':
                            st.error(f"❌ **Statut :** {statut_affiche}.")
                        else:
                            st.warning(f"⏳ **Statut :** {statut_affiche} - En attente de réponse.")
                st.markdown("---") # Séparation

    
    with tab4: # Modification du profil
        st.subheader("Mes informations")
        
        with st.container(border=True):
            with st.form("formulaire_modification_profil"):
                # L'email est affiché comme non modifiable
                st.write(f"**Email :** {user['email']} (Non modifiable ici)")
                
                # Champs pré-remplis pour la modification
                nouveau_nom = st.text_input("Nom", value=user['nom'])
                nouveau_prenom = st.text_input("Prénom", value=user['prenom'])
                nouveau_telephone = st.text_input("Téléphone", value=user.get('telephone', ''))
                nouvelle_adresse = st.text_area("Adresse", value=user.get('adresse', ''))
                
                submitted = st.form_submit_button("Sauvegarder les modifications")
                
                if submitted:
                    success, message = mettre_a_jour_utilisateur(
                        user['id'], nouveau_nom, nouveau_prenom, user['email'], nouvelle_adresse, nouveau_telephone
                    )
                    if success:
                        # Mise à jour de l'état de session après succès
                        st.session_state.utilisateur.update({
                            'nom': nouveau_nom, 
                            'prenom': nouveau_prenom, 
                            'adresse': nouvelle_adresse, 
                            'telephone': nouveau_telephone
                        })
                        st.success(message)
                    else:
                        st.error(message)

# ==================== FONCTION PRINCIPALE  ====================

def main():
    #Fonction principale de l'application - Gère l'initialisation et la navigation.
    
    init_database()
    
    # Initialisation des variables d'état de session si elles n'existent pas
    if 'utilisateur' not in st.session_state:
        st.session_state.utilisateur = None
    if 'page_navigation' not in st.session_state:
        st.session_state.page_navigation = "Accueil"
    
    # Définition des options de menu en fonction de l'état de connexion
    menu_options = (["Accueil", "Proposer un service", "Trouver un service", "Mon compte"] 
                    if st.session_state.utilisateur 
                    else ["Accueil", "S'inscrire", "Se connecter", "Trouver un service"])
    
    # Création des colonnes pour la barre de navigation
    col_title, *nav_cols, col_logout = st.columns([2] + [1]*len(menu_options) + [1])
    
    with col_title:
        st.markdown("#### 🏘️ Voisins Solidaires")
    
    # Création des boutons de navigation
    for i, option in enumerate(menu_options):
        with nav_cols[i]:
            if st.button(option, key=f"nav_{option}", use_container_width=True, 
                        type="primary" if option == st.session_state.page_navigation else "secondary"):
                st.session_state.page_navigation = option
                st.rerun()
    
    # Bouton de déconnexion
    with col_logout:
        if st.session_state.utilisateur:
            if st.button("🚪 Déconnexion", key="nav_logout", use_container_width=True):
                st.session_state.utilisateur = None
                st.session_state.page_navigation = "Accueil"
                st.rerun()
    
    st.markdown("---")
    
    # Affichage du statut de connexion
    if st.session_state.utilisateur:
        st.caption(f"✅ Connecté : {st.session_state.utilisateur['prenom']} {st.session_state.utilisateur['nom']}")
    
    # La liste des pages sous forme de dictionnaire
    pages = {
        "Accueil": page_accueil,
        "S'inscrire": page_inscription,
        "Se connecter": page_connexion,
        "Proposer un service": page_proposer_service,
        "Trouver un service": page_trouver_service,
        "Mon compte": page_mon_compte,
        "Mot de passe oublié": page_mot_de_passe_oublie 
    }
    
    # Affichage de la page sélectionnée
    if st.session_state.page_navigation in pages:
        pages[st.session_state.page_navigation]()
    else:
         pages["Accueil"]() # Page par défaut

if __name__ == "__main__":
    main()