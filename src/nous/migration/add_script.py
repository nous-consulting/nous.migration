from pkg_resources import resource_filename
import datetime
import os

MIGRATION_FILE_TEMPLATE = """\
def upgrade(connection):
    pass

def downgrade(connection):
    pass

"""

UPGRADE_FILE_TEMPLATE = """\
-- alter table users add column net_worth integer not null default 0;
-- alter table users add column last_daily_money timestamp not null default (now() at time zone 'UTC');
-- create table admins (
--        id bigserial not null,
--        login varchar(20) not null,
--        password char(36),
--        primary key(id));;
"""

DOWNGRADE_FILE_TEMPLATE = """\
-- alter table users drop column net_worth;
-- drop table admins;
"""

def new_version(package, name, script_type='sql', vcs='git', schema_diff=None, editor='vim'):
    version = datetime.datetime.now().strftime("%Y%m%d%H%M")

    migration_fn = None
    upgrade_fn = None
    downgrade_fn = None

    if script_type == 'sql':
        upgrade_fn = '%s_%s.sql' % (version, name)
        downgrade_fn = '%s_downgrade.sql' % (version)
    elif script_type == 'mixed':
        migration_fn = '%s_%s.py' % (version, name)
        upgrade_fn = '%s_upgrade.sql' % (version)
        downgrade_fn = '%s_downgrade.sql' % (version)
    elif script_type == 'py':
        migration_fn = '%s_%s.py' % (version, name)

    artefacts = []
    # Create upgrade / downgrade scripts.
    if migration_fn:
        migration_fn = resource_filename(package, migration_fn)
        file(migration_fn, 'w').write(MIGRATION_FILE_TEMPLATE)
        os.system('%s add %s' % (vcs, migration_fn))
        artefacts.append(migration_fn)

    if upgrade_fn:
        upgrade_fn = resource_filename(package, upgrade_fn)
        file(upgrade_fn, 'w').write(UPGRADE_FILE_TEMPLATE)
        if schema_diff is not None:
            os.system('%s >> %s' % (schema_diff, upgrade_fn))
        artefacts.append(upgrade_fn)

    if downgrade_fn:
        downgrade_fn = resource_filename(package, downgrade_fn)
        file(downgrade_fn, 'w').write(DOWNGRADE_FILE_TEMPLATE)
        if schema_diff is not None:
            os.system('%s >> %s' % (schema_diff, downgrade_fn))
        artefacts.append(downgrade_fn)

    os.system('%s %s' % (editor, ' '.join(artefacts)))

    for artefact in artefacts:
        os.system('%s add %s' % (vcs, artefact))
