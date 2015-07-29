# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

Base = declarative_base()

class User(Base):
    """A Twitter user"""
    __tablename__ = 'user'

    uid = Column(Integer, primary_key=True)
    account = Column(String, unique=True, nullable=False)
    description = Column(String)
    official = Column(Boolean)
    following = relationship("Following", backref="user",
                             order_by="Following.follows")
    followers = relationship("Followers", backref="user",
                             order_by="Followers.follower")

class Following(Base):
    """Following table"""
    __tablename__ = 'following'

    user = Column(ForeignKey('user.uid', ondelete='CASCADE'))
    follows = Column(ForeignKey('user.uid', ondelete='CASCADE'))

class Followers(Base):
    """Followers table """
    __tablename__ = 'followers'

    user = Column(ForeignKey('user.uid', ondelete='CASCADE'))
    follower = Column(ForeignKey('user.uid', ondelete='CASCADE'))
