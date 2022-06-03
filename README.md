# pyusbpd

Python structures and decoding for USB Power Delivery exploration, testing and maybe more?

```python
from pyusbpd.message import parse

msg = parse(b"\x41\x0C")
print(msg)
# <pyusbpd.message.GoodCRCMessage object at 0x7f0a8b2ca9b0>

print(msg.header)
# Message.Header(message_type=1, port_data_role=<PortDataRole.UFP: False>, port_power_role=False, specification_revision=<SpecificationRevision.REV20: 1>, cable_plug=False, message_id=6, num_data_obj=0, extended=False)
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
