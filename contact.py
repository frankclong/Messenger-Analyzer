class Contact():
	def __init__ (self, name):
		self.name = name
		#self.sent_msg_dates = []
		#self.rcvd_msg_dates = []
		self.msg_dates = []
		self.msg_counts = []

	# Add to list of date objects
	# Perform calculations/analysis using this data
	def add_sent_msg_date(self, msg_date):
		msg_year = msg_date.year
		if msg_year not in self.msg_dates:
			self.msg_dates.append(msg_year)
			self.msg_counts.append([0,1])
		else:
			pos = self.msg_dates.index(msg_year)
			self.msg_counts[pos][1] += 1


	def add_rcvd_msg_date(self, msg_date):
		msg_year = msg_date.year
		if msg_year not in self.msg_dates:
			self.msg_dates.append(msg_year)
			self.msg_counts.append([1,0])
		else:
			pos = self.msg_dates.index(msg_year)
			self.msg_counts[pos][0] += 1


	def get_dates(self):
		return self.msg_dates

	def get_counts(self):
		return self.msg_counts