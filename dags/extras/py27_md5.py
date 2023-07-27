from sys import argv

from include.encryption import md5


def main(dag_id):
    result = md5(dag_id)
    print result
    return result


if __name__ == '__main__':
    main(argv[1])
