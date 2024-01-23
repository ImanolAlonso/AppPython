from flask import Flask, render_template, flash, request, Response, jsonify, redirect, url_for, send_from_directory, send_file
from database import app, db, ProductoSchema, CategoriaSchema
from producto import Producto, Categoria
from sqlalchemy import create_engine
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
from datetime import datetime
import os, base64
from io import BytesIO
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, FileField, SelectField, SubmitField
from wtforms.validators import DataRequired, NumberRange,ValidationError

producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)
categoria_schema = CategoriaSchema()
categorias_schema = CategoriaSchema(many=True)

def validate_image_size(form, field):
    max_size = 64 * 1024  # 64KB
    if field.data:
        file_size = len(field.data.read())
        field.data.seek(0)  # Vuelve al inicio del archivo después de leer el tamaño.
        if file_size > max_size:
            raise ValidationError('La imagen no puede ser mayor a 64KB.')

#Validacion del formulario
class ProductoForm(FlaskForm):
    nombreProducto = StringField('Nombre', validators=[DataRequired()])
    stock = IntegerField('Stock', validators=[DataRequired(), NumberRange(min=0)])
    fecha = DateField('Fecha de lanzamiento', validators=[DataRequired(message='Seleccione una fecha')])
    imagen = FileField('Imagen',validators=[DataRequired(message='La imagen es obligatoria.'),validate_image_size])
    categoria = SelectField('Categoría', choices=[('1', 'Película'), ('2', 'Funko'), ('3', 'Comic')], validators=[DataRequired()])
    guardar = SubmitField('Guardar')

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/insertar', methods=['GET','POST'])
def add_producto_form():
    formulario = ProductoForm()
    if request.method == 'POST' and formulario.validate():
        # Procesar los datos del formulario
        nombreProducto = formulario.nombreProducto.data
        stock = formulario.stock.data
        fecha = formulario.fecha.data
        imagen = request.files['imagen']  # Acceder al archivo de imagen
        categoria = formulario.categoria.data
        imagen_binario = BytesIO(imagen.read()).read()
        
        nuevo_producto = Producto(nombreProducto, stock, fecha, imagen.filename, imagen_binario, categoria)
        db.session.add(nuevo_producto)
        db.session.commit()
        
        basepath = os.path.dirname (__file__) #ruta donde esta el archivo actual
        imagen.save(os.path.join(basepath, 'static', 'imgs', imagen.filename))

        flash('Formulario procesado exitosamente')
        return listar_producto()
    return render_template('insertar.html',form = formulario)

@app.route('/listado')
def listar_producto():
    productos = Producto.query.all()
    #Se pasa el resultado de la consulta y el base64 para poder mostrar las imagenes en el fichero de listado.html 
    return render_template('listado.html', productos = productos, base64 = base64)

@app.route('/detalle/<id>', methods=['GET'])
def detalle_producto(id):
    producto = obtener_producto(id)
    #Se pasa el resultado de la consulta y el base64 para poder mostrar las imagenes en el fichero de detalle.html 
    return render_template('detalle.html', producto = producto, base64 = base64)

def obtener_producto(id):
    producto = Producto.query.get(id)
    return producto

@app.route('/delete/<id>')
def delete_producto(id):
    producto = Producto.query.get(id)
    db.session.delete(producto)
    db.session.commit()
    flash('Producto eliminado correctamente')
    return redirect(url_for('listar_producto'))

@app.route('/edit/<id>')
def edit_producto(id):
    producto = Producto.query.get(id)
    #Mostrar los datos que ya tiene el producto
    return render_template('modificar.html',producto = producto, base64 = base64)

@app.route('/edit/<id>', methods=['POST'])
def edit_producto_form(id):    
    nombreProducto = request.form['nombreProducto']
    stock = int(request.form['stock'])
    fecha = request.form['fecha']
    categoria = request.form['categoria']
    imagen = request.files['imagen']
    
    if nombreProducto and stock and fecha and categoria:
        producto = Producto.query.get(id)

        producto.nombreProducto = nombreProducto
        producto.stock = stock
        producto.fecha = datetime.strptime(fecha, '%Y-%m-%d')
        producto.idCategoria = int(categoria)
        
        #Modificacion de la imagen si recibe una nueva
        if 'imagen' in request.files and request.files['imagen'].filename != '':
            imagen = request.files['imagen']
            producto.nombreImagen = imagen.filename
            producto.imagen = BytesIO(imagen.read()).read()
        
        db.session.commit()
        flash('Producto modificado correctamente')
        return listar_producto()
    else:
        return notFound()
    
@app.route('/imagen/<nombre>')
def imagen_producto(nombre):
    producto = Producto.query.filter_by(nombreImagen=nombre).first()
    return send_file(BytesIO(producto.imagen), mimetype='image/jpeg')

@app.errorhandler(404)
def notFound(error=None):
    message ={
        'message': 'No encontrado ' + request.url,
        'status': '404 Not Found'
    }
    response = jsonify(message)
    response.status_code = 404
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5000)