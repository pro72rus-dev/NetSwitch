import pydivert
import ctypes

# Check admin
is_admin = ctypes.windll.shell32.IsUserAnAdmin()
print(f"Admin: {is_admin}")

# Check if WinDivert driver exists
import os
driver_paths = [
    os.path.join(os.path.dirname(pydivert.__file__), 'WinDivert.sys'),
    os.path.join(os.path.dirname(pydivert.__file__), 'x64', 'WinDivert.sys'),
    r'C:\Windows\System32\drivers\WinDivert.sys',
]
for p in driver_paths:
    exists = os.path.exists(p)
    print(f"Driver: {p} -> {'EXISTS' if exists else 'NOT FOUND'}")

# Try to list pydivert package files
pkg_dir = os.path.dirname(pydivert.__file__)
print(f"\nPackage dir: {pkg_dir}")
for f in os.listdir(pkg_dir):
    if 'WinDivert' in f or 'divert' in f.lower():
        print(f"  {f}")
