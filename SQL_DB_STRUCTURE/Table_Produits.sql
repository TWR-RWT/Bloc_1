CREATE TABLE produit (
    id_produit SERIAL PRIMARY KEY,
    nom_produit VARCHAR(255) NOT NULL,
    description TEXT,
    prix_unitaire NUMERIC(10, 2) NOT NULL
);