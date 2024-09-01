from flask_table import Table, Col
from flask_babel import _
# Declare a table

class All_customers_in_db(Table):
    classes = ['table', 'table-bordered', 'table-hover', 'table-striped' ] # a list of strings to be set as the class attribute on the <table> element.
    table_id = 'searchable'  # - a string to set as the id attribute on the <table> element.
    thead_classes = ['bordered-darkorange']
    first_name = Col(_('Frist Name'))
    last_name = Col(_('Last Mame'))
    email = Col(_('Email'))




