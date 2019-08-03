class Contact():
	def __init__ (self, name):
		self.name = name
		#self.sent_msg_dates = []
		#self.rcvd_msg_dates = []
		self.msg_dates = []
		self.msg_counts = []

	# Add to list of date objects
	# Perform calculations/analysis using this data
	def add_sent_msg_date(self, new_date):
		msg_year = new_date.year
		msg_month = new_date.month
		pos = -1

		# If array empty, just append
		if len(self.msg_dates) == 0:
			self.msg_dates.append(new_date)
			self.msg_counts.append([0,1])
		else:
			# Look for if month/year combo already exists
			for ex_date in self.msg_dates:
				if ex_date.year == msg_year and ex_date.month == msg_month:
					pos = self.msg_dates.index(ex_date)
					exit
	
			if pos != -1:
				self.msg_counts[pos][1] += 1
			else:
				self.msg_dates.append(new_date)
				self.msg_counts.append([0,1])


	def add_rcvd_msg_date(self, new_date):
		msg_year = new_date.year
		msg_month = new_date.month
		pos = -1

		# If array empty, just append
		if len(self.msg_dates) == 0:
			self.msg_dates.append(new_date)
			self.msg_counts.append([1,0])
		else:
			# Look for if month/year combo already exists
			for ex_date in self.msg_dates:
				if ex_date.year == msg_year and ex_date.month == msg_month:
					pos = self.msg_dates.index(ex_date)
					exit
	
			if pos != -1:
				self.msg_counts[pos][0] += 1
			else:
				self.msg_dates.append(new_date)
				self.msg_counts.append([1,0])

	def get_dates(self):
		return self.msg_dates

	def get_counts(self):
		return self.msg_counts