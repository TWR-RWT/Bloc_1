CREATE TABLE ligne_de_commande (
    id_commande INTEGER NOT NULL,
    id_produit INTEGER NOT NULL,
    quantite INTEGER NOT NULL,
    PRIMARY KEY (id_commande, id_produit),
    FOREIGN KEY (id_commande) REFERENCES commande (id_commande),
    FOREIGN KEY (id_produit) REFERENCES produit (id_produit)
);
