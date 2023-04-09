#! C:\Users\tgp\AppData\Local\Programs\Python\Python310\python.exe
from app import app, request, render_template, flash, redirect, url_for, get_db, token_required_auth
from flask import render_template, request, redirect, url_for, flash


###################### Clients ############################
@app.route('/clients/add', methods=['POST'])
@token_required_auth
def add_client():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        adresse = request.form['adresse']
        siret = request.form['siret']
        telephone = request.form['telephone']
        email = request.form['email']
        print(f"nom: {nom}")
        print(f"prenom: {prenom}")
        print(f"adresse: {adresse}")
        print(f"siret: {siret}")
        print(f"telephone: {telephone}")
        print(f"email: {email}")
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO rubansoft.client (nom, prenom, adresse, siret, telephone, email)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id_client
                """, (nom, prenom, adresse, siret, telephone, email))
                client_id = cur.fetchone()[0]
                print(f"client_id: {client_id}")
                conn.commit()
                cur.close()#
                #conn.close()#
        flash('Client ajouté avec succès')
        return redirect(url_for('index'))
        #return redirect(url_for('show_client', client_id=client_id))
    return redirect(url_for('clients'))

@app.route('/clients')
@token_required_auth
def clients():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rubansoft.client")
            clients = cur.fetchall()
            print(f"clients: {clients}")
            cur.close()
    return render_template('/main/clients.html', clients=clients)

###############
@app.route('/products')
@token_required_auth
def get_products():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rubansoft.produit")
            products = cur.fetchall()
            cur.close()
    return render_template('/main/produits.html', products=products)

@app.route('/products/create', methods=['POST'])
@token_required_auth
def create_product():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        price = request.form['price']
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO rubansoft.produit (nom_produit, description, prix_unitaire) 
                    VALUES (%s, %s, %s)
                """, (name, description, price))
                conn.commit()
                cur.close()#
                flash('Produit créé avec succès')
                return redirect(url_for('index'))
    return redirect(url_for('get_products'))

########## machine ##########
@app.route('/machines')
@token_required_auth
def get_machines():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rubansoft.machine")
            machines = cur.fetchall()
            cur.close()
    return render_template('/main/machines.html', machines=machines)


@app.route('/add_machine', methods=['POST'])
@token_required_auth
def add_machine():
    if request.method == 'POST':
        name = request.form['name']
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO rubansoft.machine (nom) VALUES (%s)", (name,))
                conn.commit()
                cur.close()#
                flash('La machine a été ajoutée avec succès.')
                return redirect(url_for('index'))
    return redirect(url_for('get_machines'))


########## commande ##########
@app.route('/commandes/', methods=['GET'])
def get_orders():
    # Récupérer la liste des clients et des produits
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_client, nom FROM rubansoft.client ORDER BY nom")
            clients = cur.fetchall()
            print(f"clients: {clients}")
            cur.execute("SELECT id_produit, nom_produit FROM rubansoft.produit ORDER BY nom_produit")
            produits = cur.fetchall()
            print(f"produits: {produits}")

            # Récupérer la liste des commandes
            cur.execute("""
                SELECT 
                commande.id_commande, 
                date_commande, 
                statut, 
                nom, 
                produit.nom_produit, 
                ligne_de_commande.quantite, 
                date_livraison_souhaitee, 
                date_livraison_reelle
                FROM rubansoft.commande
                JOIN rubansoft.client ON commande.id_client = client.id_client
                JOIN rubansoft.ligne_de_commande ON commande.id_commande = ligne_de_commande.id_commande
                JOIN rubansoft.produit ON ligne_de_commande.id_produit = produit.id_produit
                ORDER BY date_commande DESC
            """)
            commandes = cur.fetchall()
            conn.commit()
            cur.close()#
            print(f"commandes: {commandes}")

    return render_template('/main/commandes.html', clients=clients, produits=produits, commandes=commandes)


@app.route('/commandes/ajouter', methods=['GET', 'POST'])
def add_order():
    if request.method == 'POST':
        # Récupération des données de la commande depuis le formulaire
        date_commande = request.form['date_commande']
        statut = request.form['statut']
        id_client = request.form['client']
        ref_film = request.form['ref_film']
        date_livraison_souhaitee = request.form['date_livraison_souhaitee']
        date_livraison_reelle = request.form['date_livraison_reelle']

        produits = [(1, '1200 Rouleaux SR528 – avec Logo client'), (2, '1200 Rouleaux SR250 – avec Logo client	'), (3, '1200 Rouleaux DF'), (4, '1200 Rouleaux Mpro')]
        quantites = []
        for produit in produits:
            quantite = request.form.get('quantite_{}'.format(produit[0]))
            if quantite is not None and quantite.isdigit():
                quantites.append((produit[0], int(quantite)))
        #print(f"produits: {produits}")
        #print(f"quantites: {quantites}")

        try:
            # Connexion à la base de données
            with get_db() as conn:
                with conn.cursor() as cur:
                    # Ajout de la commande dans la table "commande"
                    cur.execute("""
                        INSERT INTO rubansoft.commande (date_commande, statut, id_client, ref_film, date_livraison_souhaitee, date_livraison_reelle)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING id_commande
                    """, (date_commande, statut, id_client, ref_film or None, date_livraison_souhaitee or None, date_livraison_reelle or None))
                    id_commande = cur.fetchone()[0]
                    #print(f"id_commande: {id_commande}")

                    # Ajout des lignes de commande dans la table "ligne_de_commande"
                    for quantite in quantites:
                        produit_id = quantite[0]
                        quantite_commandee = quantite[1]
                        if quantite_commandee > 0:
                            cur.execute("""
                                INSERT INTO rubansoft.ligne_de_commande (id_commande, id_produit, quantite)
                                VALUES (%s, %s, %s)
                            """, (id_commande, produit_id, quantite_commandee))

                    # Validation de la transaction
                    conn.commit()
                    cur.close()#
                    flash('Commande créée avec succès')
        except Exception as e:
            print(e)
            flash('Une erreur est survenue lors de la création de la commande')
        

        # Redirection vers la liste des commandes
        return redirect(url_for('get_orders'))

    # Affichage du formulaire pour créer une nouvelle commande
    return redirect(url_for('get_orders'))
