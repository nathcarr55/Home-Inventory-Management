from flask_wtf import FlaskForm
from .database import Location, Bin
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SubmitField, SelectField,TextAreaField, IntegerField,HiddenField
from wtforms.validators import DataRequired, Length, Optional


class LocationForm(FlaskForm):
    name = StringField('Location Name', validators=[DataRequired()])
    description = TextAreaField('Description')
    submit = SubmitField('Create Location')

class EditLocationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[Length(max=255)])
    submit = SubmitField('Update Location')

class BinForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    capacity = StringField('Capacity')
    location_id = SelectField('Location', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Create Bin')


    def __init__(self, *args, **kwargs):
        super(BinForm, self).__init__(*args, **kwargs)
        self.location_id.choices = [(str(location.id), location.name) for location in Location.query.all()]

class EditBinForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    capacity = StringField('Capacity')
    location_id = SelectField('Location', coerce=str, validators=[DataRequired()])
    submit = SubmitField('Update Bin')

    def __init__(self, *args, **kwargs):
        super(EditBinForm, self).__init__(*args, **kwargs)
        self.location_id.choices = [(str(location.id), location.name) for location in Location.query.all()]

class BinItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    quantity = IntegerField('Quantity', validators=[DataRequired()], default=0)
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    image = FileField('Item Image', validators=[FileAllowed(['jpg', 'png', '.jpeg', 'jpeg'], 'Images only!')],
                      description="Optional")
    bin_id = HiddenField()
    submit = SubmitField('Create Item')

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    quantity = IntegerField('Quantity', validators=[DataRequired()], default=0)
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    bin_id = SelectField('Bin', coerce=str, validators=[DataRequired()])
    image = FileField('Item Image', validators=[FileAllowed(['jpg', 'png','.jpeg','jpeg'], 'Images only!')], description="Optional")
    submit = SubmitField('Create Item')

    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.bin_id.choices = [(str(bin.id), bin.name) for bin in Bin.query.all()]

class EditItemForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    quantity = IntegerField('Quantity', validators=[DataRequired()])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    bin_id = SelectField('Bin', coerce=str, validators=[DataRequired()])
    image = FileField('Item Image', validators=[Optional(), FileAllowed(['jpg', 'png','.jpeg','jpeg'], 'Images only!')], description="Optional")
    submit = SubmitField('Update Item')

    def __init__(self, *args, **kwargs):
        super(EditItemForm, self).__init__(*args, **kwargs)
        self.bin_id.choices = [(str(bin.id), bin.name) for bin in Bin.query.all()]