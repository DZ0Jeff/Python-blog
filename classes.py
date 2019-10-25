from wtforms import Form, StringField, TextAreaField, PasswordField, validators


#register form
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Password does not match')
    ])
    confirm = PasswordField('Confirm password')


# Article form
class ArticleForm(Form):
    title = StringField('Title', [validators.Length(min=1, max=50)])
    body = TextAreaField('Body', [validators.Length(min=10)])
    