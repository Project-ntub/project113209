from django.contrib import admin
import pymysql
pymysql.install_as_MySQLdb()
from .models import userpreferences

admin.site.register(userpreferences)
