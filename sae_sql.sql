DROP TABLE IF EXISTS ligne_panier, ligne_commande, commande, etat,
    adresse, utilisateur ,stock_vetement, vetement, taille, type_vetement;

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

CREATE TABLE IF NOT EXISTS vetement(
    id_vetement INT NOT NULL AUTO_INCREMENT,
    nom_vetement VARCHAR(255),
    prix_vetement FLOAT,
    matiere VARCHAR(255),
    description VARCHAR(255),
    fournisseur VARCHAR(255),
    marque VARCHAR(255),
    image VARCHAR(255),
    id_taille INT,
    id_type_vetement INT,
    PRIMARY KEY(id_vetement),
    FOREIGN KEY (id_taille) REFERENCES taille(id_taille),
    FOREIGN KEY (id_type_vetement) REFERENCES type_vetement(id_type_vetement)
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

CREATE TABLE IF NOT EXISTS adresse(
    id_adresse INT NOT NULL AUTO_INCREMENT,
    nom_adresse VARCHAR(255),
    rue VARCHAR(255),
    code_postal INT,
    ville VARCHAR(255),
    id_utilisateur INT,
    PRIMARY KEY(id_adresse),
    FOREIGN KEY (id_utilisateur) REFERENCES utilisateur(id_utilisateur)
);

CREATE TABLE IF NOT EXISTS etat(
    id_etat INT NOT NULL AUTO_INCREMENT,
    libelle VARCHAR(255),
    PRIMARY KEY(id_etat)
);

CREATE TABLE IF NOT EXISTS commande(
    id_commande INT NOT NULL AUTO_INCREMENT,
    date_achat DATE,
    utilisateur_id INT,
    etat_id INT,
    PRIMARY KEY(id_commande),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (etat_id) REFERENCES etat(id_etat)
);

CREATE TABLE IF NOT EXISTS ligne_commande(
    commande_id INT,
    vetement_id INT,
    prix FLOAT,
    quantite INT,
    PRIMARY KEY(commande_id, vetement_id),
    FOREIGN KEY (commande_id) REFERENCES commande(id_commande),
    FOREIGN KEY (vetement_id) REFERENCES vetement(id_vetement)
);

CREATE TABLE IF NOT EXISTS ligne_panier(
    utilisateur_id INT,
    vetement_id INT,
    quantite INT,
    date_ajout DATE,
    PRIMARY KEY(utilisateur_id, vetement_id),
    FOREIGN KEY (utilisateur_id) REFERENCES utilisateur(id_utilisateur),
    FOREIGN KEY (vetement_id) REFERENCES vetement(id_vetement)
);

CREATE TABLE IF NOT EXISTS stock_vetement(
    id_stock INT NOT NULL AUTO_INCREMENT,
    id_vetement INT,
    id_taille INT,
    stock INT,
    PRIMARY KEY(id_stock),
    FOREIGN KEY (id_vetement) REFERENCES vetement(id_vetement)
);


INSERT INTO taille(id_taille, libelle_taille) VALUES
(1, 'XS'),
(2, 'S'),
(3, 'M'),
(4, 'L'),
(5, 'XL'),
(6, 'XXL');

INSERT INTO type_vetement(id_type_vetement, libelle_type_vetement) VALUES
(1, 'T-shirt'),
(2, 'Pantalon'),
(3, 'Chaussures'),
(4, 'Pull');

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

INSERT INTO vetement(nom_vetement, prix_vetement, matiere, description, fournisseur, marque,image, id_taille, id_type_vetement) VALUES
('Pull Adidas', 49.99, 'Coton', 'Pull doux et confortable', 'Adidas', 'Adidas', 'pull_coton_adidas.jpg',2, 4),
('Jean Diesel', 89.99, 'Denim', 'Jean slim fit', 'Diesel', 'Diesel', 'jean_denim_diesel.jpg',3, 2),
('Baskets Puma', 69.99, 'Cuir', 'Baskets légères pour le sport', 'Puma','Puma', 'basket_cuir_puma.jpg', 4, 3),
('T-shirt Gucci', 149.99, 'Coton', 'T-shirt de luxe', 'Gucci', 'Gucci', 't-shirt_coton_gucci.jpg',1, 1),
('Pantalon Prada', 199.99, 'Denim', 'Pantalon de haute qualité', 'Prada', 'Prada', 'pantalon_denim_prada.jpg',2, 2),
('Chaussures Louis Vuitton', 299.99, 'Cuir', 'Chaussures élégantes', 'Louis Vuitton','Louis Vuitton', 'chaussure_cuir_louis-vuitton.jpg', 3, 3),
('Pull Versace', 129.99, 'Coton', 'Pull à la mode', 'Versace', 'Versace', 'pull_coton_versace.jpg',4, 4),
('Jean Armani', 139.99, 'Denim', 'Jean confortable', 'Armani', 'Armani', 'jean_denim_armani.jpg',1, 2),
('Baskets Balenciaga', 399.99, 'Toile', 'Baskets de designer', 'Balenciaga', 'Balenciaga', 'basket_toile_balenciaga.jpg',2, 3),
('T-shirt Supreme', 99.99, 'Coton', 'T-shirt streetwear', 'Supreme', 'Supreme', 't-shirt_coton_supreme.jpg',3, 1),
('Pantalon Off-White', 159.99, 'Denim', 'Pantalon tendance', 'Off-White', 'Off-White', 'jean_denim_off-white.jpg',4, 2),
('Chaussures Yeezy', 249.99, 'Toile', 'Chaussures de sport à la mode', 'Yeezy', 'Yeezy', 'chaussure_toile_yeezy_.jpg',1, 3),
('Pull Stone Island', 119.99, 'Coton', 'Pull casual', 'Stone Island', 'Stone Island', 'pull_coton_stone-island.jpg',2, 4),
('Jean Tommy Hilfiger', 79.99, 'Denim', 'Jean classique', 'Tommy Hilfiger', 'Tommy Hilfiger', 'jean_denim_tommy.jpg',3, 2),
('Baskets Converse', 59.99, 'Toile', 'Baskets vintage', 'Converse', 'Converse', 'chaussure_toile_converse.jpg',4, 3);

INSERT INTO etat(id_etat, libelle) VALUES
(1, 'En attente'),
(2, 'Expédié'),
(3, 'Validé'),
(4, 'Confirmé');

INSERT INTO stock_vetement(id_vetement, id_taille, stock) VALUES
(1, 1, 10),
(1, 2, 7),
(2, 1, 5),
(3, 1, 8),
(4, 1, 7),
(5, 1, 14),
(6, 1, 6),
(7, 1, 7),
(8, 1, 8),
(9, 1, 4),
(10, 1, 3),
(11, 1, 1),
(12, 1, 0),
(13, 1, 2),
(14, 1, 7),
(15, 1, 16);