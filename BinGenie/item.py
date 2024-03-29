from flask import Blueprint, render_template, url_for, flash, jsonify,redirect, make_response,current_app,request, abort, send_from_directory
from .database import Item, Location,Bin, db
from .forms import ItemForm, EditItemForm
import os

from werkzeug.utils import secure_filename
# Create a Blueprint for items
items_bp = Blueprint('items_bp', __name__, template_folder='templates/items')

@items_bp.route('/items')
def list_items():
    items = Item.query.all()
    return render_template('items/list_items.html', items=items)

@items_bp.route('/items/<uuid:id>')
def get_item(id):
    item = Item.query.get_or_404(id)
    # storing relative paths in `image_path` and using a static folder for uploads
    image_url = url_for('static', filename=f'uploads/{item.image_path}') if item.image_path else None
    return render_template('items/item_detail.html', item=item, image_url=image_url)

@items_bp.route('/items/new', methods=['GET', 'POST'])
def new_item():
    form = ItemForm()
    if form.validate_on_submit():
        new_item = Item(
            name=form.name.data,
            quantity=form.quantity.data,
            description=form.description.data,
            bin_id=form.bin_id.data
        )
        db.session.add(new_item)
        db.session.flush()  # This will generate the ID but not commit the transaction
        item_id = new_item.id

        file = form.image.data
        if file:
            file_extension = os.path.splitext(file.filename)
            filename = secure_filename(f"{item_id}{file_extension}")
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            print(file_path)
            file.save(file_path)
            new_item.image_path = file_path

        db.session.commit()
        flash('Item created successfully!', 'success')
        return redirect(url_for('items_bp.list_items'))
    return render_template('items/new_item_form.html', form=form)


@items_bp.route('/items/edit/<uuid:id>', methods=['GET', 'POST'])
def edit_item(id):
    item = Item.query.get_or_404(str(id))
    form = EditItemForm(obj=item)
    if form.validate_on_submit():
        item.name = form.name.data
        item.quantity = form.quantity.data
        item.description = form.description.data
        item.bin_id = form.bin_id.data

        # Handle the image upload if a new file has been provided
        file = form.image.data
        if file and file.filename != '':
            # If there's a new file, you might want to delete the old image file
            # Example: os.remove(os.path.join(app.config['UPLOAD_FOLDER'], item.image_path))

            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            item.image_path = file_path  # Update the image path to the new file

        db.session.commit()
        flash('Item updated successfully!', 'success')
        return redirect(url_for('items_bp.list_items'))
    return render_template('items/edit_item_form.html', form=form, item=item)

@items_bp.route('/items/<uuid:id>/delete', methods=['POST'])
def delete_item(id):
    item = Item.query.get_or_404(str(id))
    image_path = item.image_path

    # Attempt to delete the item from the database
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully.', 'success')

    # After successfully deleting the item, try to delete its image file
    if image_path:
        full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
        try:
            os.remove(full_path)
            flash('Associated image deleted successfully.', 'success')
        except OSError as e:
            # The file might not exist or could not be deleted; handle the error
            print(f"Error deleting the image file: {e}")
            flash('Failed to delete the associated image.', 'error')

    return redirect(url_for('items_bp.list_items'))


@items_bp.route('/item-image/<uuid:item_id>')
def serve_item_image(item_id):
    directory = os.environ.get("UPLOAD_FOLDER")
    item = Item.query.get_or_404(item_id)
    image_path = item.image_path
    # If no image path, abort with a 404 response
    if not image_path:
        image_path = os.path.join(directory,"default.jpeg")
    file_path = os.path.join(image_path)
    # Extract the filename from the image path
    filename = os.path.basename(image_path)
    if not os.path.isfile(file_path):
        abort(404)
    return send_from_directory(directory, filename)

@items_bp.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return make_response("No Search Query provided", 400)

    search = f"%{query}%"
    items = Item.query.filter(Item.name.ilike(search)).all()
    results = []
    for item in items:
        bin_obj = Bin.query.get(item.bin_id)
        location_obj = Location.query.get(bin_obj.location_id) if bin_obj else None
        item_dict = {
            'item_name': item.name,
            'item_id': item.id,
            'bin_id': bin_obj.id if bin_obj else None,
            'bin_name': bin_obj.name if bin_obj else "No Bin",
            'location_id': location_obj.id if location_obj else None,
            'location_name': location_obj.name if location_obj else "No Location",
        }
        results.append(item_dict)
    return jsonify(results)

