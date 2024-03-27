#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import request, render_template, redirect, abort, flash, session

from connexion_db import get_db

client_panier = Blueprint('client_panier', __name__,
                          template_folder='templates')

@client_panier.route('/client/panier/add', methods=['POST'])
def client_panier_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article')
    quantite = request.form.get('quantite')
    id_declinaison = request.form.get('id_declinaison_article')

    sql = '''
    SELECT *
    FROM ligne_panier
    JOIN stock_vetement on ligne_panier.stock_id = stock_vetement.id_stock
    WHERE id_vetement = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    article_panier = mycursor.fetchone()

    sql_select_article = 'SELECT * FROM vetement WHERE id_vetement = %s'
    mycursor.execute(sql_select_article, (id_article,))

    if id_article:
        # ajout dans le panier d'une déclinaison d'un article (si 1 declinaison : immédiat sinon => vu pour faire un choix
        sql = '''SELECT id_stock as id_declinaison_article,
            sv.id_taille as id_taille,
            t.libelle_taille as libelle_taille,
            stock
            FROM stock_vetement sv
            JOIN taille t ON sv.id_taille = t.id_taille
            WHERE id_vetement = %s'''
        mycursor.execute(sql, id_article)
        declinaisons = mycursor.fetchall()
        if len(declinaisons) == 1 and article_panier is not None and article_panier['quantite'] >= 1:
            tuple_update = (quantite, article_panier["id_stock"], id_client)
            sql = ''' 
                UPDATE ligne_panier
                SET quantite = quantite + %s
                WHERE stock_id = %s AND utilisateur_id = %s
                '''
            mycursor.execute(sql, tuple_update)
            dec_stock()
            get_db().commit()
            return redirect('/client/article/show')
        if len(declinaisons) == 1:
            id_declinaison_article = declinaisons[0]['id_declinaison_article']
            tuple_insert = (id_client, id_declinaison_article, quantite)
            sql = '''
                        INSERT INTO ligne_panier (utilisateur_id, stock_id, quantite, date_ajout)
                        VALUES (%s, %s, %s, current_timestamp)
                        '''
            mycursor.execute(sql, tuple_insert)
            dec_stock()
            get_db().commit()
            return redirect('/client/article/show')
        elif len(declinaisons) == 0:
            abort("pb nb de declinaison")

    if id_declinaison:
        sql = '''
            SELECT *
            FROM ligne_panier
            JOIN stock_vetement on ligne_panier.stock_id = stock_vetement.id_stock
            WHERE id_stock = %s AND utilisateur_id = %s
            '''
        mycursor.execute(sql, (id_declinaison, id_client))
        article_panier_stock = mycursor.fetchone()

        if article_panier_stock is not None and article_panier_stock['quantite'] >= 1:
            tuple_update = (quantite, article_panier_stock["id_stock"], id_client)
            sql = ''' 
                UPDATE ligne_panier
                SET quantite = quantite + %s
                WHERE stock_id = %s AND utilisateur_id = %s
                '''
            mycursor.execute(sql, tuple_update)
            dec_stock()
            get_db().commit()
        else:
            tuple_insert = (id_client, id_declinaison, quantite)
            sql = '''INSERT INTO ligne_panier (utilisateur_id, stock_id, quantite, date_ajout)
                     VALUES (%s, %s, %s, current_timestamp)
                   '''
            mycursor.execute(sql, tuple_insert)
            dec_stock()
            get_db().commit()

    else:
        sql = '''SELECT id_stock as id_declinaison_article,
                        sv.id_taille as id_taille,
                        t.libelle_taille as libelle_taille,
                        stock
                        FROM stock_vetement sv
                        JOIN taille t ON sv.id_taille = t.id_taille
                        WHERE id_vetement = %s'''
        mycursor.execute(sql, id_article)
        declinaisons = mycursor.fetchall()


        sql = '''SELECT id_vetement as id_article,
                nom_vetement as nom,
                prix_vetement as prix,
                image
                FROM vetement
                WHERE id_vetement = %s'''
        mycursor.execute(sql, id_article)
        article = mycursor.fetchone()
        return render_template('client/boutique/declinaison_article.html'
                                   , declinaisons=declinaisons
                                   , quantite=quantite
                                   , article=article)
    get_db().commit()
    return redirect('/client/article/show')

@client_panier.route('/client/panier/delete', methods=['POST'])
def client_panier_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article','')
    id_declinaison_article = request.form.get('id_declinaison_article', None)

    sql = ''' SELECT *
    FROM ligne_panier
    WHERE stock_id = %s AND utilisateur_id = %s ''' #selection de la ligne du panier pour l'article et l'utilisateur connecté
    mycursor.execute(sql, (id_declinaison_article, id_client))
    article_panier=mycursor.fetchone()

    if article_panier is not None and article_panier['quantite'] > 1:
        sql = ''' UPDATE ligne_panier
        SET quantite = quantite - 1
        WHERE stock_id = %s AND utilisateur_id = %s  ''' #mise à jour de la quantité dans le panier => -1 article
        mycursor.execute(sql, (id_declinaison_article, id_client))
    else:
        sql = ''' DELETE FROM ligne_panier WHERE stock_id = %s AND utilisateur_id = %s''' #suppression de la ligne de panier
        mycursor.execute(sql, (id_declinaison_article, id_client))
    # mise à jour du stock de l'article disponible
    sql2=''' UPDATE stock_vetement SET stock = stock + 1 WHERE id_stock = %s '''
    mycursor.execute(sql2, (id_declinaison_article,))
    get_db().commit()
    return redirect('/client/article/show')





@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']

    sql_select = ''' SELECT stock_id, quantite
        FROM ligne_panier
        WHERE utilisateur_id = %s '''
    mycursor.execute(sql_select, (client_id,))
    items_panier = mycursor.fetchall()
    for item in items_panier:
        sql = ''' DELETE FROM ligne_panier
        WHERE utilisateur_id = %s AND stock_id = %s '''
        mycursor.execute(sql, (client_id, item['stock_id']))
        sql2=''' UPDATE stock_vetement
        SET stock = stock + %s
        WHERE id_vetement = %s '''
        mycursor.execute(sql2, (item['quantite'], item['stock_id']))
    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_declinaison_article = request.form.get('id_declinaison_article')

    sql = ''' SELECT quantite
        FROM ligne_panier
        WHERE utilisateur_id = %s and stock_id = %s ''' #selection de ligne du panier
    mycursor.execute(sql, (id_client, id_declinaison_article))
    quantite = mycursor.fetchone().get("quantite")

    sql = ''' DELETE FROM ligne_panier
        WHERE utilisateur_id = %s AND stock_id = %s''' #suppression de la ligne du panier
    mycursor.execute(sql, (id_client, id_declinaison_article))

    sql2=''' UPDATE stock_vetement 
    SET stock = stock + %s
    WHERE id_stock = %s''' #mise à jour du stock de l'article : stock = stock + qté de la ligne
    mycursor.execute(sql2, (quantite, id_declinaison_article))

    get_db().commit()
    return redirect('/client/article/show')






@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():

    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types')
    tup_filtre = ()

    sql = ''' SELECT v.id_vetement as id_article, 
                nom_vetement as nom, 
                prix_vetement as prix,  
                image as image, 
                id_type_vetement as id_type,
                SUM(sv.stock) as stock,
                COUNT(sv.id_stock) as nb_declinaison
              FROM vetement v
              LEFT JOIN stock_vetement sv on v.id_vetement = sv.id_vetement
              WHERE 1=1 '''

    if filter_word is not None and filter_word != '':
        sql += "AND nom_vetement LIKE %s "
        tup_filtre += ('%' + filter_word + '%',)

    if (filter_prix_max is not None and filter_prix_max != '') and (filter_prix_min is not None and filter_prix_min != ''):
        if filter_prix_max < filter_prix_min:
            flash("Le prix maximum ne peut pas être inférieur au prix minimum", "alert-danger")
            return redirect('/client/article/show')
        if filter_prix_max.isalpha() or filter_prix_min.isalpha():
            flash("Les prix doivent être des nombres", "alert-danger")
            return redirect('/client/article/show')
        sql += "AND prix_vetement BETWEEN %s AND %s "
        tup_filtre += (filter_prix_min, filter_prix_max)
    elif (filter_prix_max is not None and filter_prix_max != ''):
        if filter_prix_max.isalpha():
            flash("Le prix maximum doit être un nombre", "alert-danger")
            return redirect('/client/article/show')
        sql += "AND prix_vetement <= %s "
        tup_filtre += (filter_prix_max,)
    elif (filter_prix_min is not None and filter_prix_min != ''):
        if filter_prix_min.isalpha():
            flash("Le prix minimum doit être un nombre", "alert-danger")
            return redirect('/client/article/show')
        sql += "AND prix_vetement >= %s "
        tup_filtre += (filter_prix_min,)

    if filter_types is not None and len(filter_types) > 0:
        if len(filter_types) == 1:
            sql += "AND id_type_vetement = %s "
            tup_filtre += (filter_types[0],)
        else:
            for i in range(len(filter_types)):
                if i == 0:
                    sql += "AND (id_type_vetement = %s "
                elif i == len(filter_types) - 1:
                    sql += "OR id_type_vetement = %s) "
                else:
                    sql += "OR id_type_vetement = %s "
                tup_filtre += (filter_types[i],)

    sql += '''GROUP BY v.id_vetement,
                      nom_vetement,
                      prix_vetement,
                      image,
                      id_type_vetement'''

    mycursor = get_db().cursor()
    mycursor.execute(sql, tup_filtre)
    articles = mycursor.fetchall()

    session['filter_word'] = filter_word
    session['filter_prix_min'] = filter_prix_min
    session['filter_prix_max'] = filter_prix_max
    session['filter_types'] = filter_types


    id_client = session['id_user']
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
           ORDER BY quantite DESC
                      '''
    mycursor.execute(sql, (id_client,))
    articles_panier = mycursor.fetchall()


    sql = '''SELECT id_type_vetement  AS id_type_article
             ,libelle_type_vetement AS libelle
             FROM type_vetement
             ORDER BY  libelle_type_vetement
                '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    sql = ''' SELECT SUM(v.prix_vetement * lp.quantite) AS prix_total
            FROM ligne_panier lp
            JOIN stock_vetement ON lp.stock_id = stock_vetement.id_stock
            JOIN vetement v ON stock_vetement.id_vetement = v.id_vetement
            WHERE lp.utilisateur_id = %s; '''
    mycursor.execute(sql, (id_client,))
    prix_total = mycursor.fetchone()

    return render_template('client/boutique/panier_article.html', articles=articles, articles_panier=articles_panier, prix_total=prix_total,items_filtre=types_article)


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    return redirect('/client/article/show')


def dec_stock():
    id_declinaison_article = request.form.get('id_declinaison_article')
    id_article = request.form.get('id_article')
    quantite = request.form.get('quantite')

    if (id_declinaison_article):
        mycursor = get_db().cursor()
        sql = ''' UPDATE stock_vetement 
        SET stock = stock - %s
        WHERE id_stock = %s
        '''
        mycursor.execute(sql, (quantite, id_declinaison_article ))
        get_db().commit()
    else:
        mycursor = get_db().cursor()
        sql = ''' UPDATE stock_vetement 
                SET stock = stock - %s
                WHERE id_vetement = %s
                '''
        mycursor.execute(sql, (quantite, id_article))
        get_db().commit()