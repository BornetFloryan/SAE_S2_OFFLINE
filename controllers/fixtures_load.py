#! /usr/bin/python
# -*- coding:utf-8 -*-
from flask import *
import datetime
from decimal import *
from connexion_db import get_db

fixtures_load = Blueprint('fixtures_load', __name__, template_folder='templates')


@fixtures_load.route('/base/init')
def fct_fixtures_load():
     cursor = get_db().cursor()
     
     with open('sae_sql.sql', 'r') as f:
          sql = f.read()
          sqlCommands = sql.replace('\n', '').split(';')
          for command in sqlCommands:
               try:
                    if command.strip() != '':
                         cursor.execute(command)
                         get_db().commit()
               except IOError:
                    print(f"Command skipped: {command}")


     return redirect('/')
