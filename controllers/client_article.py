#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_article = Blueprint('client_article', __name__,
                        template_folder='templates')

@client_article.route('/client/index')
@client_article.route('/client/article/show')              # remplace /client
def client_article_show():                                 # remplace client_index
    mycursor = get_db().cursor()
    id_client = session['id_user']

    sql = '''   SELECT vetement.id_vetement as id_article, 
                nom_vetement as nom, 
                prix_vetement as prix,  
                image as image, 
                id_type_vetement as id_type,
                (SELECT 1 FROM liste_envie WHERE vetement.id_vetement=liste_envie.vetement_id AND utilisateur_id=%s) AS liste_envie,
                stock_vetement.stock as stock
                FROM vetement
                LEFT JOIN stock_vetement on vetement.id_vetement = stock_vetement.id_vetement
                LEFT JOIN liste_envie on vetement.id_vetement = liste_envie.vetement_id
                GROUP BY vetement.id_vetement, nom_vetement, prix_vetement, image, id_type_vetement, stock_vetement.stock
                '''
    list_param = []
    condition_and = ""
    # utilisation du filtre
    sql3=''' prise en compte des commentaires et des notes dans le SQL    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()


    # pour le filtre
    sql = '''SELECT id_type_vetement  AS id_type_article
             ,libelle_type_vetement AS libelle
             FROM type_vetement
             ORDER BY  libelle_type_vetement
                '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    sql = '''SELECT vetement.id_vetement as id_article,
            nom_vetement as nom,
            quantite,
           ROUND(prix_vetement, 2) as prix,
           stock,
           id_stock as id_declinaison_article,
           stock_vetement.id_taille,
           libelle_taille
           FROM ligne_panier
           LEFT JOIN stock_vetement on ligne_panier.stock_id = stock_vetement.id_stock
           LEFT JOIN vetement on vetement.id_vetement = stock_vetement.id_vetement
           JOIN taille on taille.id_taille = stock_vetement.id_taille
           WHERE utilisateur_id = %s
           GROUP BY nom_vetement, quantite, prix_vetement, 
           vetement.id_vetement, stock, id_stock, id_taille, libelle_taille
           ORDER BY quantite DESC'''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        sql = ''' SELECT SUM(v.prix_vetement * lp.quantite) AS prix_total
        FROM ligne_panier lp
        JOIN stock_vetement ON lp.stock_id = stock_vetement.id_stock
        JOIN vetement v ON stock_vetement.id_vetement = v.id_vetement
        WHERE lp.utilisateur_id = %s; '''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()
    else:
        prix_total = None
    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           , prix_total=prix_total
                           , items_filtre=types_article
                           )
