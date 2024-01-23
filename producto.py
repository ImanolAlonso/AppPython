from database import db
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class Categoria(db.Model):
    __tablename__ = 'Categoria'

    idCategoria = db.Column(db.Integer, primary_key=True)
    nombreCategoria = db.Column(db.String(255), nullable=False)

    def __init__(self, nombreCategoria):
        self.nombreCategoria = nombreCategoria

    def __repr__(self):
        return f'<Categoria {self.idCategoria}>: {self.nombreCategoria}'
    
class Producto(db.Model):
    __tablename__ = 'Producto'
    id = db.Column(db.Integer, primary_key=True)
    nombreProducto = db.Column(db.String(100), nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    fecha = db.Column(db.DateTime)
    nombreImagen = db.Column(db.String(255))
    imagen = db.Column(db.BLOB)
    idCategoria = db.Column(db.Integer, db.ForeignKey('Categoria.idCategoria'))
    categoria = db.relationship('Categoria', backref='productos')
    
    def __init__(self, nombreProducto, stock, fecha, nombreImagen, imagen, idCategoria):
        self.nombreProducto = nombreProducto
        self.stock = stock
        self.fecha = fecha
        self.nombreImagen = nombreImagen
        self.imagen = imagen
        self.idCategoria = idCategoria

    def __repr__(self):
        return f'<Producto {self.id}>: {self.nombreProducto}, {self.idCategoria}'
    


