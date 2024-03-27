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
    date_achat,
    utilisateur_id,
    etat_id,
    SUM(quantite) as nbr_articles,
    ROUND(SUM(prix * quantite), 2) as prix_total,
    libelle
    FROM commande
    JOIN ligne_commande ON commande.id_commande = ligne_commande.commande_id
    JOIN etat ON commande.etat_id = etat.id_etat
    GROUP BY id_commande, date_achat, utilisateur_id, etat_id, libelle
    ORDER BY etat_id, date_achat DESC
    '''
    mycursor.execute(sql)
    commandes= mycursor.fetchall()


    id_commande = request.args.get('id_commande', None)
    if id_commande != None:
        sql = '''
        SELECT c.id_commande,
        nom_vetement AS nom,
        lc.quantite,
        prix_vetement AS prix,
        ROUND(lc.quantite * v.prix_vetement, 2) AS prix_ligne,
        COUNT(sv2.id_vetement) AS nb_declinaisons,
        t.id_taille AS taille_id,
        libelle_taille
        FROM ligne_commande lc 
        JOIN commande c ON lc.commande_id = c.id_commande
        JOIN stock_vetement sv ON lc.stock_id = sv.id_stock
        JOIN vetement v ON sv.id_vetement = v.id_vetement
        LEFT JOIN taille t ON sv.id_taille = t.id_taille    
        LEFT JOIN stock_vetement sv2 ON sv.id_vetement = sv2.id_vetement
        WHERE c.id_commande = %s    
        GROUP BY nom_vetement, lc.quantite, prix_vetement, t.id_taille, libelle_taille, id_commande, v.id_vetement
        ORDER BY lc.quantite DESC
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
        sql = ''' UPDATE commande SET etat_id = 2 WHERE id_commande = %s'''
        mycursor.execute(sql, commande_id)
        get_db().commit()
    return redirect('/admin/commande/show')