DROP TABLE IF EXISTS vetement, utilisateur, taille, type_vetement;

CREATE TABLE IF NOT EXISTS taille(
    id_taille INT NOT NULL AUTO_INCREMENT,
    libelle_taille VARCHAR(255),
    PRIMARY KEY(id_taille)
);

CREATE TABLE IF NOT EXISTS type_vetement(
    id_type_vetement INT NOT NULL AUTO_INCREMENT,
    libelle_type_vetement VARCHAR(255),
    PRIMARY KEY(id_type_vetement)
);

CREATE TABLE IF NOT EXISTS utilisateur (
    id_utilisateur INT NOT NULL AUTO_INCREMENT,
    login VARCHAR(255),
    email VARCHAR(255),
    password VARCHAR(255),
    role VARCHAR(255),
    nom VARCHAR(255),
    est_actif TINYINT(1),
    PRIMARY KEY(id_utilisateur)
);

CREATE TABLE IF NOT EXISTS vetement(
    id_vetement INT NOT NULL AUTO_INCREMENT,
    nom_vetement VARCHAR(255),
    prix_vetement FLOAT,
    matiere VARCHAR(255),
    description VARCHAR(255),
    fournisseur VARCHAR(255),
    marque VARCHAR(255),
    id_taille INT,
    id_type_vetement INT,
    PRIMARY KEY(id_vetement),
    FOREIGN KEY (id_taille) REFERENCES taille(id_taille),
    FOREIGN KEY (id_type_vetement) REFERENCES type_vetement(id_type_vetement)
);


INSERT INTO taille(id_taille, libelle_taille) VALUES
(1, 'S'),
(2, 'M'),
(3, 'L'),
(4, 'XL');

INSERT INTO type_vetement(id_type_vetement, libelle_type_vetement) VALUES
(1, 'T-shirt'),
(2, 'Pantalon'),
(3, 'Chaussures');

INSERT INTO utilisateur(id_utilisateur,login,email,password,role,nom,est_actif) VALUES
(1,'admin','admin@admin.fr',
    'pbkdf2:sha256:600000$828ij7RCZN24IWfq$3dbd14ea15999e9f5e340fe88278a45c1f41901ee6b2f56f320bf1fa6adb933d',
    'ROLE_admin','admin','1'),
(2,'client','client@client.fr',
    'pbkdf2:sha256:600000$ik00jnCw52CsLSlr$9ac8f694a800bca6ee25de2ea2db9e5e0dac3f8b25b47336e8f4ef9b3de189f4',
    'ROLE_client','client','1'),
(3,'client2','client2@client2.fr',
    'pbkdf2:sha256:600000$3YgdGN0QUT1jjZVN$baa9787abd4decedc328ed56d86939ce816c756ff6d94f4e4191ffc9bf357348',
    'ROLE_client','client2','1');

INSERT INTO vetement(id_vetement, nom_vetement, prix_vetement, matiere, description, fournisseur, marque, id_taille, id_type_vetement) VALUES
(1, 'T-shirt Nike', 29.99, 'Coton', 'T-shirt confortable et stylé', 'Nike', 'Nike', 1, 1),
(2, 'Pantalon Levis', 59.99, 'Denim', 'Pantalon en denim de haute qualité', 'Levis', 'Levis', 2, 2),
(3, 'Chaussures Adidas', 79.99, 'Cuir', 'Chaussures de sport durables', 'Adidas', 'Adidas', 3, 3);
