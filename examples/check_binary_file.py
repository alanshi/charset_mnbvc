import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from charset_mnbvc import api

if __name__ == '__main__':
    ret = api.is_binary('/Users/alan/mywork/mnbvc/setup.py')
    print(ret)
    ret = api.is_binary('/Users/alan/mywork/mnbvc/README.md')
    print(ret)
    ret = api.is_binary('/Users/alan/mywork/mnbvc/dist/charset_mnbvc-0.0.15.tar')
    print(ret)