class Contact():    
    def __init__ (self, name, folder_name):
        self.name = name
        #self.sent_msg_dates = []
        #self.rcvd_msg_dates = []
        self.msg_dates = []
        self.msg_counts = []
        self.folder_name = folder_name

    # Add to list of date objects
    # Perform calculations/analysis using this data
    def add_sent_msg_date(self, new_date, num_words):
        msg_year = new_date.year
        msg_month = new_date.month
        msg_day = new_date.day
        msg_hr = new_date.hour
        pos = -1

        # If array empty, just append
        if len(self.msg_dates) == 0:
            self.msg_dates.append(new_date)
            self.msg_counts.append([0,1,0,num_words])
        else:
            # Look for if month/year combo already exists
            for ex_date in self.msg_dates:
                if ex_date.year == msg_year and ex_date.month == msg_month and ex_date.day == msg_day and ex_date.hour == msg_hr:
                    pos = self.msg_dates.index(ex_date)

            # Exists
            if pos != -1:
                self.msg_counts[pos][1] += 1
                self.msg_counts[pos][3] += num_words
            # does not exist
            else:
                self.msg_dates.append(new_date)
                self.msg_counts.append([0,1,0,num_words])


    def add_rcvd_msg_date(self, new_date, num_words):
        msg_year = new_date.year
        msg_month = new_date.month
        msg_day = new_date.day
        msg_hr = new_date.hour
        pos = -1

        # If array empty, just append
        if len(self.msg_dates) == 0:
            self.msg_dates.append(new_date)
            self.msg_counts.append([1,0, num_words,0])
        else:
            # Look for if month/year combo already exists
            for ex_date in self.msg_dates:
                if ex_date.year == msg_year and ex_date.month == msg_month and ex_date.day == msg_day and ex_date.hour == msg_hr:
                    pos = self.msg_dates.index(ex_date)

            if pos != -1:
                self.msg_counts[pos][0] += 1
                self.msg_counts[pos][2] += num_words
            else:
                self.msg_dates.append(new_date)
                self.msg_counts.append([1,0,num_words,0])

    def get_dates(self):
        return self.msg_dates

    def get_counts(self):
        return self.msg_counts