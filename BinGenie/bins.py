from flask import Blueprint, render_template,flash,redirect,url_for,request, current_app
from .database import Bin, db, Item, Location
from .forms import BinForm, EditBinForm, BinItemForm
import os

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
    bin = Bin.query.get_or_404(id)
    form = EditBinForm(obj=bin) if request.method == 'GET' else EditBinForm()
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

@bins_bp.route('/bins/<uuid:bin_id>/items/new', methods=['GET', 'POST'])
def create_item_in_bin(bin_id):
    bin = Bin.query.get_or_404(bin_id)
    form = BinItemForm()
    form.bin_id.data = str(bin_id)  # Pre-populate bin_id

    if form.validate_on_submit():
        new_item = Item(
            name=form.name.data,
            quantity=form.quantity.data,
            description=form.description.data,
            bin_id=bin_id,
            # Assume handling of image field remains the same
        )
        db.session.add(new_item)
        db.session.commit()
        flash('Item created successfully!', 'success')
        return redirect(url_for('bins_bp.get_bin', id=bin_id))

    # Pass the bin object to pre-populate the bin field in the template
    return render_template('bins/create_item_in_bin.html', form=form, bin=bin)


@bins_bp.route('/bins/<uuid:bin_id>/items/<uuid:item_id>/delete', methods=['POST'])
def delete_item_from_bin(bin_id, item_id):
    bin = Bin.query.get_or_404(str(bin_id))
    item = Item.query.get_or_404(str(item_id))

    # Attempt to delete the item from the database
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully.', 'success')

    # After successfully deleting the item, try to delete its image file
    image_path = item.image_path
    if image_path:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
        try:
            os.remove(full_path)
            flash('Associated image deleted successfully.', 'success')
        except OSError as e:
            # The file might not exist or could not be deleted; handle the error
            flash(f'Failed to delete the associated image. Error: {e}', 'error')

    # Redirect back to the bin details page
    return redirect(url_for('bins_bp.get_bin', id=bin_id))