#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_liste_envies = Blueprint('client_liste_envies', __name__,
                                template_folder = 'templates')


@client_liste_envies.route('/client/envie/add', methods = ['get'])
def client_liste_envies_add():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''INSERT INTO liste_envie  (vetement_id, utilisateur_id,date_liste_envie, ordre) 
SELECT %s, %s, now(),IFNULL(MAX(ordre), 0) + 1 FROM liste_envie ;
'''
    mycursor.execute(sql, (id_article, id_client,))
    get_db().commit()
    flash('Votre article a été ajouté dans votre liste d\'envie', 'success')
    return redirect('/client/article/show')

@client_liste_envies.route('/client/envie/delete', methods = ['get'])
def client_liste_envies_delete():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    www = request.referrer
    sql = '''DELETE FROM liste_envie le WHERE le.vetement_id = %s AND le.utilisateur_id = %s'''
    mycursor.execute(sql, (id_article, id_client,))
    get_db().commit()
    if www.endswith("/client/envies/show"):
        flash('Vous avez supprimez un article de votre liste d\'envie', 'error')
        return redirect('/client/envies/show')
    else:
        return redirect('/client/article/show')



@client_liste_envies.route('/client/envie/delete2', methods=['get'])
def client_liste_envies_delete2(id_client):
    mycursor = get_db().cursor()
    sql_select = '''SELECT ligne_panier.vetement_id FROM ligne_panier 
                    JOIN liste_envie on liste_envie.utilisateur_id = ligne_panier.utilisateur_id
                    WHERE ligne_panier.utilisateur_id = %s
                '''
    mycursor.execute(sql_select, (id_client,))
    results = mycursor.fetchall()
    panier_envie = [str(item['vetement_id']) for item in results]
    sql_del = '''DELETE FROM liste_envie le WHERE le.vetement_id IN (%s) AND le.utilisateur_id = %s'''
    for id_article in panier_envie:
        mycursor.execute(sql_del, (id_article, id_client,))
    get_db().commit()
    flash('Vous avez supprimé un article de votre liste d\'envie', 'error')
    return redirect('/client/commande/show')



@client_liste_envies.route('/client/envies/show', methods=['get'])
def client_liste_envies_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']

    # Sélection des articles dans la liste d'envies
    sql_liste_envies = '''
    SELECT vetement.nom_vetement AS nom, vetement.id_vetement AS id_article, 
           vetement.prix_vetement AS prix, stock_vetement.stock, vetement.image 
    FROM liste_envie le
    LEFT JOIN vetement ON vetement.id_vetement = le.vetement_id
    JOIN stock_vetement ON stock_vetement.id_vetement = vetement.id_vetement
    WHERE le.utilisateur_id = %s
    ORDER BY le.ordre ASC, le.date_liste_envie DESC;
    '''
    mycursor.execute(sql_liste_envies, (id_client,))
    articles_liste_envies = mycursor.fetchall()
    nb_liste_envies = len(articles_liste_envies)

    # Sélection des articles dans l'historique
    sql_historique = '''
    SELECT h.vetement_id AS id_article, vetement.nom_vetement AS nom, 
           vetement.prix_vetement AS prix, vetement.image AS image 
    FROM historique h
    JOIN vetement ON vetement.id_vetement = h.vetement_id
    WHERE utilisateur_id = %s
    ORDER BY h.date_historique DESC;
    '''
    mycursor.execute(sql_historique, (id_client,))
    articles_historique = mycursor.fetchall()

    # Suppression des enregistrements anciens dans l'historique
    sql_del = '''
    DELETE FROM historique h
    WHERE h.date_historique < DATE_SUB(NOW(), INTERVAL 1 MONTH) AND h.utilisateur_id = %s;
    '''
    mycursor.execute(sql_del, (id_client,))
    get_db().commit()

    articles_historique = articles_historique[0:6]
    print(articles_historique)

    return render_template('client/liste_envies/liste_envies_show.html',
                           articles_liste_envies=articles_liste_envies,
                           articles_historique=articles_historique,
                           nb_liste_envies=nb_liste_envies)


def client_historique_add(id_article, id_client):
    mycursor = get_db().cursor()
    sql_select = '''SELECT * FROM historique h WHERE h.vetement_id = %s AND h.utilisateur_id = %s'''
    mycursor.execute(sql_select, (id_article, id_client))
    containt = mycursor.fetchone()

    if containt:
        sql_update = '''UPDATE historique h SET h.date_historique = NOW() WHERE h.vetement_id = %s AND h.utilisateur_id = %s AND h.date_historique = %s'''
        mycursor.execute(sql_update, (id_article, id_client, containt['date_historique']))
        get_db().commit()
    else:
        sql_insert = '''INSERT INTO historique (utilisateur_id, vetement_id,Image, date_historique) VALUES (%s, %s,Null ,NOW())'''
        mycursor.execute(sql_insert, (id_client, id_article))
        get_db().commit()

    return redirect('/client/envies/show')



@client_liste_envies.route('/client/envies/up', methods = ['get'])
def client_liste_envies_article_moveup():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''UPDATE liste_envie le 
                SET le.ordre = le.ordre - 2 
                WHERE le.utilisateur_id = %s AND le.vetement_id = %s'''
    mycursor.execute(sql, (id_client, id_article,))
    get_db().commit()
    flash('Article déplacé vers le haut dans la liste d\'envies', 'success')
    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/down', methods = ['get'])
def client_liste_envies_article_movedown():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql = '''UPDATE liste_envie le 
                    SET le.ordre = le.ordre + 2 
                    WHERE le.utilisateur_id = %s AND le.vetement_id = %s'''
    mycursor.execute(sql, (id_client, id_article,))
    get_db().commit()
    flash('Article déplacé vers le bas dans la liste d\'envies', 'success')
    return redirect('/client/envies/show')


@client_liste_envies.route('/client/envies/last', methods=['get'])
def client_liste_envies_article_setlast():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql_select = '''
            SELECT MAX(le.ordre) + 1 AS upd_ordre  
            FROM liste_envie le
            WHERE le.utilisateur_id = %s
    '''
    mycursor.execute(sql_select, (id_client,))
    min = mycursor.fetchone()
    sql_upd = '''UPDATE liste_envie le
            SET le.ordre = %s
            WHERE le.utilisateur_id = %s AND le.vetement_id = %s;'''
    mycursor.execute(sql_upd, (min["upd_ordre"], id_client, id_article,))
    get_db().commit()
    flash('Article placé dernier dans la liste d\'envies', 'success')
    return redirect('/client/envies/show')




@client_liste_envies.route('/client/envies/first', methods = ['get'])
def client_liste_envies_article_setfirst():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_article = request.args.get('id_article')
    sql_select = '''
            SELECT MIN(le.ordre) - 1 AS upd_ordre  
            FROM liste_envie le 
            WHERE le.utilisateur_id = %s '''
    mycursor.execute(sql_select, (id_client,))
    max = mycursor.fetchone()
    sql_upd ='''UPDATE liste_envie le 
        SET le.ordre = %s
        WHERE le.utilisateur_id = %s AND le.vetement_id = %s;'''
    mycursor.execute(sql_upd, (max["upd_ordre"],id_client, id_article, ))
    get_db().commit()
    flash('Article placé premier dans la liste d\'envies', 'success')
    return redirect('/client/envies/show')

