from wtforms import Form, StringField, PasswordField, validators


class Form(Form):
    name = StringField('Name', [validators.length(min=1, max=50)])
    username = StringField('Username', [validators.length(min=4, max=25)])
    email = StringField('Email', [validators.length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.data_required(),
        validators.equal_to('confirm', message='Password Do Not Match')
    ])
    confirm = PasswordField('Confirm Password')
