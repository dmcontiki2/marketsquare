import jwt, time
print(jwt.encode({"scope":"admin","sub":"rig-admin","name":"rig-admin","exp":int(time.time())+86400}, "rigjwt_rigjwt_rigjwt_rigjwt_rigjwt_rigjwt", algorithm="HS256"))
