
from threading import Thread
import random
import time

agora = lambda: time.localtime()[3:6]
ftemp = lambda: '[%02d:%02d:%02d]' % agora() 

disp_id = 1

class Dispositivo:
	transmitindo = rodando = None
	esperando = False
	adiando = 5
	
	def transmitir (self, enviar = None):
		if self.transmitindo and not self.esperando:		
			if enviar == None:
				enviar = self.rede
			
			if enviar():
				print(ftemp(),'Máquina', self.id, self.nome, 'aguardando', enviar)
				return
			
			print(ftemp(), 'Máquina', self.id, self.nome, 'transmitindo', self.transmitindo[0], 'em', enviar)
			
			if enviar(agora(),(self.id,self.nome),self.transmitindo[0]):	
				if self.esperando != None:
					self.adiando <<= 1 + (self.adiando % 2)				
				self.esperando = random.randint(1, self.adiando)
				print(ftemp(),'\tColisão!',self.nome,self.id,'escolheu esperar',self.esperando, self.rodando)
			else:	
				if self.esperando == None:
					self.adiando >>= 1 - (self.adiando % 2)	
				self.esperando = None
				self.transmitindo.pop(0)
				
	
	def rodar (self, rede = None):
		while self.rodando:
			if self.esperando:
				self.esperando -= random.randint(0, 1)				
			else:	
				self.transmitir(rede)						
			for p in self.programas:	
				r = self.programas[p](self)
				if r != None:
					self.transmitindo.append(r)
					print(ftemp(),'\tPrograma',p,'na máquina',self.id,self.nome,'enviou',r)
		#	print(self.rodando)	
		#	self.esperando -= self.esperando > 0
			time.sleep(random.random() * 2 + 1)			
		print(ftemp(), '\tMáquina', self.id, self.nome, 'encerrada com status', self.rodando, self.esperando, self.transmitindo)	
		
		
	
	def iniciar (self, *local):
		print(ftemp(),'Iniciando máquina',self.id,self.nome,'\tStatus:',self.rodando, self.esperando)
		self.rodando = True
		return Thread(None,self.rodar,args=local)
		
	def encerrar (self):	
		print(ftemp(),'Encerrando máquina',self.id,self.nome,'\tStatus:',self.rodando, self.esperando,self.transmitindo)
		self.rodando = False 
			
		
	def __init__ (self, nome, num = None, rede = print):	
		
		if num == None:
			global disp_id
			num = disp_id
			disp_id += random.randint(1, num)
			
		self.id = num

		self.nome = str(nome)
		
		self.rede = rede
		
		self.transmitindo = []
		
		self.programas = {}
		
	def __call__ (self, *pacote):	
		if len(pacote):
			print(ftemp(),'\t', pacote, '\tchegou para', self.id, self.nome, 'em', self.rede, '\tStatus:', self.rodando, self.esperando)
		else:	
			print(ftemp(),'\tfoi', self.nome, self.id, 'que chamaram?')
			
	def __delitem__	(self, p):	
		if p in self.programas:
			self.programas.__delitem__(p)
			
	def __getitem__ (self, p): 		
		if p in self.programas:
			return self.programas[p]
			
	def __setitem__ (self, p, progr):		
		self.programas[p] = progr
		
	def __len__	(self):
		return len(self.programas)
		
class Rede:
	
	def __call__ (self, *dados):
		if self.ocupada or not len(dados):
			return self.ocupada
		c = 0	
		self.ocupada = id(dados)
		print(ftemp(), 'Rede ocupada por', self.ocupada)
		while self.ocupada == id(dados):				
			time.sleep(1 / (1 + c))
		#	print('.' if c % 5 else 'Conectando', end = '\n' * (c % 5 == 4))	
			c += 1 + int(2 * random.random())			
			if c > 2*(disp_id + len(self.dispositivos)): 				
				break
		else:
		#	self.ocupada = False
			return True
		self.ocupada = dados 
		Thread(None,self.concluir).start()
		 	
			
	def __init__ (self):		
		self.dispositivos = {}
		self.ocupada = None
		
	def __setitem__ (self, d, disp): 	
		self.dispositivos[d] = disp
		
	def __getitem__ (self, d):	
		if d in self.dispositivos:
			return self.dispositivos[d]
			
	def __delitem__ (self, d):		
		if d in self.dispositivos:
			self.dispositivos.__delitem__(d)
			
	def __len__	(self):
		return len(self.dispositivos)		
			
	def iniciar (self):		
		c = 0
		for d in self.dispositivos:
			try:
				self[d].iniciar(self).start()
				c += 1
			except AttributeError:	
				print(ftemp(), 'Máquina', d, self[d], 'inválida')
		print(ftemp(),c,'máquinas iniciadas')		
		return c

	def encerrar (self):	
		c = 0
		for d in self.dispositivos:
			try:
				self[d].encerrar()
				c += 1
			except AttributeError:	
				print(ftemp(), 'Máquina', d, self[d], 'inválida')
		print(ftemp(),c,'máquinas encerradas')		
		return c
	
	def concluir (self, m = 4):	
		time.sleep(random.random() * m)
		print(ftemp(),'Rede concluiu',self.ocupada)
		self.ocupada = None
		
rede = Rede()		
for c in range(100):
	n = hex(c)# + str(random.randint(0,c))
	d = Dispositivo(n)
	rede[n] = d
	while len(d) <= c:
		d[len(d) + c] = lambda x,y=c+len(d): (None,random.randint(-c,id(x)))[random.random() <= 1/(1 + y)]
rede.iniciar()		
time.sleep(10)
rede.encerrar()