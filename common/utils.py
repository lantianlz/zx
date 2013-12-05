# -*- coding: utf-8 -*-


def uuid_without_dash():
	import uuid
	return str(uuid.uuid1()).replace('-', '')