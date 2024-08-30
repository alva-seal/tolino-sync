from pytolino.tolino_cloud import Client, PytolinoException
import datetime
import os
import time
import pickle
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, func, create_engine, Float, desc
from sqlalchemy.orm import relationship, sessionmaker

tolino_user = os.environ['TOLINO_USER']
tolino_password = os.environ['TOLINO_PASSWORD']
debug = os.environ['DEBUG']


engine = create_engine('sqlite:///config/tolino_sync.db', echo = True)
engine = create_engine('sqlite://config/tolino_sync.db')

class Base(DeclarativeBase):
    pass

class Syncs(Base):
    __tablename__ = "syncs"
    id = Column(Integer, primary_key=True)
    revision = Column(String, unique=True)
    date = Column(DateTime(timezone=True), onupdate=func.now()) 
    patch = relationship("Patches", backref = "sync")

class Patches(Base):
    __tablename__ = "patches"
    id = Column(Integer, primary_key=True)
    position = Column(String)
    category = Column(String)
    book = Column(String)
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
    sync_id = Column(Integer,  ForeignKey('syncs.id'))
    #sync = relationship("Syncs", back_populates = "patches")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

with Session() as session:
    results = session.query(Syncs).order_by(desc(Syncs.date)).first()
revision = results.revision
print(revision)
get_data = True
if get_data:
    client = Client()
    client.login(tolino_user, tolino_password)
    client.register()
    inventory = client.get_inventory()
    response = client.sync(revision)
    client.logout()
    file = open('data2', 'wb')
    pickle.dump(response, file)
    file.close()
else:
    file = open('data', 'rb')
    response = pickle.load(file)
    file.close()
syncdict= response.json()
syncdict= response
revision = syncdict['revision']


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
                    book = book,
                    op_type = op_type,
                    sync_id=sync.id
                    )
        
                
            session.add(patch_data)
        session.commit()
        
 
while true:
    time.sleep(20)
    print('.')
