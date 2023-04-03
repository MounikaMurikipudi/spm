from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
def token(rollno,seconds):
    s=Serializer('*67@hjyijk',seconds)
    return s.dumps({'user':rollno}).decode('utf-8')
