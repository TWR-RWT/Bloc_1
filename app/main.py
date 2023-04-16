#! C:\Users\tgp\AppData\Local\Programs\Python\Python310\python.exe
from app import app, request, render_template, flash, redirect, url_for, get_db, token_required_auth
from flask import render_template, request, redirect, url_for, flash, abort


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

@app.route('/modifier_client/<int:id>', methods=['POST'])
@token_required_auth
def modifier_client(id):
    nom = request.form['nom_client']
    prenom = request.form['prenom_client']
    email = request.form['email_client']
    siret = request.form['siret']
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('UPDATE rubansoft.client SET nom=%s, prenom=%s, email=%s, siret=%s WHERE id_client=%s',
                        (nom, prenom, email, siret, id))
            conn.commit()
    flash('Le client a été modifié avec succès')
    return redirect(url_for('clients'))

@app.route('/supprimer_client/<int:id>', methods=['POST'])
@token_required_auth
def supprimer_client(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM rubansoft.client WHERE id_client=%s', (id,))
            conn.commit()
    flash('Le client a été supprimé avec succès')
    return redirect(url_for('clients'))

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

@app.route('/modifier_produit/<int:id>', methods=['POST'])
def modifier_produit(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM rubansoft.produit WHERE id_produit = %s', (id,))
            produit = cur.fetchone()
            if not produit:
                abort(404)
            else:
                nom_produit = request.form['nom_produit']
                prix_unitaire = request.form['prix_unitaire']
                cur.execute('UPDATE rubansoft.produit SET nom_produit = %s, prix_unitaire = %s WHERE id_produit = %s',
                            (nom_produit, prix_unitaire, id))
                conn.commit()
    return redirect(url_for('get_products'))


@app.route('/supprimer_produit/<int:produit_id>', methods=['POST'])
@token_required_auth
def supprimer_produit(produit_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM rubansoft.produit WHERE id_produit=%s', (produit_id,))
            conn.commit()
    flash('Le produit a été supprimé avec succès')
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

@app.route('/machines/supprimer/<int:machine_id>', methods=['POST'])
@token_required_auth
def supprimer_machine(machine_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM rubansoft.machine WHERE id_machine = %s', (machine_id,))
            conn.commit()
    flash("Machine supprimée avec succès", "success")
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
                date_livraison_reelle,
                ligne_de_commande.id_produit
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

@app.route('/supprimer_ligne_de_commande/<int:commande_id>/<int:produit_id>', methods=['POST', 'GET'])
@token_required_auth
def supprimer_ligne_de_commande(commande_id, produit_id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute('DELETE FROM rubansoft.ligne_de_commande WHERE id_commande=%s AND id_produit=%s',
                        (commande_id, produit_id))
            conn.commit()
            
            # Vérifier si la commande a d'autres lignes de commandes
            cur.execute('SELECT COUNT(*) FROM rubansoft.ligne_de_commande WHERE id_commande=%s', (commande_id,))
            ligne_commandes_count = cur.fetchone()[0]
            
            # Si la commande n'a plus de lignes de commandes, supprimer la commande aussi
            if ligne_commandes_count == 0:
                cur.execute('DELETE FROM rubansoft.commande WHERE id_commande=%s', (commande_id,))
                conn.commit()
            
            flash('Ligne de commande supprimée avec succès.', 'success')
            return redirect(url_for('get_orders'))


# Route pour modifier la quantité d'une ligne de commande
@app.route('/modifier_quantite_ligne_de_commande/<int:commande_id>/<int:produit_id>', methods=['POST'])
@token_required_auth
def modifier_quantite_ligne_de_commande(commande_id, produit_id):
    if request.method == 'POST':
        nouvelle_quantite = int(request.form['quantite'])  # Obtenir la nouvelle quantité à partir du formulaire

        if nouvelle_quantite <= 0:
            # Si la nouvelle quantité est égale à 0 ou moins, utiliser la route pour supprimer la ligne de commande
            return redirect(url_for('supprimer_ligne_de_commande', commande_id=commande_id, produit_id=produit_id))
        else:
            # Mettre à jour la quantité dans la base de données
            with get_db() as conn:
                with conn.cursor() as cur:
                    # Exécuter la requête de mise à jour de la quantité
                    cur.execute('UPDATE rubansoft.ligne_de_commande SET quantite = %s WHERE id_commande = %s AND id_produit = %s',
                                (nouvelle_quantite, commande_id, produit_id))
                    conn.commit()  # Valider la transaction
                    flash('Quantité modifiée avec succès.', 'success')

            return redirect(url_for('get_orders'))  # Rediriger vers la page d'affichage des commandes

    # Retourner une erreur si la méthode HTTP n'est pas POST
    return 'Erreur: Cette route accepte uniquement les requêtes POST.'


@app.route('/changer_statut_commande/<int:commande_id>', methods=['POST'])
@token_required_auth
def changer_statut_commande(commande_id):
    if request.method == 'POST':
        statut = request.form['statut']  # Récupérer le statut du formulaire
        with get_db() as conn:
            with conn.cursor() as cur:
                # Mettre à jour le statut de la commande dans la base de données
                cur.execute("UPDATE rubansoft.commande SET statut = %s WHERE id_commande = %s", (statut, commande_id))
                conn.commit()
                flash('Statut de la commande mis à jour avec succès', 'success')
        return redirect(url_for('get_orders'))

@app.route('/modifier_dates_livraison_commande/<int:commande_id>', methods=['POST'])
@token_required_auth
def modifier_dates_livraison_commande(commande_id):
    if request.method == 'POST':
        date_livraison_souhaitee = request.form['date_livraison_souhaitee']  # Récupérer la date de livraison souhaitée du formulaire
        date_livraison_reelle = request.form['date_livraison_reelle']  # Récupérer la date de livraison réelle du formulaire
        with get_db() as conn:
            with conn.cursor() as cur:
                # Mettre à jour les dates de livraison de la commande dans la base de données
                cur.execute("UPDATE rubansoft.commande SET date_livraison_souhaitee = %s, date_livraison_reelle = %s WHERE id_commande = %s", (date_livraison_souhaitee or None, date_livraison_reelle or None, commande_id))
                conn.commit()
                flash('Dates de livraison de la commande mises à jour avec succès', 'success')
        return redirect(url_for('get_orders'))

########## stocks ##########
@app.route('/stocks')
@token_required_auth
def get_stocks():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT stock.id_stock, stock.id_produit, produit.nom_produit, stock.quantite
                FROM rubansoft.stock
                INNER JOIN rubansoft.produit ON stock.id_produit = produit.id_produit
                ORDER BY produit.nom_produit
            """)
            stocks = cur.fetchall()
            #print(f"stocks: {stocks}")
            cur.close()
    
    # Récupérer la liste des produits
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rubansoft.machine ORDER BY nom")
            machines = cur.fetchall()

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id_produit, nom_produit FROM rubansoft.produit ORDER BY nom_produit")
            produits = cur.fetchall()

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT production.id_production, machine.nom, produit.nom_produit, production.Date_debut_production, production.Date_fin_production
                FROM rubansoft.production
                INNER JOIN rubansoft.machine ON production.id_machine = machine.id_machine
                INNER JOIN rubansoft.produit ON production.id_produit = produit.id_produit
                ORDER BY production.Date_debut_production DESC
            """)
            productions = cur.fetchall()
            print(f"productions: {productions}")
            cur.close()

    return render_template('/main/stocks_production.html', stocks=stocks, produits=produits, productions=productions, machines=machines)

@app.route('/stocks/nouveau', methods=['GET', 'POST'])
@token_required_auth
def ajouter_stock():
    if request.method == 'POST':
        produit_id = request.form['produit_id']
        quantite = request.form['quantite']
        # Insérer les données du nouveau stock dans la base de données
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO rubansoft.stock (id_produit, quantite)
                    VALUES (%s, %s)
                """, (produit_id, quantite))
                conn.commit()
        flash('Le stock a été créé avec succès', 'success')
        return redirect(url_for('get_stocks'))

    # Afficher le formulaire de création de stock
    return redirect(url_for('get_stocks'))

@app.route('/stocks/<int:id_stock>/supprimer', methods=['POST'])
@token_required_auth
def supprimer_stock(id_stock):
    # Supprimer le stock correspondant de la base de données
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                DELETE FROM rubansoft.stock WHERE id_stock=%s
            """, (id_stock,))
            conn.commit()
    flash('Le stock a été supprimé avec succès', 'success')
    return redirect(url_for('get_stocks'))

@app.route('/stocks/<int:id_stock>/modifier', methods=['POST'])
@token_required_auth
def update_stock(id_stock):
    quantite = request.form['quantite']
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE rubansoft.stock SET quantite=%s WHERE id_stock=%s", (quantite, id_stock))
            conn.commit()
    flash('Le stock a été modifié avec succès', 'success')
    return redirect(url_for('get_stocks'))

########## productions ##########
@app.route('/productions/nouveau', methods=['GET', 'POST'])
@token_required_auth
def ajouter_production():
    if request.method == 'POST':
        date_debut_production = request.form['date_debut_production']
        date_fin_production = request.form['date_fin_production']
        produit_id = request.form['produit_id']
        machine_id = request.form['machine_id']
        # Insérer les données de la nouvelle production dans la base de données
        with get_db() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO rubansoft.production (date_debut_production, date_fin_production, id_produit, id_machine)
                    VALUES (%s, %s, %s, %s)
                """, (date_debut_production, date_fin_production or None, produit_id, machine_id))
                conn.commit()
        flash('La production a été créée avec succès', 'success')
        return redirect(url_for('get_stocks'))
    
    flash('Une erreur est survenue lors de la création de la production', 'danger')
    return redirect(url_for('get_stocks'))

@app.route('/productions/supprimer/<int:id>', methods=['POST', 'DELETE'])
def supprimer_production(id):
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM rubansoft.production WHERE id_production=%s", (id,))
            conn.commit()
    flash("La production a été supprimée avec succès.")
    return redirect(url_for('get_stocks'))

@app.route('/modifier_production/<int:id_production>', methods=['GET', 'POST'])
def modifier_production(id_production):
    with get_db() as conn:
        with conn.cursor() as cur:
            # Récupérer la production à modifier
            cur.execute("SELECT * FROM rubansoft.production WHERE id_production = %s", (id_production,))
            production = cur.fetchone()
            if not production:
                flash(f"La production avec l'identifiant {id_production} n'existe pas", "danger")
                return redirect(url_for('get_stocks'))

            if request.method == 'POST':
                # Récupérer la nouvelle date_fin_production depuis le formulaire
                nouvelle_date_fin = request.form.get('date_fin_production')

                # Mettre à jour la date_fin_production dans la base de données
                cur.execute("UPDATE rubansoft.production SET date_fin_production = %s WHERE id_production = %s", (nouvelle_date_fin or None, id_production))
                conn.commit()
                flash("La production a été modifiée avec succès", "success")
                return redirect(url_for('get_stocks'))

    return redirect(url_for('get_stocks'))
