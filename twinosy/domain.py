# -*- coding: utf-8 -*-

import os

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, Table, \
     ForeignKey, create_engine
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.sql import select
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
    description = Column(String)
    official = Column(Boolean)
    protected = Column(Boolean)
    time_zone = Column(String)
    twi_id = Column(Integer, unique=True)
    following = relationship("User", secondary=following,
                             primaryjoin=uid==following.c.user,
                             secondaryjoin=uid==following.c.follows)
    followers = relationship("User", secondary=followers,
                             primaryjoin=uid==followers.c.user,
                             secondaryjoin=uid==followers.c.follower)

    def follow(self, user):
        """Follows a user"""
        # TODO queck that the user exists
        # User.check_user(user)
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
                " official='%s')>") % (self.uid, self.account, self.description, self.official)

class Database(object):

    def __init__(self, name):
        db_path = os.path.join(os.getcwd(), 'twinosy-data')
        if not os.path.exists(db_path):
            os.makedirs(db_path)
        db_path = os.path.join(db_path, name)
        self.engine = create_engine('sqlite:///{0}'.format(db_path))
        self.engine.echo = False
        Base.metadata.create_all(self.engine)

        self.Session = sessionmaker(bind=self.engine)

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
    
    d = Database('quicktest.db')
    tuser2 = User(account='another', description='AND', official=False)
    tuser = User(account='7flying', description='SUPER', official=False)
    with session_scope(d) as session:
        tuser2.follow(tuser)
        session.add_all([tuser, tuser2])
        #session.commit()

    s = select([user.c.acount, user.c.description, user.c.official,
                user.c.following]).where(user.c.account == 'another')
    conn = d.engine.connect()
    result = conn.execute(s)
    print result
