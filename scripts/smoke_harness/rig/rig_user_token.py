import jwt, time, sys
email=sys.argv[1]
print(jwt.encode({"scope":"user","sub":email,"exp":int(time.time())+86400*30}, "rigjwt_rigjwt_rigjwt_rigjwt_rigjwt_rigjwt", algorithm="HS256"))
