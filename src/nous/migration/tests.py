from nous.migration import MIGRATION_SCRIPT_REGEX


def test_migration():

    x = MIGRATION_SCRIPT_REGEX.match('201106200106_upgrade_foo_bar_baz.py').groupdict()
    assert x['version'] == '201106200106'
    assert x['name'] == 'foo_bar_baz'
    assert x['class'] == 'py'

    x = MIGRATION_SCRIPT_REGEX.match('201106200106_foo_bar_baz.py').groupdict()
    assert x['version'] == '201106200106'
    assert x['name'] == 'foo_bar_baz'
    assert x['class'] == 'py'

    x = MIGRATION_SCRIPT_REGEX.match('201106200106_foo_bar_baz.sql').groupdict()
    assert x['version'] == '201106200106'
    assert x['name'] == 'foo_bar_baz'
    assert x['class'] == 'sql'

    assert MIGRATION_SCRIPT_REGEX.match('201106200106_foo_bar_baz.py~') is None

