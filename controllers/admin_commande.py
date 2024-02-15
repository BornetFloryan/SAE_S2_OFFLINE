#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_commande = Blueprint('admin_commande', __name__,
                        template_folder='templates')

@admin_commande.route('/admin')
@admin_commande.route('/admin/commande/index')
def admin_index():
    return render_template('admin/layout_admin.html')


@admin_commande.route('/admin/commande/show', methods=['get','post'])
def admin_commande_show():
    mycursor = get_db().cursor()
    admin_id = session['id_user']
    sql = '''   
    SELECT id_commande,
    etat_id,
    login,
    date_achat,
    SUM(quantite) as nbr_articles,
    ROUND(SUM(vetement.prix_vetement * quantite), 2) as prix_total,
    etat.libelle
    FROM commande 
    JOIN utilisateur ON commande.utilisateur_id = utilisateur.id_utilisateur
    JOIN etat ON commande.etat_id = etat.id_etat
    JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
    JOIN vetement ON ligne_commande.vetement_id = vetement.id_vetement
    GROUP BY id_commande, etat_id, login, date_achat, etat.libelle
    ORDER BY etat_id, date_achat DESC
    '''
    mycursor.execute(sql)
    commandes= mycursor.fetchall()


    id_commande = request.args.get('id_commande', None)
    print(id_commande)
    if id_commande != None:
        sql = '''
        SELECT id_commande,
        nom_vetement as nom,
        SUM(quantite) as quantite,
        prix_vetement as prix,
        ROUND(SUM(prix_vetement * quantite), 2) as prix_ligne
        FROM commande
        JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
        JOIN vetement ON ligne_commande.vetement_id = vetement.id_vetement
        WHERE id_commande = %s
        GROUP BY id_commande, quantite, prix_vetement, nom_vetement
        '''
        mycursor.execute(sql, id_commande)
        articles_commande = mycursor.fetchall()
        commande_adresses = None
    else:
        articles_commande = None
        commande_adresses = None
    return render_template('admin/commandes/show.html'
                           , commandes=commandes
                           , articles_commande=articles_commande
                           , commande_adresses=commande_adresses
                           )


@admin_commande.route('/admin/commande/valider', methods=['get','post'])
def admin_commande_valider():
    mycursor = get_db().cursor()
    commande_id = request.form.get('id_commande', None)
    if commande_id != None:
        print(commande_id)
        sql = ''' UPDATE commande SET etat_id = 2 WHERE id_commande = %s'''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')
