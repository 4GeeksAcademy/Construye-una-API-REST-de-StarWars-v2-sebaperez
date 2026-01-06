from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False) 
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)    
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    favorite_character: Mapped [list["FavoriteCharacter"]] = relationship(back_populates="user")
    favorite_planet: Mapped[list["FavoritePlanet"]] = relationship(back_populates="user")
   
   
    def __repr__(self):
       return f'Usuario {self.email}'    

    def serialize(self):
        return {
            "id": self.id,
            "name" : self.name,
            "email": self.email,
            'is_active': self.is_active
            # do not serialize the password, its a security breach
        }


class Character (db.Model):
    __tablename__= 'character'
    id: Mapped [int] = mapped_column (primary_key=True)
    name:Mapped [str] = mapped_column (String(50), nullable=False)
    height: Mapped [int] = mapped_column (Integer)
    weight: Mapped [int] = mapped_column (Integer)
    favorite_by: Mapped [list["FavoriteCharacter"]] = relationship (back_populates="character")

    def __repr__(self):
        return f'Personaje {self.name}'

    def serialize (self):
        return { 
            'id' : self.id,
            'name' : self.name,
            'height' : self.height,
            'weight' : self.weight

        }


class FavoriteCharacter (db.Model):

    __tablename__= 'favorite_character'
    id: Mapped [int] = mapped_column (primary_key=True)
    user_id: Mapped [int] = mapped_column (ForeignKey('user.id'), nullable=False) 
    user: Mapped['User'] = relationship (back_populates = 'favorite_character')
    character_id: Mapped [int] = mapped_column (ForeignKey ('character.id'), nullable= False)
    character: Mapped ['Character'] = relationship (back_populates= 'favorite_by')

    def __repr__ (self):
        return f'A {self.user} le gusta {self.character}'


class Planet (db.Model):
    __tablename__= 'planet'
    id: Mapped [int] = mapped_column (primary_key=True)
    name:Mapped [str] = mapped_column (String(50), nullable=False)
    density: Mapped [int] = mapped_column (Integer)
    favorite_by: Mapped [list["FavoritePlanet"]] = relationship (back_populates="planet")

    def __repr__(self):
        return f'Planet {self.name}'

    def serialize (self):
        return { 
            'id' : self.id,
            'name' : self.name,
            'density' : self.density,
        }


class FavoritePlanet (db.Model):

    __tablename__= 'favorite_planet'
    id: Mapped [int] = mapped_column (primary_key=True)
    user_id: Mapped [int] = mapped_column (ForeignKey('user.id'), nullable=False) 
    user: Mapped['User'] = relationship (back_populates = 'favorite_planet')
    planet_id: Mapped [int] = mapped_column (ForeignKey ('planet.id'), nullable= False)
    planet: Mapped ['Planet'] = relationship (back_populates= 'favorite_by')

    def __repr__ (self):
        return f'A {self.user} le gusta {self.planet}'