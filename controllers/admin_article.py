#! /usr/bin/python
# -*- coding:utf-8 -*-
import math
import os.path
from random import random

from flask import Blueprint
from flask import request, render_template, redirect, flash
#from werkzeug.utils import secure_filename

from connexion_db import get_db

admin_article = Blueprint('admin_article', __name__,
                          template_folder='templates')


@admin_article.route('/admin/article/show')
def show_article():
    mycursor = get_db().cursor()
    sql = '''SELECT
                v.id_vetement as id_article,
                nom_vetement as nom,
                prix_vetement as prix,
                v.id_type_vetement as type_article_id,
                image as image,
                libelle_type_vetement as libelle,
                sv.stock as stock,
                t.libelle_taille as taille
            FROM vetement v
            JOIN type_vetement tv ON v.id_type_vetement = tv.id_type_vetement
            LEFT JOIN stock_vetement sv ON v.id_vetement = sv.id_vetement
            LEFT JOIN taille t ON sv.id_taille = t.id_taille
            GROUP BY v.id_vetement, sv.id_stock, v.nom_vetement, v.prix_vetement, v.id_type_vetement, v.image, tv.libelle_type_vetement, sv.stock, t.libelle_taille
    '''
    mycursor.execute(sql)
    articles = mycursor.fetchall()

    return render_template('admin/article/show_article.html', articles=articles)



@admin_article.route('/admin/article/add', methods=['GET'])
def add_article():
    mycursor = get_db().cursor()
    sql = ''' SELECT id_type_vetement as id_type_article,
                libelle_type_vetement as libelle
            FROM type_vetement '''
    mycursor.execute(sql)
    type_article = mycursor.fetchall()

    sql = '''SELECT id_taille, libelle_taille FROM taille'''
    mycursor.execute(sql)
    tailles = mycursor.fetchall()
    return render_template('admin/article/add_article.html'
                           ,types_article=type_article,
                           tailles = tailles,
                           #,couleurs=colors
                           #,tailles=tailles
                            )


@admin_article.route('/admin/article/add', methods=['POST'])
def valid_add_article():
    mycursor = get_db().cursor()

    nom = request.form.get('nom', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description', '')
    image = request.files.get('image', '')

    if image:
        filename = 'img_upload'+ str(int(2147483647 * random())) + '.png'
        image.save(os.path.join('static/images/', filename))
    else:
        print("erreur")
        filename=None

    sql = ''' INSERT INTO vetement (nom_vetement, image, prix_vetement, id_type_vetement, description) VALUES (%s, %s, %s, %s, %s) '''

    tuple_add = (nom, filename, prix, type_article_id, description)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    id_vetement = '''SELECT MAX(id_vetement) FROM vetement'''
    mycursor.execute(id_vetement)
    id_vetement = mycursor.fetchone()
    valeur = list(id_vetement.values())[0]

    id_taille = request.form.get('id_taille', '')
    stock = request.form.get('stock', '')

    sql = ''' INSERT INTO stock_vetement (id_vetement, id_taille, stock) VALUES (%s, %s, %s) '''

    tuple_add = (valeur, id_taille, stock)
    mycursor.execute(sql, tuple_add)
    get_db().commit()

    print(u'article ajouté , nom: ', nom, ' - type_article:', type_article_id, ' - prix:', prix,
          ' - description:', description, ' - image:', image)
    message = u'article ajouté , nom:' + nom + '- type_article:' + type_article_id + ' - prix:' + prix + ' - description:' + description + ' - image:' + str(
        image)
    flash(message, 'alert-success')
    return redirect('/admin/article/show')


@admin_article.route('/admin/article/delete', methods=['GET'])
def delete_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = ''' requête admin_article_3 '''
    mycursor.execute(sql, id_article)
    nb_declinaison = mycursor.fetchone()
    if nb_declinaison['nb_declinaison'] > 0:
        message= u'il y a des declinaisons dans cet article : vous ne pouvez pas le supprimer'
        flash(message, 'alert-warning')
    else:
        sql = ''' requête admin_article_4 '''
        mycursor.execute(sql, id_article)
        article = mycursor.fetchone()
        print(article)
        image = article['image']

        sql = ''' requête admin_article_5  '''
        mycursor.execute(sql, id_article)
        get_db().commit()
        if image != None:
            os.remove('static/images/' + image)

        print("un article supprimé, id :", id_article)
        message = u'un article supprimé, id : ' + id_article
        flash(message, 'alert-success')

    return redirect('/admin/article/show')


@admin_article.route('/admin/article/edit', methods=['GET'])
def edit_article():
    id_article=request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''
    requête admin_article_6    
    '''
    mycursor.execute(sql, id_article)
    article = mycursor.fetchone()
    print(article)
    sql = '''
    requête admin_article_7
    '''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()

    # sql = '''
    # requête admin_article_6
    # '''
    # mycursor.execute(sql, id_article)
    # declinaisons_article = mycursor.fetchall()

    return render_template('admin/article/edit_article.html'
                           ,article=article
                           ,types_article=types_article
                         #  ,declinaisons_article=declinaisons_article
                           )


@admin_article.route('/admin/article/edit', methods=['POST'])
def valid_edit_article():
    mycursor = get_db().cursor()
    nom = request.form.get('nom')
    id_article = request.form.get('id_article')
    image = request.files.get('image', '')
    type_article_id = request.form.get('type_article_id', '')
    prix = request.form.get('prix', '')
    description = request.form.get('description')
    sql = '''
       requête admin_article_8
       '''
    mycursor.execute(sql, id_article)
    image_nom = mycursor.fetchone()
    image_nom = image_nom['image']
    if image:
        if image_nom != "" and image_nom is not None and os.path.exists(
                os.path.join(os.getcwd() + "/static/images/", image_nom)):
            os.remove(os.path.join(os.getcwd() + "/static/images/", image_nom))
        # filename = secure_filename(image.filename)
        if image:
            filename = 'img_upload_' + str(int(2147483647 * random())) + '.png'
            image.save(os.path.join('static/images/', filename))
            image_nom = filename

    sql = '''  requête admin_article_9 '''
    mycursor.execute(sql, (nom, image_nom, prix, type_article_id, description, id_article))

    get_db().commit()
    if image_nom is None:
        image_nom = ''
    message = u'article modifié , nom:' + nom + '- type_article :' + type_article_id + ' - prix:' + prix  + ' - image:' + image_nom + ' - description: ' + description
    flash(message, 'alert-success')
    return redirect('/admin/article/show')







@admin_article.route('/admin/article/avis/<int:id>', methods=['GET'])
def admin_avis(id):
    mycursor = get_db().cursor()
    article=[]
    commentaires = {}
    return render_template('admin/article/show_avis.html'
                           , article=article
                           , commentaires=commentaires
                           )


@admin_article.route('/admin/comment/delete', methods=['POST'])
def admin_avis_delete():
    mycursor = get_db().cursor()
    article_id = request.form.get('idArticle', None)
    userId = request.form.get('idUser', None)

    return admin_avis(article_id)
