from sqlalchemy import Column, Table, String, Integer, DateTime, Boolean, ForeignKey, MetaData
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Author(Base):
    __tablename__ = "author"
    id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    post = relationship("Post")

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.full_name = kwargs["full_name"]
        self.url = kwargs["url"]


tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("tag_id", Integer, ForeignKey("tag.id")),
    Column("post_id", Integer, ForeignKey("post.id")),
)


class Post(Base):
    __tablename__ = "post"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    img = Column(String)
    author_id = Column(Integer, ForeignKey("author.id"))
    created_at = Column(DateTime, nullable=False)
    author = relationship("Author")
    tag = relationship("Tag", secondary=tag_post)
    comment = relationship("Comment")


class Tag(Base):
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False, unique=True)
    post = relationship("Post", secondary=tag_post)


class Comment(Base):
    __tablename__ = "comment"
    id = Column(Integer, primary_key=True)
    post_id = Column(Integer, ForeignKey("post.id"))
    author_id = Column(Integer, ForeignKey("author.id"))
    parent_id = Column(Integer, ForeignKey("comment.id"), nullable=True)
    likes_count = Column(Integer)
    body = Column(String)
    hidden = Column(Boolean)
    deep = Column(Integer)
    created_at = Column(DateTime, nullable=False)
    author = relationship("Author")

    def __init__(self, **kwargs):
        self.id = kwargs["id"]
        self.author_id = kwargs["user"]["id"]
        self.parent_id = kwargs["parent_id"]
        self.likes_count = kwargs["likes_count"]
        self.body = kwargs["body"]
        self.hidden = kwargs["hidden"]
        self.deep = kwargs["deep"]
        self.created_at = datetime.fromisoformat(kwargs["created_at"])
