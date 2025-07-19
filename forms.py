from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    user_type = SelectField('User Type', choices=[('club', 'Student Club'), ('sponsor', 'Sponsor')], validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class ClubProfileForm(FlaskForm):
    club_name = StringField('Club Name', validators=[DataRequired(), Length(max=100)])
    university = StringField('University', validators=[DataRequired(), Length(max=100)])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description')
    contact_person = StringField('Contact Person', validators=[Length(max=100)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    submit = SubmitField('Save Profile')

class SponsorProfileForm(FlaskForm):
    company_name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    industry = SelectField('Industry', choices=[
        ('technology', 'Technology'),
        ('finance', 'Finance'),
        ('healthcare', 'Healthcare'),
        ('education', 'Education'),
        ('entertainment', 'Entertainment'),
        ('food_beverage', 'Food & Beverage'),
        ('automotive', 'Automotive'),
        ('retail', 'Retail'),
        ('sports', 'Sports'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Company Description')
    website = StringField('Website URL', validators=[Length(max=200)])
    budget_range = SelectField('Budget Range', choices=[
        ('under_1k', 'Under $1,000'),
        ('1k_5k', '$1,000 - $5,000'),
        ('5k_10k', '$5,000 - $10,000'),
        ('10k_25k', '$10,000 - $25,000'),
        ('25k_50k', '$25,000 - $50,000'),
        ('over_50k', 'Over $50,000')
    ])
    target_demographics = StringField('Target Demographics', validators=[Length(max=200)])
    contact_person = StringField('Contact Person', validators=[Length(max=100)])
    phone = StringField('Phone Number', validators=[Length(max=20)])
    submit = SubmitField('Save Profile')

class EventForm(FlaskForm):
    name = StringField('Event Name', validators=[DataRequired(), Length(max=200)])
    description = TextAreaField('Event Description')
    theme = StringField('Event Theme', validators=[Length(max=100)])
    event_date = DateField('Event Date', validators=[Optional()])
    location = StringField('Event Location', validators=[Length(max=200)])
    expected_footfall = IntegerField('Expected Footfall', validators=[Optional(), NumberRange(min=1)])
    target_audience = StringField('Target Audience', validators=[Length(max=200)])
    sponsor_requirements = TextAreaField('Sponsor Requirements')
    monetary_requirement = StringField('Monetary Requirements', validators=[Length(max=50)])
    material_requirement = TextAreaField('Material Requirements')
    marketing_requirement = TextAreaField('Marketing Requirements')
    past_engagement_stats = TextAreaField('Past Engagement Statistics')
    tags = StringField('Tags (comma-separated)', validators=[Length(max=500)])
    submit = SubmitField('Create Event')

class MessageForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')

class SearchForm(FlaskForm):
    keyword = StringField('Search Keywords')
    location = StringField('Location')
    theme = StringField('Theme')
    min_footfall = IntegerField('Minimum Expected Footfall', validators=[Optional(), NumberRange(min=1)])
    submit = SubmitField('Search Events')
