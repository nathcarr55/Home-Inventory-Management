from flask import Blueprint, render_template, redirect,url_for,request, flash
from .database import Location, db, Bin
from .forms import LocationForm


locations_bp = Blueprint('locations_bp', __name__, template_folder='templates/locations')

@locations_bp.route('/locations')
def list_locations():
    locations = Location.query.all()
    return render_template('locations/list_locations.html', locations=locations)

@locations_bp.route('/locations/<id>')
def get_location(id):
    location = Location.query.get_or_404(id)
    bins = Bin.query.filter_by(location_id=id)
    return render_template('locations/location_details.html', location=location, bins=bins)


@locations_bp.route('/locations/new', methods=['GET', 'POST'])
def new_location():
    form = LocationForm()
    if form.validate_on_submit():
        new_location = Location(name=form.name.data, description=form.description.data)
        db.session.add(new_location)
        db.session.commit()
        flash('New location added successfully!', 'success')
        return redirect(url_for('locations_bp.list_locations'))
    return render_template('locations/new_location_form.html', form=form)

@locations_bp.route('/locations/<id>/edit', methods=['GET', 'POST'])
def edit_location(id):
    location = Location.query.get_or_404(id)
    if request.method == 'POST':
        location.name = request.form['name']
        db.session.commit()
        return redirect(url_for('locations_bp.list_locations'))
    return render_template('locations/edit_location.html', location=location)

@locations_bp.route('/locations/<id>/delete', methods=['POST'])
def delete_location(id):
    location = Location.query.get_or_404(f"{id}")
    db.session.delete(location)
    db.session.commit()
    return redirect(url_for('locations_bp.list_locations'))