CREATE TABLE client (
    id_client SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    prenom VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    telephone VARCHAR(20),
    adresse TEXT NOT NULL,
    siret VARCHAR(14) NOT NULL UNIQUE
);
