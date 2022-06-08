from socket import *
from statistics import mean, stdev
import time
import sys

"""
existem 4 parâmetros possíveis para o argv, mas para manter a implementação simples, argv[2] depende que argv[1] exista, e assim por diante.
alguns exemplos de como rodar o programa com os argvs:

- python3 udp_client.py 127.0.0.1 -> usa somente um ip novo
- python3 udp_client.py 127.0.0.1 30000 -> usa um ip e um port novos
- python3 udp_client.py 127.0.0.1 30000 3 -> usa um ip, um port e limita o numero de pings
- python3 udp_client.py 127.0.0.1 30000 3 'mensagem aqui' -> usa um ip, um port, limita o numero de pings e permite modificar a mensagem enviada

caso esses parâmetros não sejam utilizados, os valores padrão são:
- ip: '127.0.0.1'
- port: 30000
- count: 10
- mensagem: ' - test message :)'
"""

# this checks if the received packet doesn't have 40 characters
# if req type is not '1'
# and if any of the payload sections is different from the received sections
def validate_received_message(payload, received):
	if len(received) != 40:
		return False

	validationList = [
		payload[0:5] == received[0:5],
		received[5:6] == '1',
		payload[6:10] == received[6:10],
		payload[10:40] == received[10:40]
	]

	# if at least one element is False, returns False
	return all(validationList)

def main():
	client_socket = socket(AF_INET, SOCK_DGRAM)
	client_socket.settimeout(1)

	ip = len(sys.argv) > 1 and sys.argv[1] or '127.0.0.1'
	port = len(sys.argv) > 2 and int(sys.argv[2]) or 30000
	ping_number = len(sys.argv) > 3 and int(sys.argv[3]) or 10
	message = len(sys.argv) > 4 and sys.argv[4] or ' - test message :)'

	sent_pkts = 0
	received_pkts = 0
	rtts = []
	total_time = 0

	print('PING ' + ip)
	total_time = time.time_ns()
	for i in range(ping_number):
		rtt = time.time_ns() # easier than handling 0.xxxx ms

		# pkt formatting
		id = str(i).rjust(5, '0')
		timestamp = str(int(rtt / 1000000) % 10000)
		msg = message.ljust(30, '\0')
		payload = id + '0' + timestamp + msg

		client_socket.sendto(payload.encode(), (ip, port))
		sent_pkts += 1

		try:
			data = client_socket.recvfrom(1024)[0]
			received = data.decode()
			received_id = int(received[0:5])
			payload_id = int(payload[0:5])

			# this makes the loop wait for the right received packet id
			while received_id != payload_id:
				data = client_socket.recvfrom(1024)[0]
				received = data.decode()
				received_id = int(received[0:5])

			rtt = time.time_ns() - rtt
			rtt = rtt / 1000000

			# see comment above function
			if not validate_received_message(payload, received):
				print('Invalid Payload')
				continue
			
			received_pkts += 1
			
			rtts.append(rtt)
			
			print(received)

		# if there's a timeout exception, we exit try block and go to here
		except timeout:
			print('Timed Out')

	total_time = time.time_ns() - total_time
	total_time = total_time / 1000000

	if received_pkts != 0:
		pkt_loss = 100 - received_pkts/sent_pkts*100
		rtt_min = min(rtts)
		rtt_avg = mean(rtts)
		rtt_max = max(rtts)
		rtt_stdev = stdev(rtts)

		print(f'\n--- {ip} ping statistics ---')
		print(str(sent_pkts) + ' packets transmitted')
		print(str(received_pkts) + ' packets received')
		print(str(pkt_loss) + '% packet loss')
		print('time ' + str(total_time) + ' ms')
		print('rtt min/avg/max/mdev')
		print(f'min {rtt_min:.4} ms')
		print(f'avg {rtt_avg:.4} ms')
		print(f'max {rtt_max:.4} ms')
		print(f'mdev {rtt_stdev:.4} ms')

if __name__ == "__main__":
    main()
