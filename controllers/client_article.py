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
                stock_vetement.stock as stock
                FROM vetement 
                LEFT JOIN stock_vetement on vetement.id_vetement = stock_vetement.id_vetement
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

    sql = '''SELECT vetement_id as id_article,
            nom_vetement as nom,
            quantite,
           ROUND(prix_vetement, 2) as prix,
           stock
           FROM ligne_panier
           LEFT JOIN vetement on vetement.id_vetement = ligne_panier.vetement_id
              LEFT JOIN stock_vetement on vetement.id_vetement = stock_vetement.id_vetement
           WHERE utilisateur_id = %s
           GROUP BY nom_vetement, quantite, prix_vetement, vetement_id, stock
                      '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()

    if len(articles_panier) >= 1:
        sql = ''' calcul du prix total du panier '''
        prix_total = None
    else:
        prix_total = None
    return render_template('client/boutique/panier_article.html'
                           , articles=articles
                           , articles_panier=articles_panier
                           #, prix_total=prix_total
                           , items_filtre=types_article
                           )
