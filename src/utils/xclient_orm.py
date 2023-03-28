from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class MacApp(Base):
    __tablename__ = 'mac_app'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    name = Column(String, nullable=False)
    latest_version = Column(String, nullable=False)
    description = Column(String, nullable=False)
    detail_link = Column(String, nullable=False)
    category_link = Column(String)
    download_link = Column(String)
    source = Column(String, default='website')
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now)

    versions = relationship('MacAppVersion', back_populates='app')
    categories = relationship('MacCategory', secondary='mac_category_apps', back_populates='apps')


class MacAppVersion(Base):
    __tablename__ = 'mac_app_versions'
    id = Column(Integer, primary_key=True)
    version = Column(String, nullable=False)
    detail_link = Column(String, nullable=False)
    download_link = Column(String, nullable=False)
    app_id = Column(Integer, ForeignKey('mac_app.id'))
    source = Column(String, default='website')
    create_time = Column(DateTime, default=datetime.now)

    app = relationship('MacApp', back_populates='versions')


class MacCategory(Base):
    __tablename__ = 'mac_category'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    link = Column(String)
    create_time = Column(DateTime, default=datetime.now)

    apps = relationship('MacApp', secondary='mac_category_apps', back_populates='categories')


class MacCategoryApp(Base):
    __tablename__ = 'mac_category_apps'
    app_id = Column(Integer, ForeignKey('mac_app.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('mac_category.id'), primary_key=True)
