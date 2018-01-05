from acg_forum import create_app, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from acg_forum import models

app = create_app('development')

Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix
    app.wsgi_app = ProxyFix(app.wsgi_app)
    print(app)
    print(app.url_map)
    manager.run()
