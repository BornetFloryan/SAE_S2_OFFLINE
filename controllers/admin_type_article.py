#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, flash, session

from connexion_db import get_db

admin_type_article = Blueprint('admin_type_article', __name__,
                        template_folder='templates')

@admin_type_article.route('/admin/type-article/show')
def show_type_article():
    mycursor = get_db().cursor()
    sql = '''SELECT tv.id_type_vetement as id_type_article, 
                COUNT(v.id_type_vetement) as nbr_articles,
                tv.libelle_type_vetement as libelle
                FROM type_vetement tv
                LEFT JOIN vetement v on tv.id_type_vetement = v.id_type_vetement
                GROUP BY tv.id_type_vetement, tv.libelle_type_vetement'''
    mycursor.execute(sql)
    types_article = mycursor.fetchall()
    return render_template('admin/type_article/show_type_article.html', types_article=types_article)

@admin_type_article.route('/admin/type-article/add', methods=['GET'])
def add_type_article():
    return render_template('admin/type_article/add_type_article.html')

@admin_type_article.route('/admin/type-article/add', methods=['POST'])
def valid_add_type_article():
    libelle = request.form.get('libelle', '')
    tuple_insert = (libelle,)
    mycursor = get_db().cursor()
    sql = ''' INSERT INTO type_vetement (libelle_type_vetement) VALUES (%s) '''
    mycursor.execute(sql, tuple_insert)
    get_db().commit()
    message = u'type ajouté , libellé :'+libelle
    flash(message, 'alert-success')
    return redirect('/admin/type-article/show') #url_for('show_type_article')

@admin_type_article.route('/admin/type-article/delete', methods=['GET'])
def delete_type_article():
    id_type_article = request.args.get('id_type_article', '')
    mycursor = get_db().cursor()
    sql = '''SELECT * FROM vetement WHERE id_type_vetement = %s'''
    mycursor.execute(sql, (id_type_article,))
    articles = mycursor.fetchall()
    if len(articles) == 0:
        sql = '''DELETE FROM type_vetement WHERE id_type_vetement = %s'''
        mycursor.execute(sql, (id_type_article,))
        get_db().commit()
        flash(u'suppression type article, id : ' + id_type_article, 'alert-success')
        return redirect('/admin/type-article/show')
    else:
        flash(u'Impossible de supprimer ce type d\'article, il est utilisé par des articles', 'alert-danger')
        return redirect('/admin/article/show?id_type_article=' + id_type_article)


@admin_type_article.route('/admin/type-article/edit', methods=['GET'])
def edit_type_article():
    id_type_article = request.args.get('id_type_article', '')
    mycursor = get_db().cursor()
    sql = '''SELECT tv.id_type_vetement as id_type_article,
                tv.libelle_type_vetement as libelle
            FROM type_vetement tv WHERE id_type_vetement = %s
            GROUP BY id_type_vetement, libelle_type_vetement'''
    mycursor.execute(sql, (id_type_article,))
    type_article = mycursor.fetchone()
    return render_template('admin/type_article/edit_type_article.html', type_article=type_article)

@admin_type_article.route('/admin/type-article/edit', methods=['POST'])
def valid_edit_type_article():
    libelle = request.form['libelle']
    id_type_article = request.form.get('id_type_article', '')
    tuple_update = (libelle, id_type_article)
    mycursor = get_db().cursor()
    sql = ''' UPDATE type_vetement SET libelle_type_vetement = %s WHERE id_type_vetement = %s '''
    mycursor.execute(sql, tuple_update)
    get_db().commit()
    flash(u'type article modifié, id: ' + id_type_article + " libelle : " + libelle, 'alert-success')
    return redirect('/admin/type-article/show')








