CREATE TABLE production (
    id_production SERIAL PRIMARY KEY,
    id_produit INTEGER NOT NULL,
    id_machine INTEGER NOT NULL,
    date_debut_production TIMESTAMP NOT NULL,
    date_fin_production TIMESTAMP,
    FOREIGN KEY (id_produit) REFERENCES produit (id_produit),
    FOREIGN KEY (id_machine) REFERENCES machine (id_machine)
);
