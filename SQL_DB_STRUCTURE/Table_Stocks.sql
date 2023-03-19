CREATE TABLE stock (
    id_stock SERIAL PRIMARY KEY,
    id_produit INTEGER NOT NULL,
    quantite INTEGER NOT NULL,
    FOREIGN KEY (id_produit) REFERENCES produit (id_produit)
);
