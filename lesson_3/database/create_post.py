from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from . import db_tables


class Database:
    def __init__(self, db_client):
        engine = create_engine(db_client)
        db_tables.Base.metadata.create_all(engine)
        self.maker = sessionmaker(bind=engine)

    def create_post(self, data):
        session = self.maker()
        author = self._get_or_create(
            session,
            db_tables.Author,
            db_tables.Author.url,
            data["author_data"]["url"],
            **data["author_data"],
        )
        tags = map(
            lambda tag_data: self._get_or_create(
                session, db_tables.Tag, db_tables.Tag.url, tag_data["url"], **tag_data
            ),
            data["tags_data"],
        )
        post = self._get_or_create(
            session,
            db_tables.Post,
            db_tables.Post.url,
            data["post_data"]["url"],
            **data["post_data"],
            author=author,
        )
        comments = self._pass_comments(session, data["comments_data"])
        post.tag.extend(tags)
        post.comment.extend(comments)
        session.add(post)
        try:
            session.commit()
        except Exception:
            session.rollback()
        finally:
            session.close()

    def _get_or_create(self, session, table, filter_key, filter_value, **data):
        db_data = session.query(table).filter(filter_key == filter_value).first()
        if not db_data:
            db_data = table(**data)
            session.add(db_data)
        return db_data

    def _pass_comments(self, session, data):
        result = []
        if data:
            for comment in data:
                comment_author = self._get_or_create(
                    session,
                    db_tables.Author,
                    db_tables.Author.url,
                    comment["comment"]["user"]["url"],
                    **comment["comment"]["user"],
                )
                db_comment = self._get_or_create(
                    session,
                    db_tables.Comment,
                    db_tables.Comment.id,
                    comment["comment"]["id"],
                    **comment["comment"],
                    author=comment_author,
                )
                result.append(db_comment)
                if comment["comment"]["children"]:
                    result.extend(self._pass_comments(session, comment["comment"]["children"]))
        return result
