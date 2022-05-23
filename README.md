# pyusbpd

Python structures and decoding for USB Power Delivery exploration, testing and maybe more?

```python
from pyusbpd.message import Message
from pyusbpd.enum import SOP

msg = Message(sop=SOP.SOP, raw=b"\x41\x0C").decode()

print(msg)
# <pyusbpd.message.GoodCRCMessage object at 0x7f0a8b2ca9b0>

print(msg.message_header)
# USB Power Delivery Message Header
# ---
# Extended: False
# Number of Data Objects: 0
# MessageID: 6
# Port Power Role: False
# Cable Plug: False
# Specification Revision: Revision 2.0
# Port Data Role: False
# Message Type: 1
```

pyusbpd is mostly in a PoC state, but feel free to send pull requests ;-)

## Install

Using `pip`:

```bash
pip install pyusbpd
```

Or using `git`:

```bash
git clone https://github.com/jeanthom/pyusbpd
cd pyusbpd
python setup.py install --user
```
