from os.path import abspath, dirname
my_cwd = abspath(dirname(__file__))

sql_migration_file =  "{}/migration_003_down.sql".format(abspath(dirname(__file__)))


a = open(sql_migration_file).read()


