from flask_table import Table, Col

# Declare a table
class SmsTable(Table):
    classes = ['table','table-bordered','table-hover','table-striped'] # a list of strings to be set as the class attribute on the <table> element.
    table_id = 'searchable' # - a string to set as the id attribute on the <table> element.
    thead_classes = ['bordered-darkorange']
    to = Col('Nexmo Virtual Number')
    msisdn = Col('Sent From')
    messageTimestamp = Col('Date')
    text = Col('Text')

class NexmoNumbersTable(Table):
    classes = ['table', 'table-bordered', 'table-hover',
               'table-striped']  # a list of strings to be set as the class attribute on the <table> element.
    table_id = 'searchable'  # - a string to set as the id attribute on the <table> element.
    thead_classes = ['bordered-darkorange']
    country = Col('country')
    msisdn = Col('Number')
    type = Col('Type')
    # if features[0] == 'VOICE':
    features = Col('Features')

class SingleDidDetails(Table):
    classes = ['table', 'table-bordered', 'table-hover', 'table-striped' ] # a list of strings to be set as the class attribute on the <table> element.
    table_id = 'searchable'  # - a string to set as the id attribute on the <table> element.
    thead_classes = ['bordered-darkorange']
    msisdn = Col('Number')
    account_username = Col('Account username')
    account_password = Col('Account Password')
    phone_number = Col('phone_number')

class MangeSms(Table):
    classes = ['table', 'table-bordered', 'table-hover',
               'table-striped']  # a list of strings to be set as the class attribute on the <table> element.
    table_id = 'searchable'  # - a string to set as the id attribute on the <table> element.
    thead_classes = ['bordered-darkorange']
    last_name = Col('Last Name')
    msisdn = Col('Number')
    account_username = Col('Account username')
    account_password = Col('Account Password')
    phone_number = Col('phone_number')





