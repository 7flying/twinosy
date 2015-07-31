# -*- coding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Boolean, Integer, String, Table, \
     ForeignKey
from sqlalchemy.orm import relationship, backref, sessionmaker
# testing
from sqlalchemy import create_engine


engine = create_engine('sqlite:///:memory:', echo=False)

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
    following = relationship("User", secondary=following,
                             primaryjoin=uid==following.c.user,
                             secondaryjoin=uid==following.c.follows)
    followers = relationship("User", secondary=followers,
                             primaryjoin=uid==followers.c.user,
                             secondaryjoin=uid==followers.c.follower)

    def __repr__(self):
        return ("<User(uid='%d', account='%s', description='%s'," + \
                " official='%s')>") % (self.uid, self.account,
                                       self.description, self.official)

if __name__ == '__main__':
    print " ~ Starting tests ~ \n"
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    # Without a engine:
    # Session = sessionmaker()
    # Session.configure(bind=engine)
    session = Session()
    tuser = User(account='7flying', description='SUPER', official=False)
    session.add(tuser)
    tuser2 = User(account='another', description='AND', official=False,
                  following=[tuser])
    session.add(tuser2)
    session.commit()
    print tuser
    print tuser2
    print tuser2.following
    session.close()
    
