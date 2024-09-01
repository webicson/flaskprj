from flask_table import Table, Col

class Mange(Table):
    classes = ['table', 'table-bordered', 'table-hover',
               'table-striped']  # a list of strings to be set as the class attribute on the <table> element.
    table_id = 'searchable'  # - a string to set as the id attribute on the <table> element.
    thead_classes = ['bordered-darkorange']
    last_name = Col('Last Name')
    first_name = Col('First Name')
    email = Col('Email')
    number = Col('DID Number')
    time_start = Col('Start')
    time_end = Col('End')






