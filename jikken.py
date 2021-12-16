

class MyClass(object):
    """ 自作のクラス """

    def __enter__(self):
        print("前処理")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("後処理")

with MyClass() as m:
    print("aaaa error is about to explode!!!")
    raise RuntimeError("test")