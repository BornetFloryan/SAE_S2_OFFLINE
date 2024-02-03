#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g
from datetime import datetime
from connexion_db import get_db

client_commande = Blueprint('client_commande', __name__,
                        template_folder='templates')


# validation de la commande : partie 2 -- vue pour choisir les adresses (livraision et facturation)
@client_commande.route('/client/commande/valide', methods=['POST'])
def client_commande_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = ''' SELECT vetement_id,
    nom_vetement as nom,
     ligne_panier.quantite as quantite,
     vetement.prix_vetement as prix,
     SUM(ligne_panier.quantite * vetement.prix_vetement) as prix_total
     FROM ligne_panier 
     JOIN vetement ON ligne_panier.vetement_id = vetement.id_vetement
     WHERE utilisateur_id = %s
     GROUP BY vetement_id, quantite, prix_vetement, nom_vetement
     '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()
    print(articles_panier)

    if len(articles_panier) >= 1:
        sql = ''' SELECT prix_vetement as prix,
        quantite
        FROM ligne_panier 
        JOIN vetement ON ligne_panier.vetement_id = vetement.id_vetement
        WHERE utilisateur_id = %s '''
        mycursor.execute(sql, (id_client,))
        prix_total = mycursor.fetchone()
    else:
        prix_total = None
    # etape 2 : selection des adresses
    return render_template('client/boutique/panier_validation_adresses.html'
                           #, adresses=adresses
                           , articles_panier=articles_panier
                           , prix_total= prix_total
                           , validation=1
                           #, id_adresse_fav=id_adresse_fav
                           )


@client_commande.route('/client/commande/add', methods=['POST'])
def client_commande_add():
    mycursor = get_db().cursor()

    # choix de(s) (l')adresse(s)

    id_client = session['id_user']
    sql = ''' SELECT * FROM ligne_panier WHERE utilisateur_id = %s '''
    mycursor.execute(sql, (id_client,))
    items_ligne_panier = mycursor.fetchall()
    if items_ligne_panier is None or len(items_ligne_panier) < 1:
        flash(u'Pas d\'articles dans le ligne_panier', 'alert-warning')
        return redirect('/client/article/show')
                                           # https://pynative.com/python-mysql-transaction-management-using-commit-rollback/
    #a = datetime.strptime('my date', "%b %d %Y %H:%M")

    sql = ''' INSERT INTO commande (date_achat, utilisateur_id, etat_id) VALUES (current_timestamp, %s, 1) '''
    mycursor.execute(sql, (id_client,))
    sql = '''SELECT last_insert_id() as last_insert_id'''
    mycursor.execute(sql)
    commande_id = mycursor.fetchone()

    for item in items_ligne_panier:
        sql = ''' DELETE FROM ligne_panier WHERE utilisateur_id = %s AND vetement_id = %s '''
        mycursor.execute(sql, (id_client, item['vetement_id']))
        sql = ''' SELECT prix_vetement AS prix FROM vetement WHERE id_vetement = %s '''
        mycursor.execute(sql, (item['vetement_id'],))
        prix_vetement = mycursor.fetchone()
        sql = "  INSERT INTO ligne_commande (commande_id, vetement_id, quantite, prix) VALUES (%s, %s, %s, %s) "
        mycursor.execute(sql, (commande_id['last_insert_id'], item['vetement_id'], item['quantite'], prix_vetement['prix']))
    get_db().commit()
    flash(u'Commande ajoutée','alert-success')
    return redirect('/client/article/show')




@client_commande.route('/client/commande/show', methods=['get','post'])
def client_commande_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''  SELECT id_commande,
                        date_achat,
                        utilisateur_id,
                        etat_id,
                        SUM(quantite) as nbr_articles,
                        SUM(prix * quantite) as prix_total,
                        libelle
                FROM commande
                JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
                JOIN etat ON commande.etat_id = etat.id_etat
                WHERE utilisateur_id = %s
                GROUP BY id_commande, date_achat, utilisateur_id, etat_id, libelle
                ORDER BY etat_id, date_achat DESC
                '''
    mycursor.execute(sql, (id_client,))
    commandes = mycursor.fetchall()

    articles_commande = None
    commande_adresses = None
    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        print(id_commande)
        sql = ''' selection du détails d'une commande '''

        # partie 2 : selection de l'adresse de livraison et de facturation de la commande selectionnée
        sql = ''' SELECT * FROM adresse WHERE id_utilisateur = %s '''

    return render_template('client/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )

