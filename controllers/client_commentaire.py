#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session, g

from connexion_db import get_db

from controllers.client_liste_envies import client_historique_add

client_commentaire = Blueprint('client_commentaire', __name__,
                               template_folder='templates')


@client_commentaire.route('/client/article/details', methods=['GET'])
def client_article_details():
    mycursor = get_db().cursor()
    id_article = request.args.get('id_article', None)
    id_client = session['id_user']

    # partie 4
    # client_historique_add(id_article, id_client)

    sql = '''
        SELECT ve.nom_vetement as nom, ve.prix_vetement as prix, ve.image, ve.description, ve.id_vetement as id_article, ROUND(AVG(n.note), 2) as moyenne_notes, COUNT(n.note) as nb_notes
        FROM vetement ve
        LEFT JOIN note n ON ve.id_vetement = n.vetement_id
        WHERE ve.id_vetement = %s 
        GROUP BY ve.nom_vetement, ve.prix_vetement, ve.image, ve.description, ve.id_vetement'''


    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    if article is None:
        abort(404, "pb id article")

    sql = '''
    SELECT c.contenu as commentaire, u.nom, u.id_utilisateur, c.date_ajout as date_publication, c.vetement_id as id_article
    FROM commentaire c
    JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
    WHERE c.vetement_id = %s
    '''
    
    mycursor.execute(sql, ( id_article))
    commentaires = mycursor.fetchall()
    
    
    sql = '''    
    SELECT COUNT(lc.vetement_id) as nb_commandes_article
    FROM ligne_commande lc
    JOIN commande c ON lc.commande_id = c.id_commande
    JOIN utilisateur u ON c.utilisateur_id = u.id_utilisateur
    WHERE u.id_utilisateur = %s AND lc.vetement_id = %s
    '''
    
    mycursor.execute(sql, (id_client, id_article))
    commandes_articles = mycursor.fetchone()
    
    sql = ''' SELECT note
    FROM note 
    WHERE utilisateur_id = %s AND vetement_id = %s'''
    mycursor.execute(sql, (id_client, id_article))
    note = mycursor.fetchone()
    
    if note:
        note=note['note']
    
    sql = '''
    SELECT
        (SELECT COUNT(id_commentaire) FROM commentaire WHERE utilisateur_id = %s AND vetement_id = %s) as nb_commentaires_utilisateur,
        (SELECT COUNT(id_commentaire) FROM commentaire WHERE vetement_id = %s) as nb_commentaires_total
    '''

    mycursor.execute(sql, (id_client, id_article, id_article))
    nb_commentaires = mycursor.fetchone()

    return render_template('client/article_info/article_details.html', article=article, commandes_articles=commandes_articles, note=note,  nb_commentaires=nb_commentaires, commentaires=commentaires)


@client_commentaire.route('/client/commentaire/add', methods=['POST'])
def client_comment_add():
    mycursor = get_db().cursor()
    
    commentaire = request.form.get('commentaire', None)
    id_article = request.form.get('id_article', None)
    id_client = session['id_user']
    
    if commentaire == '':
        flash(u'Commentaire non prise en compte')
        return redirect('/client/article/details?id_article='+id_article)
    if commentaire != None and len(commentaire) > 0 and len(commentaire) < 3:
        flash(u'Commentaire avec plus de 2 caractères',
              'alert-warning')              #
        return redirect('/client/article/details?id_article='+id_article)
    
    sql = ''' 
    SELECT * 
    FROM commande c
    WHERE c.utilisateur_id = %s'''
    
    mycursor.execute(sql, (id_client,))
    check_commande = mycursor.fetchall()
    
    if not check_commande:
        flash('Vous devez avoir passé une commande pour pouvoir commenter', 'alert-warning')
        return redirect('/client/article/details?id_article='+id_article)
    
    
    sql = ''' SELECT * FROM commentaire WHERE utilisateur_id = %s AND vetement_id = %s '''
    mycursor.execute(sql, (id_client, id_article))
    check_nbr_com = mycursor.fetchall()
    
    if len(check_nbr_com) >= 5:
        flash('Nombre maximal de commentaire atteint pour cette article', 'alert-warning')
        return redirect('/client/article/details?id_article='+id_article)

    sql = ''' INSERT INTO commentaire(contenu, date_ajout, utilisateur_id, vetement_id) 
    VALUES (%s, NOW(), %s, %s) '''
    
    mycursor.execute(sql, (commentaire, id_client, id_article))
    get_db().commit()
    
    return redirect('/client/article/details?id_article='+id_article)


@client_commentaire.route('/client/commentaire/delete', methods=['POST'])
def client_comment_detete():
    mycursor = get_db().cursor()
    
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)
    date_publication = request.form.get('date_publication', None)
    
    print(request.form)
    
    sql = ''' DELETE FROM commentaire WHERE utilisateur_id = %s AND vetement_id = %s AND date_ajout = %s'''
    
    mycursor.execute(sql, (id_client, id_article, date_publication))   
    get_db().commit()
    return redirect('/client/article/details?id_article='+id_article)


@client_commentaire.route('/client/note/add', methods=['POST'])
def client_note_add():
    mycursor = get_db().cursor()
    
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    
    if note == '':
        flash(u'Note non prise en compte', 'alert-warning')
        return redirect('/client/article/details?id_article='+id_article)
    
    sql = ''' INSERT INTO note (note, utilisateur_id, vetement_id) 
    VALUES (%s, %s, %s)'''
    mycursor.execute(sql, (note, id_client, id_article))
    get_db().commit()

    return redirect('/client/article/details?id_article='+id_article)


@client_commentaire.route('/client/note/edit', methods=['POST'])
def client_note_edit():
    mycursor = get_db().cursor()
    
    id_client = session['id_user']
    note = request.form.get('note', None)
    id_article = request.form.get('id_article', None)
    
    sql = ''' UPDATE note SET note = %s WHERE utilisateur_id = %s AND vetement_id = %s'''
    mycursor.execute(sql, (note, id_client, id_article))
    get_db().commit()
    
    return redirect('/client/article/details?id_article='+id_article)


@client_commentaire.route('/client/note/delete', methods=['POST'])
def client_note_delete():
    mycursor = get_db().cursor()
    
    id_client = session['id_user']
    id_article = request.form.get('id_article', None)

    sql = ''' DELETE FROM note WHERE utilisateur_id = %s AND vetement_id = %s'''
    mycursor.execute(sql, (id_client, id_article))
    get_db().commit()
    
    return redirect('/client/article/details?id_article='+id_article)
