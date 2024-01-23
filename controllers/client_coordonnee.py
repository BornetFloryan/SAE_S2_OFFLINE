#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, url_for, abort, flash, session, g

from connexion_db import get_db

client_coordonnee = Blueprint('client_coordonnee', __name__,
                        template_folder='templates')


@client_coordonnee.route('/client/coordonnee/show')
def client_coordonnee_show():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT login as login, email as email, nom as nom FROM utilisateur WHERE id_utilisateur = %s'''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    mycursor2 = get_db().cursor()
    sql = '''SELECT id_adresse, nom_adresse as nom, rue, code_postal, ville 
    FROM adresse
    JOIN utilisateur ON adresse.id_utilisateur = utilisateur.id_utilisateur
    WHERE utilisateur.id_utilisateur = %s
    '''
    mycursor2.execute(sql, id_client)
    adresses = mycursor2.fetchall()

    return render_template('client/coordonnee/show_coordonnee.html'
                           , utilisateur=utilisateur
                           , adresses=adresses
                         #  , nb_adresses=nb_adresses
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['GET'])
def client_coordonnee_edit():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT login as login, email as email, nom as nom FROM utilisateur WHERE id_utilisateur = %s'''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()
    return render_template('client/coordonnee/edit_coordonnee.html'
                           ,utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/edit', methods=['POST'])
def client_coordonnee_edit_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom=request.form.get('nom')
    login = request.form.get('login')
    email = request.form.get('email')

    utilisateur = None
    if utilisateur:
        flash(u'votre cet Email ou ce Login existe déjà pour un autre utilisateur', 'alert-warning')
        return render_template('client/coordonnee/edit_coordonnee.html'
                               #, user=user
                               )
    sql = '''UPDATE utilisateur SET nom = %s, login = %s, email = %s WHERE id_utilisateur = %s'''
    mycursor.execute(sql, (nom, login, email, id_client))
    get_db().commit()
    return redirect('/client/coordonnee/show')


@client_coordonnee.route('/client/coordonnee/delete_adresse',methods=['POST'])
def client_coordonnee_delete_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse= request.form.get('id_adresse')

    sql = '''DELETE FROM adresse WHERE id_adresse = %s'''
    mycursor.execute(sql, id_adresse)
    get_db().commit()

    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/add_adresse')
def client_coordonnee_add_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    sql = '''SELECT login as login, nom as nom FROM utilisateur WHERE id_utilisateur = %s'''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()
    return render_template('client/coordonnee/add_adresse.html'
                           ,utilisateur=utilisateur
                           )

@client_coordonnee.route('/client/coordonnee/add_adresse',methods=['POST'])
def client_coordonnee_add_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    sql = '''INSERT INTO adresse (nom_adresse, rue, code_postal, ville, id_utilisateur) 
    VALUES (%s, %s, %s, %s, %s)'''
    mycursor.execute(sql, (nom, rue, code_postal, ville, id_client))
    get_db().commit()
    return redirect('/client/coordonnee/show')

@client_coordonnee.route('/client/coordonnee/edit_adresse')
def client_coordonnee_edit_adresse():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    id_adresse = request.args.get('id_adresse')
    sql = '''SELECT login as login, nom as nom FROM utilisateur WHERE id_utilisateur = %s'''
    mycursor.execute(sql, id_client)
    utilisateur = mycursor.fetchone()

    mycursor2 = get_db().cursor()
    sql = '''SELECT id_adresse, nom_adresse as nom, rue, code_postal, ville
    FROM adresse
    WHERE adresse.id_adresse = %s
    '''
    print(id_adresse)
    mycursor2.execute(sql, id_adresse)
    adresse = mycursor2.fetchone()

    return render_template('/client/coordonnee/edit_adresse.html'
                            ,utilisateur=utilisateur
                            ,adresse=adresse
                           )

@client_coordonnee.route('/client/coordonnee/edit_adresse',methods=['POST'])
def client_coordonnee_edit_adresse_valide():
    mycursor = get_db().cursor()
    id_client = session['id_user']
    nom= request.form.get('nom')
    rue = request.form.get('rue')
    code_postal = request.form.get('code_postal')
    ville = request.form.get('ville')
    id_adresse = request.form.get('id_adresse')

    sql = '''UPDATE adresse SET nom_adresse = %s, rue = %s, code_postal = %s, ville = %s WHERE id_adresse = %s'''
    mycursor.execute(sql, (nom, rue, code_postal, ville, id_adresse))
    get_db().commit()

    return redirect('/client/coordonnee/show')
