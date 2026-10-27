"""USTAR headers safe for Darwin 6 gnutar's 100-byte name boundary.
The old extractor truncates a full (non-NUL-terminated) name field to 99
bytes. Use USTAR's prefix even at exactly 100 bytes; file bytes are unchanged.
"""
import tarfile
class Darwin6TarInfo(tarfile.TarInfo):
    def tobuf(self,format=tarfile.USTAR_FORMAT,encoding=tarfile.ENCODING,errors='surrogateescape'):
        data=super().tobuf(format,encoding,errors)
        if format!=tarfile.USTAR_FORMAT or b'\0' in data[:100]:return data
        prefix,name=self.name.rsplit('/',1)
        prefix=prefix.encode(encoding,errors);name=name.encode(encoding,errors)
        if len(prefix)>155 or len(name)>99:raise ValueError('No safe USTAR prefix split: '+self.name)
        header=bytearray(data[:512]);header[:100]=name.ljust(100,b'\0');header[345:500]=prefix.ljust(155,b'\0')
        header[148:156]=b' '*8;checksum=sum(header);header[148:156]=('%06o\0 '%checksum).encode('ascii')
        return bytes(header)+data[512:]
