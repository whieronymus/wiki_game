from sqlalchemy import Column, ForeignKey, Integer, String, Table, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import create_engine

from wiki_api import visit_page_and_get_links


Base = declarative_base()
engine = create_engine('sqlite:///sql.db',
                       connect_args={'check_same_thread': False},
                       echo=False)

page_link = Table(
    'page_link',
    Base.metadata,
    Column('page_link_id', Integer, primary_key=True),
    Column('link_id', Integer, ForeignKey('page.page_id')),
    Column('backlink_id', Integer, ForeignKey('page.page_id'))
)


class Page(Base):
    __tablename__ = 'page'
    page_id = Column(Integer, primary_key=True)
    title = Column(String(250), nullable=False)
    sourced_links = Column(Boolean, nullable=False, default=False)
    sourced_backlinks = Column(Boolean, nullable=False, default=False)
    links = relationship(
        'Page',
        secondary=page_link,
        primaryjoin=page_id == page_link.c.link_id,
        secondaryjoin=page_id == page_link.c.backlink_id,
        backref=backref('backlinks', lazy='subquery')
    )

    def __repr__(self):
        return f"Page(title={self.title})"

    @classmethod
    def get_or_create(cls, title: str) -> 'Page':
        try:
            instance = session.query(cls).filter_by(title=title).one()
        except NoResultFound:
            instance = cls(title=title)
            session.add(instance)
            session.commit()

        return instance

    def get_links(self):
        """
        Use this method instead of the links attribute to get a list
        of linked pages.

        This method will return the list of linked
        pages if the page has previously been visited or it will
        go grab the list of links from the API.
        """
        if not self.sourced_links:
            titles = visit_page_and_get_links(self.title, "links")

            for title in titles:
                try:
                    page = session.query(Page).filter_by(title=title).one()
                except NoResultFound:
                    page = Page(title=title)
                self.links.append(page)

            # Set page to visited so we don't need to visit the API
            # for links on this page again
            self.sourced_links = True
            session.commit()

        return self.links

    def get_backlinks(self):
        """
        Use this method instead of the backlinks attribute to get a list
        of backlinked pages.

        This method will return the list of backlinked
        pages if the page has previously been visited or it will
        go grab the list of links from the API..
        """
        if not self.sourced_backlinks:
            titles = visit_page_and_get_links(self.title, "backlinks")

            for title in titles:
                try:
                    page = session.query(Page).filter_by(title=title).one()
                except NoResultFound:
                    page = Page(title=title)
                page.links.append(self)

            # Set page to visited so we don't need to visit the API
            # for links on this page again
            self.sourced_backlinks = True
            session.commit()

        return self.backlinks


Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
