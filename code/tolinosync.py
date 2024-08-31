from pytolino.tolino_cloud import Client, PytolinoException
import datetime
import os
import time
import pickle
import configparser
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, create_engine, Float, desc, and_
from sqlalchemy.orm import relationship, sessionmaker


def main():
    config = configparser.ConfigParser()
    config.read('/config/tolino-sync.ini')

    tolino_user = config['TOLINO']['TOLINO_USER']
    tolino_password = config['TOLINO']['TOLINO_PASSWORD']
    debuging = config['TOLINO']['DEBUG']

    debuging = False;

    if debuging is True:
        engine = create_engine('sqlite:////config/tolino-sync.db', echo = True)
    else:
        engine = create_engine('sqlite:////config/tolino-sync.db')

    class Base(DeclarativeBase):
        pass

    class Syncs(Base):
        __tablename__ = "syncs"
        id = Column(Integer, primary_key=True)
        revision = Column(String, unique=True)
        date = Column(DateTime(timezone=True), onupdate=func.now()) 
        patch = relationship("Patches", backref = "sync")

    class Books(Base):
        __tablename__ = "books"
        id = Column(Integer, primary_key=True)
        tolino_identifier = Column(String, unique=True)
        calibre_uuid = Column(String)
        calibre_id = Column(Integer)
        title = Column(String)
        reseller_id = Column(Integer, ForeignKey('books.id')) 
        publisher = Column(String)
        booktype = Column(String)
        issued = Column(DateTime(timezone=True))
        book_format = Column(String)
        epubversion = Column(Float)
        author_id = Column(Integer, ForeignKey('books.id')) 
        tolino_last_modified = Column(DateTime(timezone=True))
        cover_url = Column(String)
        tolino_cover_last_modified = Column(DateTime(timezone=True))
        book_url = Column(String)
        tolino_book_last_modified = Column(DateTime(timezone=True))
        book_filesize = Column(Integer)
        protection = Column(String)
        transaction = Column(String)
        rendering = Column(String)
        
    class Authors(Base):
        __tablename__ = "authors"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        first_name = Column(String)
        last_name = Column(String)
             
    class Resellers(Base):
        __tablename__ = "resellers"
        id = Column(Integer, primary_key=True)
        name = Column(String)
        
    class Patches(Base):
        __tablename__ = "patches"
        id = Column(Integer, primary_key=True)
        position = Column(String)
        category = Column(String)
        book_id = Column(Integer, ForeignKey('books.id')) 
        op_type  = Column(String)
        name = Column(String)
        startPosition = Column(String)
        path = Column(String)
        modified = Column(DateTime(timezone=True))
        lastPosition = Column(String)
        currentPosition = Column(String)
        note = Column(String)
        op = Column(String)
        progress = Column(Float)
        text = Column(String)
        endPosition = Column(String)
        revision = Column(String)
        sync_id = Column(Integer, ForeignKey('syncs.id'))
        #sync = relationship("Syncs", back_populates = "patches")

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)


    try:
        with Session() as session:
            results = session.query(Syncs).order_by(desc(Syncs.date)).first()
        revision = results.revision
    except:
        revision = None 
    
    try:
        get_data = False
        if get_data:
            client = Client()
            client.login(tolino_user, tolino_password)
            client.register()
            inventory = client.get_inventory()
            response = client.sync(revision)
            client.logout()
            file = open('/config/data2', 'wb')
            pickle.dump(response, file)
            file.close()
            syncdict= response
            revision = syncdict['revision']
        else:
            client = Client()
            client.login(tolino_user, tolino_password)
            client.register()
            inventory = client.get_inventory()
            client.logout()
            file = open('/config/data', 'rb')
            response = pickle.load(file)
            file.close()
            syncdict= response.json()
            revision = syncdict['revision']
    except:
        return "Sync with cloud failed!"

    if len(inventory) > 0:
        with Session() as session:
            for item in inventory:
                results = session.query(Resellers.id).filter(Resellers.id == item['resellerId'])
                if results == None:
                    reseller = Resellers(
                        id = item['resellerId'],
                        name = item['resellerId']
                    )
                    result = session.add(reseller)
                    session.commit()
                results = session.query(Authors.id).filter(and_(Authors.name == item['epubMetaData']['author'][0]['name'], Authors.first_name == item['epubMetaData']['author'][0]['firstName'], Authors.last_name == item['epubMetaData']['author'][0]['lastName']))
                if results == None:
                    author = Authors(
                        name = item['epubMetaData']['author'][0]['name'],
                        first_name = item['epubMetaData']['author'][0]['firstName'],
                        last_name = item['epubMetaData']['author'][0]['lastName']
                    )
                    result = session.add(author)
                    session.commit()
                    author_id = author.id
                else:
                    author_id = results 
                results = session.query(Books.id).filter(Books.tolino_identifier == item['epubMetaData']['identifier'])
                if results == None:
                    if length(item['epubMetaData']['issued']) == 13:
                        issued = datetime.datetime.fromtimestamp(item['epubMetaData']['issued']/1000)
                    elif length(item['epubMetaData']['issued']) == 9:
                        issued = datetime.datetime.fromtimestamp(item['epubMetaData']['issued'])
                    else:
                        issued = None
                    if length(item['epubMetaData']['deliverable'][0]['purchased']) == 13:
                        tolino_last_modified = datetime.datetime.fromtimestamp(item['epubMetaData']['deliverable'][0]['purchased']/1000)
                    elif length(item['epubMetaData']['deliverable'][0]['purchased']) == 9:
                        tolino_last_modified = datetime.datetime.fromtimestamp(item['epubMetaData']['deliverable'][0]['purchased'])
                    else:
                        tolino_last_modified = None
                     
                    book = Books(
                        tolino_identifier = item['epubMetaData']['identifier'],
                        title = item['epubMetaData']['title'],
                        reseller_id = item['resellerId'],
                        publisher = item['epubMetaData']['publisher'],
                        booktype = item['epubMetaData']['type'],
                        issued = issued,
                        book_format = item['epubMetaData']['format'],
                        epubversion = item['epubMetaData']['format'],
                        author_id = author.id,
                        tolino_last_modified = tolino_last_modified,
                        cover_url = item['epubMetaData']['fileResource'][0]['resource'],
                        book_url = item['epubMetaData']['deliverable'][0]['resource'],
                        book_filesize = item['epubMetaData']['fileSize'],
                        protection = item['epubMetaData']['deliverable'][0]['protectionType'],
                        transaction = item['epubMetaData']['fileSize'],
                        rendering = item['ext_data']['renderingEngineSuitable']
                    )
                    result = session.add(book)
                    session.commit()
                    return('books committed')
                     
    return('premature end')
    if 'patches' in syncdict:
        with Session() as session:
            sync = Syncs(revision = revision, date = datetime.datetime.now())
            result = session.add(sync)
            session.commit()
            patches = syncdict['patches']
            for patch in patches:
                op = patch['op']
                path =  patch['path']
                revision = patch['value']['revision'] if patch['value']['revision'] else None
                position = patch['value']['position'] if 'position' in patch['value'] else None
                category =  patch['value']['category'] if 'category' in patch['value'] else None
                name =  patch['value']['name'] if 'name' in patch['value']  else None
                startPosition =  patch['value']['startPosition'] if 'startPosition' in  patch['value'] else None
                modified =  datetime.datetime.fromtimestamp(patch['value']['modified']/1000) if 'modified' in patch['value'] else None
                lastPosition =  patch['value']['lastPosition'] if 'lastPosition' in patch['value'] else None
                currentPosition =  patch['value']['currentPosition'] if 'currentPosition' in patch['value'] else None
                note =  patch['value']['note'] if 'note' in patch['value'] else None
                progress =  patch['value']['progress'] if 'progress' in patch['value'] else None
                text =  patch['value']['text'] if 'text' in patch['value'] else None
                endPosition =  patch['value']['endPosition'] if 'endPosition' in patch['value'] else None
                op_type = path.split('/')[3]
                book = path.split('/')[2]
                book_id = session.query(Books.id).filter(Books.tolino_identifier == book)
                patch_data = Patches(
                        position = position,
                        category = category,
                        name = name,
                        startPosition = startPosition,
                        path = path,
                        modified = modified,
                        lastPosition = lastPosition,
                        currentPosition = currentPosition,
                        note = note,
                        op = op,
                        progress = progress,
                        text = text,
                        endPosition = endPosition,
                        revision = revision,
                        book_id = book_id,
                        op_type = op_type,
                        sync_id=sync.id
                        )
            
                    
                session.add(patch_data)
            session.commit()
    return ('Sync done')
