from ming import Session
from ming.orm import ThreadLocalORMSession

doc_session = Session.by_name('chef')
orm_session = ThreadLocalORMSession(doc_session)
