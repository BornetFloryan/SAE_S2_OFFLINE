#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import Blueprint
from flask import Flask, request, render_template, redirect, abort, flash, session

from connexion_db import get_db

admin_dataviz = Blueprint('admin_dataviz', __name__,
                        template_folder='templates')

@admin_dataviz.route('/admin/dataviz/etat1')
def show_type_article_stock():
    mycursor = get_db().cursor()
    sql = '''SELECT tv.id_type_vetement as id_type_article,
                tv.libelle_type_vetement as libelle,
                COUNT(v.id_type_vetement) as nbr_articles,
                SUM(stock) as nbr_articles_stock
            FROM type_vetement tv
            LEFT JOIN vetement v ON tv.id_type_vetement = v.id_type_vetement
            LEFT JOIN stock_vetement sv ON v.id_vetement = sv.id_vetement
            GROUP BY tv.id_type_vetement, libelle_type_vetement
            '''

    mycursor.execute(sql)
    datas_show = mycursor.fetchall()
    labels = [str(row['libelle']) for row in datas_show]
    values = [int(row['nbr_articles']) for row in datas_show]

    # sql = '''
    #         
    #        '''
    # datas_show=[]
    # labels=[]
    # values=[]

    return render_template('admin/dataviz/dataviz_etat_1.html'
                           , types_articles_nb=datas_show
                           , labels=labels
                           , values=values)


# sujet 3 : adresses


@admin_dataviz.route('/admin/dataviz/etat2')
def show_dataviz_map():
    # mycursor = get_db().cursor()
    # sql = '''    '''
    # mycursor.execute(sql)
    # adresses = mycursor.fetchall()

    #exemples de tableau "résultat" de la requête
    adresses =  [{'dep': '25', 'nombre': 1}, {'dep': '83', 'nombre': 1}, {'dep': '90', 'nombre': 3}]

    # recherche de la valeur maxi "nombre" dans les départements
    # maxAddress = 0
    # for element in adresses:
    #     if element['nbr_dept'] > maxAddress:
    #         maxAddress = element['nbr_dept']
    # calcul d'un coefficient de 0 à 1 pour chaque département
    # if maxAddress != 0:
    #     for element in adresses:
    #         indice = element['nbr_dept'] / maxAddress
    #         element['indice'] = round(indice,2)

    print(adresses)

    return render_template('admin/dataviz/dataviz_etat_map.html'
                           , adresses=adresses
                          )


