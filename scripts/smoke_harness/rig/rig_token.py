import jwt, time, os
print(jwt.encode({"scope":"review","exp":int(time.time())+86400*30}, os.environ["MS_REVIEW_SECRET"], algorithm="HS256"))
