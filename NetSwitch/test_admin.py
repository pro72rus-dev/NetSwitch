import pydivert, os, tempfile

results = []
tests = [
    ('SOCKET', 'process.name == "python.exe"'),
    ('SOCKET', 'true'),
    ('NETWORK', 'true'),
    ('NETWORK', 'tcp.DstPort == 443'),
    ('FLOW', 'true'),
]

for layer_name, filt in tests:
    layer = getattr(pydivert.Layer, layer_name)
    try:
        with pydivert.WinDivert(filt, layer=layer, flags=pydivert.Flag.SNIFF) as w:
            results.append('OK: ' + layer_name + ' ' + filt)
    except Exception as e:
        results.append('FAIL: ' + layer_name + ' ' + filt + ' -> ' + str(e))

outpath = os.path.join(os.environ.get('SYSTEMROOT', r'C:\Windows'), 'Temp', 'pydivert_test.txt')
with open(outpath, 'w') as f:
    f.write('\n'.join(results))
