Yet another sqlalchemy based database schema migration tool
===========================================================

Installation
------------

To install it, add:

[migration]
recipe = zc.recipe.egg
eggs=
  nous.migration

to your buildout.cfg

You might want to add your databse driver pakcage and your application
package like this:

[migration]
recipe = zc.recipe.egg
eggs=
  psycopg2
  nous.some_app
  nous.migration

Configuration
-------------

Add to your development.ini or some other kind of ini:

[nous.migration]
app = app:busy
package = busy.migration

migrator expects sqlalchemy configuration to be present in the app
section, for example:

[app:busy]
sqlalchemy.url = postgresql:///development

I might add sqlalchemy configuration to the migration section too if
someone will ask.

You can also add:

vcs = git
schema_diff_cmd = git diff src/busy/models/schema.sql

so that add_script command would add the files to the version control
system, and populate them with the delta of your schema automatically.

These two settings might go the setup.cfg as they are not really
deployment related and are never required to run your application.

Usage
-----

bin/migrate development.ini [upgrade|downgrade|setup|add_script] [version]


Integrating with your application
---------------------------------


Add something like this:

    engine = engine_from_config(conf, 'sqlalchemy.')
    DBMigrator(engine, 'busy.migration').set_up_migration(init_migration=DBSetUp(), run_scripts=False)

to your setup_app, or in your initialize_sql

DBSetUp is a class that has an "upgrade" method that initializes your
schema.

You can do it in multiple ways, you can add a migration script that
sets up your tables and then migrate that using migration scripts:

    DBMigrator(engine, 'busy.migration').set_up_migration(run_scripts=True)

Or you can have a canonical schema set up and initialize it all at
once and just mark all the scripts as 'done'

    DBMigrator(engine, 'busy.migration').set_up_migration(init_migration=DBSetUp(), run_scripts=False)

Scripts
-------

Put your scripts in the package that you have set up in your migration
config.

Scripts are tracked separately.

Script files should be of this format:

Timestamp    script title
201006231515_python_migration_script.py

Timestamp    script title
201006231516_sql_migration_script.sql
201006231516_downgrade.sql

If both, python and sql exist with the same timestamp I assume that
python script is responsible for running sql scripts. I might add
helpers to make running an sql file later.

201006231517_mixed_migration_script.py
201006231517_upgrade.sql
201006231517_downgrade.sql

Sql files are just that, sql files that will be executed. Python files
should contain callables: upgrade and downgrade, downgrade can be
missing if script is not intended to be reversable.

TODO: add example migration scripts
