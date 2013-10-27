etqwlib
=======

This is a small library for querying Enemy Territory: Quake Wars servers.

usage
-----

Usage is pretty simple. The fetch_data function returns a 3-tuple containing
the server variables, player data and server info in that order. Each of these
is a dictionary:

	import etqwlib
	vars, players, info = etqwlib.fetch_data('example.com', 27733)
	print vars['si_maxplayers']  # '23'
	print players[10]['nick']    # nick of player id 10 (with colors stripped)
	print info['time_left']      # number of seconds left

