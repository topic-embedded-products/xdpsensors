#!/usr/bin/env python

import iio

def get_attr_float(chn, key, default):
	v = chn.attrs.get(key, None)
	if v is None:
		return default
	return float(v.value)

class SensorChannel:
	def __init__(self, chn, k):
		self.name = chn.name or chn.id
		self.val = chn.attrs[k]
		self.chn = chn
		self.offset = get_attr_float(chn, 'offset', 0)
		self.scale = get_attr_float(chn, 'scale', 1)
	def get(self):
		v = float(self.val.value)
		return (v + self.offset) * self.scale

def create_sensor_channel(channels, chn):
	if 'raw' in chn.attrs:
		k = 'raw'
	elif 'input' in chn.attrs:
		k = 'input'
	else:
		return
	channels.append(SensorChannel(chn, k))

class SensorChannels:
	def __init__(self, dev, blacklist = lambda x: False):
		self.channels = []
		self.name = dev.name
		for chn in dev.channels:
			if chn.output:
				# Ignore outputs
				continue
			if blacklist(chn):
				continue
			create_sensor_channel(self.channels, chn)

def create_sensor_channel_list(ctx, blacklist):
	sc = []

	for dev in ctx.devices:
		s = SensorChannels(dev, blacklist)
		if s.channels:
			sc.append(s)
	return sc

def show(sc):
	for s in sc:
		print(s.name)
		for c in s.channels:
			try:
				v = c.get()
			except OSError as e:
				v = e.strerror
			print("\t%s: %s" % (c.name, v))


if __name__ == '__main__':
	import sys
	import time
	uri = None
	if len(sys.argv) > 1:
		uri = sys.argv[1]
	ctx = iio.Context(uri)
	sl = create_sensor_channel_list(ctx, lambda c: c.id.startswith('volt'))
	show(sl)
	time.sleep(1)
	show(sl)
