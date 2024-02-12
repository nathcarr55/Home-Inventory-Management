from flask import Blueprint, render_template,flash,redirect,url_for
from .database import Bin, db, Item, Location
from .forms import BinForm, EditBinForm

# Create a Blueprint for bins
bins_bp = Blueprint('bins_bp', __name__, template_folder='templates/bins')

@bins_bp.route('/bins')
def list_bins():
    bins = Bin.query.all()
    return render_template('bins/list_bins.html', bins=bins)

@bins_bp.route('/bins/<uuid:id>')
def get_bin(id):
    bin = Bin.query.get_or_404(id)
    items = Item.query.filter_by(bin_id=id).all()
    location = Location.query.filter_by(id=bin.location_id).first()
    return render_template('bins/bin_detail.html', bin=bin, items=items, location=location)

@bins_bp.route('/bins/new', methods=['GET', 'POST'])
def new_bin():
    form = BinForm()
    if form.validate_on_submit():
        new_bin = Bin(
            name=form.name.data,
            capacity=form.capacity.data,
            location_id=form.location_id.data
        )
        db.session.add(new_bin)
        db.session.commit()
        flash('Bin created successfully!', 'success')
        return redirect(url_for('bins_bp.list_bins'))
    return render_template('bins/new_bin_form.html', form=form)

@bins_bp.route('/bins/edit/<uuid:id>', methods=['GET', 'POST'])
def edit_bin(id):
    bin = Bin.query.get_or_404(str(id))
    form = EditBinForm(obj=bin)
    if form.validate_on_submit():
        bin.name = form.name.data
        bin.capacity = form.capacity.data
        bin.location_id = form.location_id.data
        db.session.commit()
        flash('Bin updated successfully!', 'success')
        return redirect(url_for('bins_bp.list_bins'))
    return render_template('bins/edit_bin_form.html', form=form, bin=bin)

@bins_bp.route('/bins/<uuid:id>/delete', methods=['POST'])
def delete_bin(id):
    bin = Bin.query.get_or_404(str(id))
    db.session.delete(bin)
    db.session.commit()
    flash('Bin deleted successfully.')
    return redirect(url_for('bins_bp.list_bins'))