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