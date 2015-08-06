# -*- coding: utf-8 -*-

import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, Table, \
     ForeignKey, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from contextlib import contextmanager


Base = declarative_base()
following = Table('following', Base.metadata,
                  Column('user', Integer,
                         ForeignKey('user.uid', ondelete='CASCADE'),
                         primary_key=True),
                  Column('follows', Integer,
                         ForeignKey('user.uid', ondelete='CASCADE'),
                         primary_key=True))
followers = Table('followers', Base.metadata,
                  Column('user', Integer,
                         ForeignKey('user.uid', ondelete='CASCADE'),
                         primary_key=True),
                  Column('follower', Integer,
                         ForeignKey('user.uid', ondelete='CASCADE'),
                         primary_key=True))


class User(Base):
    """A Twitter user"""
    __tablename__ = 'user'

    uid = Column(Integer, primary_key=True)
    account = Column(String, unique=True, nullable=False)
    name = Column(String)
    description = Column(String)
    verified = Column(Boolean)
    protected = Column(Boolean)
    suspended = Column(Boolean)
    location = Column(String)
    time_zone = Column(String)
    id = Column(Integer, unique=True)
    statuses_count = Column(Integer)
    favourites_count = Column(Integer)
    friends_count = Column(Integer)
    followers_count = Column(Integer)
    following = relationship("User", secondary=following,
                             primaryjoin=uid==following.c.user,
                             secondaryjoin=uid==following.c.follows)
    followers = relationship("User", secondary=followers,
                             primaryjoin=uid==followers.c.user,
                             secondaryjoin=uid==followers.c.follower)

    def follow(self, user):
        """Follows a user"""
        if user not in self.following:
            self.following.append(user)
            user.followers.append(self)

    def unfollow(self, user):
        """Unfollows a user"""
        if user in self.following:
            self.following.remove(user)
            user.followers.remove(self)

    def __repr__(self):
        return ("<User(uid='%d', account='%s', description='%s'," + \
                " official='%s')>") % (self.uid, self.account, self.description,
                                       self.official)


class Database(object):

    def __init__(self, name):
        db_path = os.path.join(os.getcwd(), 'twinosy-data')
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        db_path = os.path.join(db_path, name)
        self.engine = create_engine('sqlite:///{0}'.format(db_path))
        self.engine.echo = False
        Base.metadata.create_all(self.engine)
        Base.metadata.bind = self.engine
        self.Session = sessionmaker()

    def account_exists(self, account):
        vl = None
        with session_scope(self) as session:
            vl = session.query(User).filter(
                User.account == account).first() is not None
        return vl

    def create_cache(self):
        cache = {}
        with session_scope(self) as session:
            users = session.query(User).all()
            for user in users:
                cache[user.account] = user
        return cache

    def save_cache(self, cache):
        with session_scope(self) as session:
            for key in cache.keys():
                 u = session.query(User).filter(User.account == key).first()
                 if u is None:
                     u = User(account=key, id=cache[key].id,
                              name=cache[key].name,
                              description=cache[key].description,
                              verified=cache[key].verified,
                              protected=cache[key].protected,
                              suspended=cache[key].suspended,
                              location=cache[key].location,
                              time_zone=cache[key].time_zone,
                              statuses_count=cache[key].statuses_count,
                              favourites_count=cache[key].favourites_count,
                              friends_count=cache[key].friends_count,
                              followers_count=cache[key].followers_count)
                 else:
                    u.name = cache[key].name
                    u.description = cache[key].description
                    u.verified = cache[key].verified
                    u.protected = cache[key].protected
                    u.suspended = cache[key].suspended
                    u.location = cache[key].location
                    u.time_zone = cache[key].time_zone
                    u.id = cache[key].id
                    u.statuses_count = cache[key].statuses_count
                    u.favourites_count = cache[key].favourites_count
                    u.friends_count = cache[key].friends_count
                    u.followers_count = cache[key].followers_count


@contextmanager
def session_scope(db):
    session = db.Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == '__main__':
    print " ~ Starting tests ~ \n"
    """
    d = Database('quicktest.db')
    tuser2 = User(account='another', description='AND', official=False)
    tuser = User(account='7flying', description='SUPER', official=False)
    with session_scope(d) as session:
        tuser2.follow(tuser)
        session.add_all([tuser, tuser2])
        #session.commit()
    """
    d = Database('quicktest.db')
    with session_scope(d) as session:
        perso = session.query(User).first()
        print perso
        custm = session.query(User).filter(User.account == '7flyin').first()
        print custm
        print d.account_exists('another')
