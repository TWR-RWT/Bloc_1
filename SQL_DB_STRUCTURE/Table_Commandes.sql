CREATE TABLE commande (
    id_commande SERIAL PRIMARY KEY,
    date_commande DATE NOT NULL,
    statut VARCHAR(20) NOT NULL,
    id_client INTEGER NOT NULL,
    ref_film VARCHAR(50),
    date_livraison_souhaitee DATE,
    date_livraison_reelle DATE,
    FOREIGN KEY (id_client) REFERENCES client(id_client)
);
