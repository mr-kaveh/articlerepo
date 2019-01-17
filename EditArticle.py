from wtforms import Form, StringField, TextAreaField, PasswordField, validators


class ArticleForm(Form):
        title = StringField('Title', [validators.length(min=1, max=50)])
        body = TextAreaField('Body', [validators.length(min=30)])
