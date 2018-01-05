from datetime import datetime
from datetime import timedelta
import time
from acg_forum.models import Article

t1 = datetime.now()

time.sleep(1)

t2 = datetime.now()

print(t1, t2)
print(type(t2-t1))
print((t2-t1).seconds)
print((t2-t1).days)
print('----------')

print(type(time.time()))
print(type(Article.create_time))
print(Article.create_time)
print(type(datetime.now()))
print(type(datetime.now()))
print((datetime.now() - timedelta(days=7)).day)
print(type(datetime.now() - timedelta(days=7)))
# print(datetime.now().day)
