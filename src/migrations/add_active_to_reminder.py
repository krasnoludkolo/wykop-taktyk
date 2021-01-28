import shelve

with shelve.open('reminders.db', writeback=True) as db:
    for key, value in db.items():
        value.active = True
