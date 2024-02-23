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

    sql = '''
    SELECT *
    FROM ligne_panier
    WHERE vetement_id = %s AND utilisateur_id = %s
    '''
    mycursor.execute(sql, (id_article, id_client))
    article_panier = mycursor.fetchone()

    sql_select_article = 'SELECT * FROM vetement WHERE id_vetement = %s'
    mycursor.execute(sql_select_article, (id_article,))
    article = mycursor.fetchone()

    if article_panier is not None and article_panier['quantite'] >= 1:
        tuple_update = (quantite, id_article, id_client)
        print(quantite, id_article, id_client)
        sql = ''' 
        UPDATE ligne_panier
        SET quantite = quantite + %s
        WHERE vetement_id = %s AND utilisateur_id = %s
        '''
        mycursor.execute(sql, tuple_update)
        dec_stock()
    else:
        tuple_insert = (id_client, id_article, quantite)
        sql = '''
        INSERT INTO ligne_panier (utilisateur_id, vetement_id, quantite, date_ajout)
        VALUES (%s, %s, %s, current_timestamp)
        '''
        mycursor.execute(sql, tuple_insert)
        dec_stock()

    # ajout dans le panier d'une déclinaison d'un article (si 1 declinaison : immédiat sinon => vu pour faire un choix
    sql = '''  SELECT *
    FROM taille
    LEFT JOIN stock_vetement ON stock_vetement.id_taille = taille.id_taille
    WHERE stock_vetement.id_vetement = %s  '''
    mycursor.execute(sql, (id_article))
    declinaisons = mycursor.fetchall()
    if len(declinaisons) == 1:
        id_declinaison_article = declinaisons[0]['id_taille']
    elif len(declinaisons) == 0:
        abort("pb nb de declinaison")
    else:
        sql = '''  '''
        mycursor.execute(sql, (id_article))
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
    # ---------
    # partie 2 : on supprime une déclinaison de l'article
    # id_declinaison_article = request.form.get('id_declinaison_article', None)

    sql = ''' SELECT *
    FROM ligne_panier
    WHERE vetement_id = %s AND utilisateur_id = %s ''' #selection de la ligne du panier pour l'article et l'utilisateur connecté
    mycursor.execute(sql, (id_article, id_client))
    article_panier=mycursor.fetchone()

    if article_panier is not None and article_panier['quantite'] > 1:
        sql = ''' UPDATE ligne_panier
        SET quantite = quantite - 1
        WHERE vetement_id = %s AND utilisateur_id = %s  ''' #mise à jour de la quantité dans le panier => -1 article
        mycursor.execute(sql, (id_article, id_client))
    else:
        sql = ''' DELETE FROM ligne_panier WHERE vetement_id = %s AND utilisateur_id = %s''' #suppression de la ligne de panier
        mycursor.execute(sql, (id_article, id_client))
    # mise à jour du stock de l'article disponible
    sql2=''' UPDATE stock_vetement SET stock = stock + 1 WHERE id_vetement = %s '''
    mycursor.execute(sql2, (id_article,))
    get_db().commit()
    return redirect('/client/article/show')





@client_panier.route('/client/panier/vider', methods=['POST'])
def client_panier_vider():
    mycursor = get_db().cursor()
    client_id = session['id_user']

    sql_select = ''' SELECT vetement_id, quantite
        FROM ligne_panier
        WHERE utilisateur_id = %s '''
    mycursor.execute(sql_select, (client_id,))
    items_panier = mycursor.fetchall()
    for item in items_panier:
        sql = ''' DELETE FROM ligne_panier
        WHERE utilisateur_id = %s AND vetement_id = %s '''
        mycursor.execute(sql, (client_id, item['vetement_id']))
        sql2=''' UPDATE stock_vetement
        SET stock = stock + %s
        WHERE id_vetement = %s '''
        mycursor.execute(sql2, (item['quantite'], item['vetement_id']))
    get_db().commit()
    return redirect('/client/article/show')


@client_panier.route('/client/panier/delete/line', methods=['POST'])
def client_panier_delete_line():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.form.get('id_article', '')
    #id_declinaison_article = request.form.get('id_declinaison_article')

    sql = ''' SELECT quantite
        FROM ligne_panier
        WHERE utilisateur_id = %s and vetement_id = %s ''' #selection de ligne du panier
    mycursor.execute(sql, (id_client, id_article))
    quantite = mycursor.fetchone().get("quantite")
    print(quantite)

    sql = ''' DELETE FROM ligne_panier
        WHERE utilisateur_id = %s AND vetement_id = %s  ''' #suppression de la ligne du panier
    mycursor.execute(sql, (id_client, id_article))
    sql2=''' UPDATE stock_vetement 
    SET stock = stock + %s
    WHERE id_vetement = %s ''' #mise à jour du stock de l'article : stock = stock + qté de la ligne pour l'
    mycursor.execute(sql2, (quantite, id_article))

    get_db().commit()
    return redirect('/client/article/show')






@client_panier.route('/client/panier/filtre', methods=['POST'])
def client_panier_filtre():    
    
    filter_word = request.form.get('filter_word', None)
    filter_prix_min = request.form.get('filter_prix_min', None)
    filter_prix_max = request.form.get('filter_prix_max', None)
    filter_types = request.form.getlist('filter_types')
    tup_filtre = ()

    sql = ''' SELECT vetement.id_vetement as id_article, 
                nom_vetement as nom, 
                prix_vetement as prix,  
                image as image, 
                id_type_vetement as id_type,
                stock_vetement.stock as stock 
              FROM vetement
              LEFT JOIN stock_vetement on vetement.id_vetement = stock_vetement.id_vetement
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

    mycursor = get_db().cursor()
    mycursor.execute(sql, tup_filtre)
    articles = mycursor.fetchall()

    session['filter_word'] = filter_word
    session['filter_prix_min'] = filter_prix_min
    session['filter_prix_max'] = filter_prix_max
    session['filter_types'] = filter_types
    
    
    id_client = session['id_user']
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
    

    sql = '''SELECT id_type_vetement  AS id_type_article
             ,libelle_type_vetement AS libelle
             FROM type_vetement
             ORDER BY  libelle_type_vetement
                '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    return render_template('client/boutique/panier_article.html', articles=articles, articles_panier=articles_panier, items_filtre=types_article)


@client_panier.route('/client/panier/filtre/suppr', methods=['POST'])
def client_panier_filtre_suppr():
    session.pop('filter_word', None)
    session.pop('filter_prix_min', None)
    session.pop('filter_prix_max', None)
    session.pop('filter_types', None)
    return redirect('/client/article/show')





def dec_stock():
    id_vetement = request.form.get('id_article')
    quantite = request.form.get('quantite')
    mycursor = get_db().cursor()
    sql = ''' UPDATE stock_vetement 
    SET stock = stock - %s
    WHERE id_vetement = %s
    '''
    mycursor.execute(sql, (quantite, id_vetement))
    get_db().commit()

