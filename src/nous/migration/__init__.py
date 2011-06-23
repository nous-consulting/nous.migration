import sys
from collections import defaultdict
import re
import pkg_resources

from sqlalchemy import engine_from_config
from paste.deploy.loadwsgi import ConfigLoader

MIGRATION_SCRIPT_REGEX = re.compile(r'(?P<version>\d+)(_upgrade)*(_(?P<name>.*))*(.(?P<class>py|sql))$')


class PythonMigrationScript(object):

    def __init__(self, version, file_names, package):
        pass

    def upgrade(self, engine):
        pass

    def downgrade(self, engine):
        pass


class SQLMigrationScript(object):

    def __init__(self, version, files_names, package):
        self.package = package
        self.version = version

    def upgrade(self, engine):
        connection = engine.connect()
        statements = pkg_resources.resource_string(self.package, self.upgrade_file)
        connection.execute(statements)

    def downgrade(self, engine):
        connection = engine.connect()
        statements = pkg_resources.resource_string(self.package, self.downgrade_file)
        connection.execute(statements)


def make_migration_script(version, file_names, package):
    for file_name in file_names:
        groups = MIGRATION_SCRIPT_REGEX.match(file_name).group_dict()
        if groups['class'] == 'py':
            return PythonMigrationScript(version, file_name, package)
        elif groups['class'] == 'sql':
            return SQLMigrationScript(version, file_name, package)


class DBMigrator(object):

    def __init__(self, engine, package):
        self.engine = engine
        self.connection = engine.connect()
        self.package = package
        self.evolution_script_list = self.collect_evolution_scripts()
        self.evolution_script_dict = dict([(s.version, s)
                                           for s in self.evolution_script_list])

    def set_up_migration(self, init_migration=None, run_scripts=False):
        versions_table = self.connection.execute(
            "select * from information_schema.tables"
            " where table_schema = 'public'"
            "   and table_name = 'versions'").fetchall()

        if versions_table:
            return False # Version table already present, bailing out

        tx = self.connection.begin()
        if init_migration is not None:
            init_migration.upgrade(self.engine)

        self.connection.execute("create table versions (version bigint not null)")

        if run_scripts:
            self.run_scritps(self.get_not_executed_scripts())
        else:
            for script in self.get_not_executed_scripts():
                self.mark_script_as_executed(script)

        tx.commit()
        return True

    def collect_evolution_scripts(self):
        script_files = pkg_resources.resource_listdir(self.package, '')
        script_data = defaultdict(list)

        for script_file in script_files:
            res = MIGRATION_SCRIPT_REGEX.match(script_file)
            if res is None:
                continue # Not a migration script, skipping
            groups = res.groupdict()
            script_data[groups['version']].append(script_file)

        return [make_migration_script(version, file_names, self.package)
                for version, file_names in sorted(script_data.items())]

    @property
    def last_version(self):
        return self.evolution_scripts[-1].version

    @property
    def db_version(self):
        connection = self.engine.connect()
        versions = list(connection.execute("select * from versions"))
        if 0 < len(versions) < 2:
            return versions[0][0]
        else:
            raise ValueError(versions)
        connection.close()

    def mark_script_as_executed(self, version):
        self.connection.execute("insert into versions %d" % version)

    def run_scripts(self, scripts):
        for script in scripts:
            print "Running:", script.title
            script.upgrade(self.connection)
            print "Setting database version to:", script.versions
            self.mark_script_as_executed(script.version)

    def run_downgrade_scripts(self, scripts):
        for script in scripts:
            print "Running:", script.title
            script.downgrade(self.connection)
            print "Setting script %d as not run:", script.version
            self.connection.execute("delete from versions where version = %d" % script.version)

    def get_executed_scripts(self):
        versions = list(self.connection.execute("select * from versions order by version desc"))
        return [version[0]
                for version in versions]

    def get_not_executed_scripts(self):
        return sorted(set(self.evolution_script_dict.keys()) - set(self.get_executed_scripts()))

    def upgrade(self, version=None):
        tx = self.connection.begin()
        if version is None:
            scripts = self.get_not_executed_scripts()
        else:
            scripts = [version]
        self.run_scripts(scripts)
        tx.commit()

    def downgrade(self, version=None):
        tx = self.connection.begin()
        if version is None:
            version = self.get_executed_scripts()[-1]
        self.run_downgrade_scripts([version])
        tx.commit()

    def add_script(self):
        pass


def main():
    config_file = sys.argv[1] if len(sys.argv) > 1 else 'development.ini'
    action = sys.argv[2] if len(sys.argv) > 2 else 'upgrade'
    version = sys.argv[3] if len(sys.argv) > 3 else None

    clo = ConfigLoader(config_file)

    migrator_config = dict(clo.parser.items('nous.migration'))
    section = migrator_config['app']
    package = migrator_config['package']

    engine = engine_from_config(dict(clo.parser.items(section)))

    migrator = DBMigrator(engine, package)

    if action == 'upgrade':
        migrator.upgrade(version)
    if action == 'setup':
        migrator.set_up_migration(run_scripts=True)
    if action == 'downgrade':
        migrator.downgrade(version)
    if action == 'add_script':
        migrator.add_script()
