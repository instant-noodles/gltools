import struct

class GLReaderEOF(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return "Insufficient bytes to read"

class GLReader:
    def __init__(self, fname):
        self.file=open(fname, "rb")

    def close(self):
        self.file.close()

    def next(self, typ):
        if typ==float:
            return self.Float()
        elif typ==int:
            return self.Int()
        elif typ==str:
            return self.GLStr()

    def read(self, fmt):
        size=struct.calcsize(fmt)
        val=self.file.read(size)

        if size!=len(val):
            raise GLReaderEOF

        return struct.unpack(fmt, val)[0]

    def seek(self, pos):
        self.file.seek(pos)

    def Byte(self):
        return self.read("B")

    def Char(self):
        return self.read("s")

    def Float(self):
        return self.read("f")

    def GLBStr(self):
        sLen=self.Byte()

        return self.Str(sLen)

    def GLStr(self):
        sLen=self.Int()

        return self.Str(sLen)

    def Int(self):
        return self.read("I")

    def Str(self, sLen):
        output=b""
    
        for char in range(sLen):
            output+=self.Char()

        return output.decode("utf-8")

    def __del__(self):
        self.file.close()
