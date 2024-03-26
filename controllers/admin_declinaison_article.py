#! /usr/bin/python
# -*- coding:utf-8 -*-

from flask import Blueprint
from flask import request, render_template, redirect, flash
from connexion_db import get_db

admin_declinaison_article = Blueprint('admin_declinaison_article', __name__,
                                      template_folder='templates')


@admin_declinaison_article.route('/admin/declinaison_article/add')
def add_declinaison_article():
    id_article = request.args.get('id_article')
    mycursor = get_db().cursor()
    sql = '''SELECT id_vetement as id_article,  
    image
    FROM vetement v 
    WHERE id_vetement = %s'''
    mycursor.execute(sql, (id_article,))
    article = mycursor.fetchone()

    sql2 = '''SELECT id_taille FROM stock_vetement WHERE id_vetement = %s AND id_taille != 1'''
    mycursor.execute(sql2, (article["id_article"],))
    taille_unique = mycursor.fetchone()
    if taille_unique:
        sql3 = '''SELECT id_taille, libelle_taille as libelle FROM taille WHERE id_taille != 1'''
        mycursor.execute(sql3)
        tailles = mycursor.fetchall()
    else:
        sql3 = '''SELECT id_taille, libelle_taille as libelle FROM taille'''
        mycursor.execute(sql3)
        tailles = mycursor.fetchall()

    sql4 = '''SELECT id_taille FROM stock_vetement WHERE id_vetement = %s AND id_taille = 1'''
    mycursor.execute(sql4, (article["id_article"],))
    taille_unique = mycursor.fetchone()

    if (taille_unique and taille_unique["id_taille"] == 1):
        d_taille_uniq = 1
    else:
        d_taille_uniq = None
    d_couleur_uniq = 1
    return render_template('admin/article/add_declinaison_article.html'
                           , article=article
                           , tailles=tailles
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_article.route('/admin/declinaison_article/add', methods=['POST'])
def valid_add_declinaison_article():
    mycursor = get_db().cursor()
    id_article = request.form.get('id_article')
    stock = request.form.get('stock')
    taille_id = request.form.get('taille')
    sql = '''SELECT id_taille FROM stock_vetement WHERE id_vetement = %s AND id_taille = %s'''
    mycursor.execute(sql, (id_article, taille_id))
    taille = mycursor.fetchone()
    if taille and int(taille["id_taille"]) == int(taille_id):
        flash(u'Information : doublon sur cette déclinaison, seul le stock a été mise à jour', 'alert-danger')
        sql = '''UPDATE stock_vetement SET id_taille = %s, stock = stock + %s  WHERE id_vetement = %s and id_taille = %s'''
        mycursor.execute(sql, (taille_id, stock, id_article, taille["id_taille"]))
        get_db().commit()
        return redirect('/admin/article/edit?id_article=' + str(id_article))
    sql2 = '''INSERT INTO stock_vetement (id_vetement, id_taille, stock) VALUES (%s, %s, %s)'''
    mycursor.execute(sql2, (id_article, taille_id, stock))
    get_db().commit()
    return redirect('/admin/article/edit?id_article=' + id_article)


@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['GET'])
def edit_declinaison_article():
    id_declinaison_article = request.args.get('id_declinaison_article')
    mycursor = get_db().cursor()
    sql = '''SELECT
        v.id_vetement as article_id,
        nom_vetement as nom,
        prix_vetement as prix,
        v.id_type_vetement as type_article_id,
        image as image_article,
        libelle_type_vetement as libelle,
        SUM(sv.stock) as stock,
        sv.id_stock as id_declinaison_article,
        t.id_taille as taille_id
    FROM vetement v
    JOIN type_vetement tv ON v.id_type_vetement = tv.id_type_vetement
    LEFT JOIN stock_vetement sv ON v.id_vetement = sv.id_vetement
    LEFT JOIN taille t ON sv.id_taille = t.id_taille
    WHERE sv.id_stock = %s
    GROUP BY v.id_vetement, v.nom_vetement, v.prix_vetement, v.id_type_vetement, v.image, tv.libelle_type_vetement, sv.id_stock, t.id_taille;

    '''
    mycursor.execute(sql, (id_declinaison_article,))
    declinaison_article = mycursor.fetchone()

    sql2 = '''SELECT id_taille FROM stock_vetement WHERE id_vetement = %s AND id_taille != 1'''
    mycursor.execute(sql2, (declinaison_article["article_id"],))
    pas_unique = mycursor.fetchone()
    if pas_unique:
        sql3 = '''SELECT id_taille, libelle_taille as libelle FROM taille WHERE id_taille != 1'''
        mycursor.execute(sql3)
        tailles = mycursor.fetchall()
    else:
        sql3 = '''SELECT id_taille, libelle_taille as libelle FROM taille'''
        mycursor.execute(sql3)
        tailles = mycursor.fetchall()

    sql3 = '''SELECT id_taille FROM stock_vetement WHERE id_vetement = %s AND id_taille = 1'''
    mycursor.execute(sql3, (declinaison_article["article_id"],))
    taille_unique = mycursor.fetchone()

    if (taille_unique and taille_unique["id_taille"] == 1):
        d_taille_uniq = 1
    else:
        d_taille_uniq = None
    d_couleur_uniq = 1
    return render_template('admin/article/edit_declinaison_article.html'
                           , tailles=tailles
                           , declinaison_article=declinaison_article
                           , d_taille_uniq=d_taille_uniq
                           , d_couleur_uniq=d_couleur_uniq
                           )


@admin_declinaison_article.route('/admin/declinaison_article/edit', methods=['POST'])
def valid_edit_declinaison_article():
    id_declinaison_article = request.form.get('id_declinaison_article', '')
    id_article = request.form.get('id_article', '')
    stock = request.form.get('stock', '')
    taille_id = request.form.get('id_taille', '')
    couleur_id = request.form.get('id_couleur', '')
    mycursor = get_db().cursor()
    sql = '''SELECT id_taille FROM stock_vetement WHERE id_vetement = %s'''
    mycursor.execute(sql, id_article)
    taille = mycursor.fetchone()
    if (taille and taille_id) and (int(taille["id_taille"]) == int(taille_id)):
        flash(u'Information : doublon sur cette déclinaison, seul le stock a été mise à jour', 'alert-danger')
        sql = '''UPDATE stock_vetement SET id_taille = %s, stock = stock + %s  WHERE id_vetement = %s and id_taille = %s'''
        mycursor.execute(sql, (taille_id, stock, id_article, taille["id_taille"]))
        if int(taille["id_taille"]) != int(taille_id):
            sql2 = '''DELETE FROM stock_vetement WHERE id_stock = %s'''
            mycursor.execute(sql2, (id_declinaison_article,))
        get_db().commit()
        return redirect('/admin/article/edit?id_article=' + str(id_article))
    if taille and taille["id_taille"] == 1:
        sql = '''UPDATE stock_vetement SET id_vetement = %s, id_taille = %s, stock = %s WHERE id_stock = %s '''
        mycursor.execute(sql, (id_article, taille["id_taille"], stock, id_declinaison_article))
        get_db().commit()
    else:
        sql = '''UPDATE stock_vetement SET id_vetement = %s, id_taille = %s, stock = %s WHERE id_stock = %s '''
        mycursor.execute(sql, (id_article, taille_id, stock, id_declinaison_article))
        get_db().commit()
    message = u'declinaison_article modifié , id:' + str(id_declinaison_article) + '- stock :' + str(
        stock) + ' - taille_id:' + str(taille_id) + ' - couleur_id:' + str(couleur_id)
    flash(message, 'alert-success')
    return redirect('/admin/article/edit?id_article=' + str(id_article))


@admin_declinaison_article.route('/admin/declinaison_article/delete', methods=['GET'])
def admin_delete_declinaison_article():
    id_declinaison_article = request.args.get('id_declinaison_article', '')
    id_article = request.args.get('id_article', '')
    mycursor = get_db().cursor()
    sql = '''SELECT stock_id 
            FROM ligne_panier 
            WHERE stock_id = %s'''
    mycursor.execute(sql, id_declinaison_article)
    inc_panier = mycursor.fetchone()

    sql2 = '''SELECT stock_id 
            FROM ligne_commande 
            WHERE stock_id = %s'''
    mycursor.execute(sql2, id_declinaison_article)
    inc_commande = mycursor.fetchone()

    if inc_panier == None and inc_commande == None:
        sql2 = '''DELETE FROM stock_vetement WHERE id_stock = %s'''
        mycursor.execute(sql2, (id_declinaison_article,))
        get_db().commit()
        flash(u'declinaison supprimée, id_declinaison_article : ' + str(id_declinaison_article), 'alert-success')
        return redirect('/admin/article/edit?id_article=' + str(id_article))
    else:
        flash(u'Impossible de supprimer cette déclinaison, elle est présente dans une commande ou un panier',
              'alert-danger')
        return redirect('/admin/article/edit?id_article=' + str(id_article))