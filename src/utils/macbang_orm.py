from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class MacApp(Base):
    __tablename__ = 'mac_app'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    name = Column(String, nullable=False)
    latest_version = Column(String, nullable=False)
    detail_link = Column(String, nullable=False)
    description = Column(String, nullable=False)
    slogan = Column(String)
    content = Column(String)
    download_link = Column(String)
    own_download_link = Column(String)
    source = Column(String, default='website')
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now)

    versions = relationship('MacAppVersions', back_populates='app')
    categories = relationship('MacCategory', secondary='mac_category_apps', back_populates='apps')


class MacAppVersions(Base):
    __tablename__ = 'mac_app_versions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    version = Column(String, nullable=False)
    detail_link = Column(String, nullable=False)
    download_link = Column(String)
    own_download_link = Column(String)
    app_id = Column(Integer, ForeignKey('mac_app.id'))
    source = Column(String, default='website')
    web_post_time = Column(DateTime)
    article_id = Column(Integer, ForeignKey('mac_article.id'))
    create_time = Column(DateTime, default=datetime.now)

    app = relationship('MacApp', back_populates='versions')


class MacCategory(Base):
    __tablename__ = 'mac_category'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    description = Column(String)
    link = Column(String)
    create_time = Column(DateTime, default=datetime.now)

    apps = relationship('MacApp', secondary='mac_category_apps', back_populates='categories')
    articles = relationship('MacArticle', back_populates='category')


class MacCategoryApps(Base):
    __tablename__ = 'mac_category_apps'

    app_id = Column(Integer, ForeignKey('mac_app.id'), primary_key=True)
    category_id = Column(Integer, ForeignKey('mac_category.id'), primary_key=True)
    create_time = Column(DateTime, default=datetime.now)


class MacArticle(Base):
    __tablename__ = 'mac_article'

    id = Column(Integer, primary_key=True, autoincrement=True)
    web_post_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    content = Column(String, nullable=False)
    thumbnail = Column(String, nullable=False)
    detail_link = Column(String, nullable=False)
    download_link = Column(String)
    own_download_link = Column(String)
    category_id = Column(Integer, ForeignKey('mac_category.id'))
    web_post_time = Column(DateTime)
    create_time = Column(DateTime, default=datetime.now)

    category = relationship('MacCategory', back_populates='articles')


class MacTag(Base):
    __tablename__ = 'mac_tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String)
    link = Column(String, nullable=False)
    create_time = Column(DateTime, default=datetime.now)


class MacArticleTags(Base):
    __tablename__ = 'mac_article_tags'
    article_id = Column(Integer, ForeignKey('mac_article.id'), primary_key=True)
    tag_id = Column(Integer, ForeignKey('mac_tag.id'), primary_key=True)
    create_time = Column(DateTime, default=datetime.now)
