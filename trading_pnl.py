'''
Analyzes trades that a hypothetical trading firm makes in some stocks and outputs paired trades.
No third party packages (numpy, pandas) are allowed. 
'''
import csv
import sys 

input_csv = sys.argv[1] 

# A single trade 
class Trade(object): 
	def __init__(self, time, symbol, side, price, quantity): 
		self.time = time 
		self.symbol = symbol
		self.side = side 
		self.price = price 
		self.quantity = quantity

class ClosedTrade(object):
	def __init__(self, open_time, close_time, symbol, quantity, pnl, open_side, close_side, open_price, close_price):
		self.open_time = open_time
		self.close_time = close_time
		self.symbol = symbol
		self.quantity = quantity
		self.pnl = pnl
		self.open_side = open_side
		self.close_side = close_side
		self.open_price = open_price
		self.close_price = close_price

	# For printing out the closed trades
	def __str__(self):
		return "{},{},{},{},{},{},{},{},{}".format(self.open_time, self.close_time, self.symbol, self.quantity, self.pnl, self.open_side, self.close_side, self.open_price, self.close_price)

def trade_pnl(input_file): 
	with open(input_file, 'rb') as csv_file: 
		next(csv_file)
		csv_reader = csv.reader(csv_file, delimiter = ',')
		line_count = 0 
		total_pnl = 0 

		# Array of Trade objects
		trade_list = [] 
		# Array of Closed Trade objects
		closed_trades = [] 

		for row in csv_reader:
			time, symbol, side, price, quantity = int(row[0]), row[1], row[2], float(row[3]), int(row[4])
	
			if trade_list == []: 
				trade_list.append(Trade(time,symbol,side,price,quantity))

			# Matching symbols, and reverse orders 
			if trade_list[0].symbol == symbol and trade_list[0].side != side: 

				# CLOSING ORDER IS CLOSED AND MATCHED 
				if trade_list[0].quantity >= quantity: 
					total_pnl += abs(price*quantity - trade_list[0].price*quantity)
					trade_list[0].quantity -= quantity

					# Adding result to closed_trade list 
					closed_trades.append(ClosedTrade(trade_list[0].time, time, symbol, quantity, abs(price*quantity - trade_list[0].price*quantity), trade_list[0].side, side, trade_list[0].price, price))

					if trade_list[0].quantity == 0:
						del trade_list[0]

				# CLOSING ORDER IS BIGGER THAN OPENING ORDER 
				elif trade_list[0].quantity < quantity: 
					total_pnl += abs(trade_list[0].price*trade_list[0].quantity - price*trade_list[0].quantity)
					quantity -= trade_list[0].quantity

					closed_trades.append(ClosedTrade(trade_list[0].time, time, symbol, trade_list[0].quantity, abs(trade_list[0].price*trade_list[0].quantity - price*trade_list[0].quantity), trade_list[0].side, side, trade_list[0].price, price))
					del trade_list[0]

					for open_trade in trade_list: 
						if open_trade.symbol == symbol: 
							# CLOSING TRADE IS FINALLY MATCHED 
							if quantity <= open_trade.quantity: 
								total_pnl += abs(price*quantity - open_trade.price*quantity)
								open_trade.quantity -= quantity 

								# Adding result to the closed_trade list 
								closed_trades.append(ClosedTrade(open_trade.time, time, symbol, quantity, abs(price*quantity - open_trade.price*quantity), open_trade.side, side, open_trade.price, price))
								if open_trade.quantity == 0: 
									trade_list.remove(open_trade)
									break
							# CLOSING TRADE REMAINS UNMATCHED
							else: 
								total_pnl += abs(open_trade.price*open_trade.quantity - price*open_trade.quantity)
								quantity -= open_trade.quantity
								trade_list.remove(open_trade)
								continue 
						else: 
							continue 

					# CLOSING ORDER IS BIGGER THAN ENTIRE INVENTORY 
					if quantity > 0: 
						trade_list.append(Trade(time,symbol,side,price,quantity))
				
			else:
				trade_list.append(Trade(time,symbol,side,price,quantity))

				# Sorting for efficiency every 25000 lines
				# This is useful when a closing trade is not match the first time 
				if line_count > 25000: 
					trade_list = sorted(trade_list, key=lambda x: (x.symbol,x.symbol))
					line_count = 0
				else: 
					line_count = line_count + 1 

	# Printing out closed trades
	for x in closed_trades: 
		print x
	return total_pnl


if __name__ == "__main__":
	print "OPEN_TIME,CLOSE_TIME,SYMBOL,QUANTITY,PNL,OPEN_SIDE,CLOSE_SIDE,OPEN_PRICE,CLOSE_PRICE" 
	print(trade_pnl(input_csv))
