from flask_table import Table, Col

# Declare a table

class All_available_dids(Table):
    classes = ['table', 'table-bordered', 'table-hover', 'table-striped' ] # a list of strings to be set as the class attribute on the <table> element.
    table_id = 'searchable'  # - a string to set as the id attribute on the <table> element.
    thead_classes = ['bordered-darkorange']
    number = Col('Did Nunmber')
    vendor_id = Col('Vendor')
    timestamp = Col('Add Date')
    country_id = Col('Country')



