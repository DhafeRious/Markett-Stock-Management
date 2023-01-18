#!/usr/bin/env python3


import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext as  stxt
from tkinter.simpledialog import askstring

import os
import csv
import sqlite3
from datetime import date,datetime

import os
if os.name == "nt":
	from ctypes import windll, pointer, wintypes
	try:
		windll.shcore.SetProcessDpiAwareness(1)
	except Exception:
		pass
__appname__ = "Gestion de stock"
__version__  = "1.0"

class ItemOut(tk.Toplevel):

	def __init__(self,root):
	
		tk.Toplevel.__init__(self)
		self.root=root
		self.validee=False
		self.newcom = True
		self.state('zoomed')
		# Set the window title.
		self.title('Gestion des ventes')
		self.type="vente"
		# This protocol is used to call the method self.quitApp
		# for exiting the application in proper way and to make
		# sure that the database has been closed.
		self.protocol('WM_DELETE_WINDOW', self.quitApp)
		self.style = ttk.Style()
		self.style.layout("TEntry",
                   [(
					   'Entry.field', {'sticky': 'nswe', 'border': '1', 'children': [(
					   'Entry.highlight', {'sticky': 'nswe', 'children': [(
					   'Entry.backgroud', {'sticky': 'nswe','border': '1', 'children': [(
					   'Entry.padding', {'sticky': 'nswe', 'children': [(
					   'Entry.textarea', {'sticky': 'nswe'})]})]})]})]})])
		self.style.configure("TEntry",
                 fieldbackground="white")
		self.style.layout("Q.TEntry",
                   [('Entry.plain.field', {'children': [(
                     'Entry.background', {'children': [(
                     'Entry.padding', {'children': [(
                     'Entry.textarea', {'sticky': 'nswe'})],
					 'sticky': 'nswe'})], 'sticky': 'nswe'})],
					 'border':'1', 'sticky': 'nswe'})])
		self.style.configure("Q.TEntry",
                 fieldbackground="white")
		# Set the window icon.
		self.iconlocation = os.getcwd() + "/tsicon.ico"
		try:
			self.iconbitmap(self.iconlocation)
		except:
			pass

		# Initialize the database and the cursor.
		self.database = sqlite3.connect('quinc.db')
		self.cur = self.database.cursor()

		# Create menu bar of the main window.
		self.menubar = tk.Menu(self)
		self.config(menu=self.menubar)
		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.aboutmenu = tk.Menu(self.menubar, tearoff=0)
		self.optionmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='Fichier', menu=self.filemenu)
		self.menubar.add_cascade(label='Options', menu=self.optionmenu)
		self.menubar.add_cascade(label='About', menu=self.aboutmenu)
		self.filemenu.add_command(label='Quit', command=self.quitApp)
		self.aboutmenu.add_command(label='About', command='')
		self.optionmenu.add_command(label='Nouveau commande', command=self.newCmd)
		self.optionmenu.add_command(label='Annuler commande', command=self.cancelCmd)
		
		# Add to labelframe for select item and insert item.
		self.selectframe = ttk.LabelFrame(self, text="Liste d'articles",width=200)
		self.selectframe.propagate(False)
		self.selectframe.grid(row=0, column=0, sticky='wens',rowspan=2)
		self.insertframe = ttk.LabelFrame(self, text='Sortie stock')
		self.insertframe.grid(row=0, column=1, sticky='wens')
		self.displayframe = ttk.LabelFrame(self, text='Details')
		self.displayframe.grid(row=1, column=1, sticky='wens')
		# Add a ttk treeview for the display of transaction.
		self.treeview = ttk.Treeview(self.displayframe)
		self.treeview.grid(row=0, column=0, sticky='wens',rowspan=10)
		self.treeview.bind('<ButtonRelease-1>', self.selectTree)
		self.disyscroll = tk.Scrollbar(self.displayframe,
									   command=self.treeview.yview)
		self.disyscroll.grid(row=0, column=1, sticky='wns',rowspan=10)
		self.treeview.config(yscrollcommand=self.disyscroll.set)
		
		self.column = ('Ref',
					   'Designation',
					   'Quantité', 'prix',
					   'Remise',
					   'Montant')
		self.heading = ('Réf',
					   'Designation',
					   'Quantité', 'prix',
					   'Remise (%)',
					   'Montant (DT)')
		self.treeview['columns'] = self.column
		for elem in self.column:
			if elem == 'Ref':
				col_width = 100
			elif elem == 'Designation':
				col_width = 250
			elif elem == 'prix':
				col_width = 100			
			elif elem == 'Quantité':
				col_width = 100
			elif elem == 'Remise':
				col_width = 100
			else:
				col_width = 100

			if elem == 'Montant':
				self.treeview.column(elem,anchor="c", width=col_width)
			else:
				self.treeview.column(elem,anchor="c", width=col_width, stretch=False)

		counter = 0
		self.treeview.heading('#0', text='S. No.')
		self.treeview.column('#0', width=50, stretch=False)
		for elem in self.column:
			self.treeview.heading(elem, text=self.heading[counter])
			counter += 1
		# Create tags for treeview.
		self.treeview.tag_configure('evenrow', background='#d5d5d5')
		self.treeview.tag_configure('oddrow', background='#f7f7f7')



		# Create and add a list box and a entry inside selectframe.
		self.searchCbx = ttk.Combobox(self.selectframe, values=('Référence','Designation'),state='readonly')
		self.searchCbx.set("Designation")
		self.searchCbx.grid(row=0, column=0, sticky='we',rowspan=1)
		self.searchby = {'Référence':'ref','Designation':'Designation'}
		self.searchCbx.bind("<<ComboboxSelected>>", self.searchList)
		self.dt = None
		self.searchentry = ttk.Entry(self.selectframe)
		self.searchentry.grid(row=1, column=0, sticky='we',rowspan=1)
		self.searchentry.bind('<KeyPress>', self.searchList)
		self.itemlistbox = tk.Listbox(self.selectframe, width = 60)
		self.itemlistbox.grid(row=2, column=0, sticky='wens',rowspan=18)
		self.yscroll = tk.Scrollbar(self.selectframe,
									command=self.itemlistbox.yview)
		self.yscroll.grid(row=2, column=1, sticky='ns',rowspan=18)
		self.itemlistbox.config(yscrollcommand=self.yscroll.set)
		self.itemlistbox.bind('<<ListboxSelect>>', self.selectList)

		# Insert item list into the listbox.
		self.refreshList()

		# Create labels inside the insert frame.
		self.date_label = ttk.Label(self.insertframe, text='Date:')
		self.date_label.grid(row=0, column=10, sticky='w',columnspan=3)	
		self.client_label = ttk.Label(self.insertframe, text='Client:')
		self.client_label.grid(row=1, column=10, sticky='w',columnspan=3)		
		self.numcmd_label = ttk.Label(self.insertframe, text='N° Commande:')
		self.numcmd_label.grid(row=0, column=0, sticky='w',columnspan=3)
		self.itemcode_label = ttk.Label(self.insertframe, text='Référence:')
		self.itemcode_label.grid(row=1, column=0, sticky='w')
		self.descp_label = ttk.Label(self.insertframe, text='Description:')
		self.descp_label.grid(row=2, column=0, sticky='wns')
		self.prix_label = ttk.Label(self.insertframe, text='prix:')
		self.prix_label.grid(row=5, column=0, sticky='w')
		self.quantity_label = ttk.Label(self.insertframe, text='Quantité en stock:')
		self.quantity_label.grid(row=6, column=0, sticky='w')
		
		self.qtd_label = ttk.Label(self.insertframe, text='Quantité demandée:')
		self.qtd_label.grid(row=2, column=10, sticky='w')
		self.remise_label = ttk.Label(self.insertframe, text='Remise (%)')
		self.remise_label.grid(row=4, column=10, sticky='w')
		self.total_label = ttk.Label(self.insertframe, text='Total (DT):')
		self.total_label.grid(row=6, column=10, sticky='w')
		# Create entries inside the insert frame.
		self.date_entry = ttk.Entry(self.insertframe,state='readonly',justify="center")
		self.date_entry.grid(row=0, column=11, sticky='w',pady=5)
		self.client_entry = ttk.Entry(self.insertframe,justify="center")
		self.client_entry.grid(row=1, column=11, sticky='w',pady=5)
		self.client_entry.bind('<Return>',self.updateDetails)		
		self.numcmd_entry = tk.Entry(self.insertframe,justify="center")
		self.numcmd_entry.grid(row=0, column=1, sticky='w',pady=5)
		self.numcmd_entry.bind('<Return>',self.getCmdList)

		self.ref_entry = ttk.Entry(self.insertframe,state='readonly',justify="center")
		self.ref_entry.grid(row=1, column=1, sticky='w',pady=5)
		self.desc_entry = tk.Text(self.insertframe,height =2,width=30,state='disabled',wrap='word')
		self.desc_entry.grid(row=2, column=1, sticky='wns',pady=5,rowspan=3,columnspan=8)
		self.prix_entry = ttk.Entry(self.insertframe, width=20,state='readonly',justify="center")
		self.prix_entry.grid(row=5, column=1, sticky='w',pady=5)
		self.quantity_entry = ttk.Entry(self.insertframe, width=20,state='readonly',justify="center",style="Q.TEntry" )
		self.quantity_entry.grid(row=6, column=1, sticky='w',pady=5)
		
		self.qtd_entry = ttk.Entry(self.insertframe, width=20,justify="center")
		self.qtd_entry.bind("<Key>", self.onValidate)
		self.qtd_entry.grid(row=2, column=11, sticky='w',pady=5)
		self.remise_entry = ttk.Entry(self.insertframe, width=20,justify="center",text="0")
		self.remise_entry.grid(row=4, column=11, sticky='w',pady=5)
		self.total_entry = ttk.Entry(self.insertframe, width=20,justify="center")
		self.total_entry.grid(row=6, column=11, sticky='w',pady=5)
		self.remise_entry.delete('0','end')
		self.remise_entry.insert('0','10')
		self.total_entry.delete('0','end')
		self.total_entry.insert('0','0')
		self.qtd_entry.bind('<Return>',self.addtoTreeView)
		self.remise_entry.bind('<Return>',self.addtoTreeView)
		self.remise_entry.bind('<Key>',self.onValidateRms)
		self.lstEnt = [self.ref_entry,self.prix_entry,self.quantity_entry]
		# Create cancel save button
				# Add a delete and edit button for under tree view for
		# database manipulation and editing.
		self.getcmd_btn = tk.Button(self.insertframe, text='LISTE DES COMMANDES',command=self.showSearchWin,height=1)
		self.getcmd_btn.grid(row=0, column=2, sticky='w',pady=5)
		self.nouv_btn = ttk.Button(self.displayframe,text='Nouveau',command=self.newCmd)
		self.nouv_btn.grid(row=6, column=2, sticky='we',padx=20,pady=5)
		self.delete_btn = ttk.Button(self.displayframe, text='Supprimer',command=self.deleteItemTreeView)
		self.delete_btn.grid(row=5, column=2,sticky='we',padx=20,pady=5)
		self.edit_btn = ttk.Button(self.displayframe, text='Ajout/Mod',command= self.addtoTreeView)
		self.edit_btn.grid(row=4, column=2,sticky='we',padx=20,pady=5)
		self.cancel_btn = ttk.Button(self.displayframe,text='Annuler',command=self.cancelCmd )
		self.cancel_btn.grid(row=8, column=2, sticky='we',padx=20,pady=5)
		self.val_btn = tk.Button(self.insertframe,text='Valider',command=self.validateCmd,bg='#15d900')
		self.val_btn.grid(row=6, column=12, sticky='we',padx=5)		
		self.print_btn = tk.Button(self.insertframe,text='Imprimer',command=self.printFact,bg='#158aff')
		self.print_btn.grid(row=6, column=13, sticky='we',padx=5)

		# Insert today's date.
		today = datetime.strftime(datetime.now(),'%y-%m-%d %H:%M')
		self.date_entry.configure(state='normal')
		self.date_entry.insert(0, today)
		self.date_entry.configure(state='readonly')
		ncmd = datetime.strftime(datetime.now(),'%y%m%d%H%M%S')
		self.numcmd_entry.insert(0, ncmd)
		self.ref_entry.focus_set()
		for x in range(2):
			self.grid_rowconfigure(x, weight=1)
		self.grid_columnconfigure(1, weight=1)
		for x in range(20):
			self.selectframe.grid_rowconfigure(x, weight=1)
		for x in range(1):
			self.selectframe.grid_columnconfigure(x, weight=1)
		for x in range(8):
			self.insertframe.grid_rowconfigure(x, weight=1)
		for x in range(20):
			self.insertframe.grid_columnconfigure(x, weight=1)
		for x in range(10):
			self.displayframe.grid_rowconfigure(x, weight=1)
		for x in range(1):
			self.displayframe.grid_columnconfigure(x, weight=1)
	def selectTree(self,event):
		curItem = self.treeview.focus()
		row = self.treeview.item(curItem)['values']
		if row !='':
			code,_,qtd,_,rms,_ = row
			for w in self.lstEnt :
				w.configure(state='normal')
			self.desc_entry.configure(state='normal')
			self.style.configure('Q.TEntry', fieldbackground='white')		
			for d in self.dt:
				if d[0] == str(code) :
					row = d
					break

			self.desc_entry.configure(state='normal')
			self.ref_entry.delete('0', 'end')
			self.desc_entry.delete('1.0', 'end')
			self.prix_entry.delete('0', 'end')
			self.quantity_entry.delete('0', 'end')
			self.qtd_entry.delete('0', 'end')
			self.remise_entry.delete('0', 'end')
			
			self.ref_entry.insert('end', str(row[0]))
			self.desc_entry.insert('end', str(row[1]))
			self.prix_entry.insert('end', str(row[2]))
			self.quantity_entry.insert('end', str(row[3]))
			self.qtd_entry.insert('end',str(qtd))
			self.remise_entry.insert('end',str(rms))
			if row[3] == 0 :
				self.style.configure('Q.TEntry', fieldbackground='yellow')	
			else: 
				self.style.configure('Q.TEntry', fieldbackground='white')		

			for w in self.lstEnt :
				w.configure(state='readonly')
			self.desc_entry.configure(state='disabled')
	def selectList(self, event):
		try : 
			crt = self.itemlistbox.curselection()[0]
		except :
			return False
			
		for w in self.lstEnt :
			w.configure(state='normal')
		self.desc_entry.configure(state='normal')
		self.ref_entry.delete("0", 'end')
		self.desc_entry.delete('1.0',tk.END)
		self.prix_entry.delete("0", 'end')
		self.quantity_entry.delete("0", 'end')
		self.qtd_entry.delete('0', 'end')
		self.remise_entry.delete('0', 'end')
		self.remise_entry.insert('0','10')
		self.ref_entry.insert('end', str(self.dt[crt][0]))
		self.desc_entry.insert('end', str(self.dt[crt][1]))
		self.prix_entry.insert('end', str(self.dt[crt][2]))
		self.quantity_entry.insert('end', str(self.dt[crt][3]))
		if str(self.dt[crt][3])=='0':
			self.style.configure('Q.TEntry', fieldbackground='yellow')
		else:
			self.style.configure('Q.TEntry', fieldbackground='white')		
		for w in self.lstEnt :
			w.configure(state='readonly')
		self.desc_entry.configure(state='disabled')
		

	def deleteItemTreeView(self):
		if not self.validee :
			curItem = self.treeview.focus()
			if curItem !='':
				q1 = self.cur.execute("Select count(*) FROM commande where idcmd= ?",(self.numcmd_entry.get(),))
				data1 = q1.fetchall()[0][0]
				if data1 :
					self.cur.execute("delete from vente where idcmd= ? and idprod= ?",(self.numcmd_entry.get(),self.ref_entry.get(),))
					try:
						self.database.commit()
					except sqlite3.Error:
						self.database.rollback()
						tk.messagebox.showwarning('avertissement', "un erreur s'est produit", parent=self.master)
				self.treeview.delete(curItem)
				self.refreshList()
				self.clearFields()
				self.redrawTree()
		else :
			tk.messagebox.showwarning('avertissement', "Commande validée", parent=self.master)

	def redrawTree(self):
		listPrd = self.treeview.get_children()
		cnt=1
		for r in listPrd:
			if cnt % 2 == 0:
				self.treeview.item(str(r),text=cnt,tag=("oddrow",))
			else:
				self.treeview.item(str(r),text=cnt,tag=("evenrow",))
			cnt+=1
	def addtoTreeView(self,event=None):

		if self.remise_entry.get()== '' or self.qtd_entry.get()== '' or self.quantity_entry.get()== '0':
			return False
		if not self.validee :
			
			row =[self.ref_entry.get(),self.desc_entry.get('1.0','end'),self.qtd_entry.get(),self.prix_entry.get(),self.remise_entry.get()]
			mnt = ((float(row[2]) * float(row[3])) * (100.0 - float(row[4]))/100.0)/1000.0
			listPrd = self.treeview.get_children()
			rowid=None
			if self.checkremise():
				if self.newcom :
					self.cur.execute("insert into commande values(?,?,null,?)",(self.numcmd_entry.get(),self.date_entry.get(),self.client_entry.get(),))
					
				for r in listPrd:
					if str(self.treeview.item(r)['values'][0]) == self.ref_entry.get() :
						rowid=self.treeview.item(r)['text']
						q = int(self.treeview.item(r)['values'][2])
						break
				if rowid == None : 
					if len(listPrd) != 0:
						child = self.treeview.get_children()
						rowid = int(self.treeview.item(child[-1])['text'])+1
					else:
						rowid = 1
					if rowid % 2 == 0 :
						tg = 'evenrow'
					else:
						tg = 'oddrow'

					self.cur.execute("insert into vente values(null,?,?,?,?)",(row[2],row[4],row[0],self.numcmd_entry.get(),))
					self.treeview.insert('', 'end', str(rowid), text=str(rowid), tag=(tg,))

				else:
					self.cur.execute("update vente set quantite=?, remise = ? where idcmd = ? and idprod = ?",(row[2],row[4],self.numcmd_entry.get(),row[0],))
				self.cur.execute("update commande set client=? where idcmd = ?",(self.client_entry.get(),self.numcmd_entry.get(),))
				try:
					self.database.commit()
					self.newcom = False
					self.refreshList()
				except sqlite3.Error:
					self.database.rollback() 
					tk.messagebox.showwarning('avertissement', "un erreur s'est produit", parent=self.master)

				self.treeview.set(str(rowid), self.column[0], str(row[0]))
				self.treeview.set(str(rowid), self.column[1], str(row[1]))
				self.treeview.set(str(rowid), self.column[2], str(row[2]))
				self.treeview.set(str(rowid), self.column[3], str(row[3]))
				self.treeview.set(str(rowid), self.column[4], str(row[4]))
				self.treeview.set(str(rowid), self.column[5], tl.convert(str(mnt)))
				self.calculTotal()
				self.clearFields()
			else:
				tk.messagebox.showwarning('avertissement', "Vérifier le Remise")
			
		
	
	def validateCmd(self):
		if self.validee :
			tk.messagebox.showinfo('Info', "Commande déjà validée", parent=self.master)
			return False
		if not self.newcom :
			if not self.isFullStock():
				tk.messagebox.showinfo('Info', "Stock insuffisant", parent=self.master)
				return False
		listPrd = self.treeview.get_children()
		if len(listPrd) == 0 :
			tk.messagebox.showwarning('Info', "Liste vide", parent=self.master)
			return False
		if messagebox.askyesno("Confirmation", "Valider cette commande?"):
			if not self.newcom:
						self.cur.execute("update commande set validee=1 ,date = ?,client = ? where idcmd = ?",('{}'.format(self.date_entry.get()),'{}'.format(self.client_entry.get()),self.numcmd_entry.get(),))
						for r in listPrd:
							q = int(self.treeview.item(r)['values'][2])
							ref = str(self.treeview.item(r)['values'][0])
							self.cur.execute("update produit set quantite = quantite - ? where ref = ?",(q,ref,))
							
			else:
				self.cur.execute("insert into commande values(?,?,1,?)",(self.numcmd_entry.get(),self.date_entry.get(),self.client_entry.get(),))
				for r in listPrd:
					row = [self.treeview.item(r)['values'][2],self.treeview.item(r)['values'][4],self.treeview.item(r)['values'][0],self.numcmd_entry.get()]
					self.cur.execute("insert into vente values(null,?,?,?,?)",(row[0],row[1],row[2],row[3],))
					self.cur.execute("update produit set quantite = quantite - ? where ref = ?",(row[0],row[2],))

			try:
				self.database.commit()
				tk.messagebox.showinfo('Info', "Commande validée", parent=self.master)
				self.newcom = False
				self.validee=True
				self.numcmd_entry.configure(bg='#80ff00')
				self.refreshList()
			except sqlite3.Error:
				self.database.rollback()
				tk.messagebox.showwarning('avertissement', "un erreur s'est produit", parent=self.master)
	def searchList(self, event):
		x = self.searchby[self.searchCbx.get()]
		item = self.searchentry.get()
		if event.char.isalpha() or event.char.isnumeric():
			item +=  str(event.char)
		if event.keysym == 'BackSpace':
			item = item[:-1]
		self.dt = None
		self.itemlistbox.delete('0', 'end')
		if item != '' :
			model = "SELECT ref,designation,pvente,quantite FROM produit WHERE " + x + " like ?"
			dataquery = self.cur.execute(model, ('{}%'.format(item),))
		else:
			model = "SELECT ref,designation,pvente,quantite FROM produit "
			dataquery = self.cur.execute(model)
		self.dt = dataquery.fetchall()
		for data in self.dt:
			self.itemlistbox.insert('end', data[self.searchCbx.current()])

	def refreshList(self):
		# Insert item list into the listbox.
		self.itemlistbox.delete('0', 'end')
		dataquery = self.cur.execute("Select ref,designation,pvente,quantite FROM produit")
		self.dt = dataquery.fetchall()
		for row in self.dt:
			self.itemlistbox.insert('end', row[self.searchCbx.current()])
	def checkremise(self):
		q2=self.cur.execute("SELECT pvente,pachat FROM produit WHERE ref= ?",(self.ref_entry.get(),))
		data2=q2.fetchall()
		valapresrem=((1-(float(self.remise_entry.get())/100))*data2[0][0])
		if valapresrem>data2[0][1]:
			rslt=True
		else:
			rslt=False
		return rslt		
	def getCmdList(self,event=None):
	
		self.clearFields()
		ncmd = str(self.numcmd_entry.get())
		data = self.cur.execute("SELECT p.ref,p.designation,v.quantite, p.pvente,v.remise,c.client,c.validee FROM vente v,produit p,commande c WHERE v.idcmd = ? AND v.idprod = p.ref and c.idcmd=v.idcmd;",(ncmd,))
		rows = data.fetchall()
		
		if len(rows):
			self.client_entry.delete('0','end')
			self.client_entry.insert('0',rows[0][5])
			self.newcom = False
			if rows[0][6] == 1:
				self.validee= True
				self.numcmd_entry.configure(bg='#80ff00')
			else:
				self.validee= False
				self.numcmd_entry.configure(bg='white')
				
			for item in self.treeview.get_children():
				self.treeview.delete(item)

			counter = 1
			
			for row in rows:

				if counter % 2 == 0:
					self.treeview.insert('', 'end', str(counter), text=str(counter), tag=('evenrow',))
				else:
					self.treeview.insert('', 'end', str(counter), text=str(counter), tag=('oddrow',))
				mnt = ((float(row[2]) * float(row[3])) * (100.0 - float(row[4]))/100.0)/1000.0
				self.treeview.set(str(counter), self.column[0], str(row[0]))
				self.treeview.set(str(counter), self.column[1], str(row[1]))
				self.treeview.set(str(counter), self.column[2], str(row[2]))
				self.treeview.set(str(counter), self.column[3], str(row[3]))
				self.treeview.set(str(counter), self.column[4], str(row[4]))
				self.treeview.set(str(counter), self.column[5], tl.convert(str(mnt)))
				counter += 1
			self.calculTotal()

	def isFullStock(self):
		ncmd = str(self.numcmd_entry.get())
		data = self.cur.execute("SELECT p.quantite,v.quantite FROM vente v,produit p,commande c WHERE v.idcmd = ? AND v.idprod = p.ref and c.idcmd=v.idcmd;",(ncmd,))
		rows = data.fetchall()
		v= True
		for r in rows :
			if float(r[0]) < float(r[1]) :
				v = False
				break
		return v
	def quitApp(self):
		# Check first if the database is open, if so close it.
		if self.database:
			try: 
				self.database.commit()
			except sqlite3.Error:
				self.database.rollback()
			self.cur.close()
			self.database.close()
		self.root.update()
		self.root.deiconify()
		self.root.state("zoomed")
		self.destroy()
	def cancelCmd(self):
		if messagebox.askyesno("Confirmation", "Annuler cette commande?"):
			try:
				self.cur.execute("delete from vente where idcmd = ?",(self.numcmd_entry.get(),))
				self.cur.execute("delete from commande where idcmd = ?",(self.numcmd_entry.get(),))
				if self.validee:
					for r in self.treeview.get_children():
						q= self.treeview.item(r)['values'][2]
						ref= self.treeview.item(r)['values'][0]
						self.cur.execute("update produit set quantite = quantite + ? where ref = ?",(q,ref,))

				self.database.commit()
				self.newCmd()
				self.refreshList()
			except sqlite3.Error:
				self.database.rollback()
				tk.messagebox.showwarning('avertissement', "un erreur s'est produit", parent=self.master)

	def newCmd(self):
		self.validee = False
		self.newcom = True
		self.numcmd_entry.configure(bg='white')
		ncmd = datetime.strftime(datetime.now(),'%y%m%d%H%M%S')
		self.numcmd_entry.delete('0','end')
		self.numcmd_entry.insert('0', ncmd)
		self.clearFields()
		self.client_entry.delete('0','end')
		self.total_entry.delete('0','end')
		if len(self.treeview.get_children()) != 0:
			child = self.treeview.get_children()
			for item in child:
				self.treeview.delete(item)
	def updateDetails(self,event):
		try:
			q1 = self.cur.execute("Select count(*) FROM commande where idcmd= ?",(self.numcmd_entry.get(),))
			data1 = q1.fetchall()
			if data1[0][0]:
				self.cur.execute("update commande set client=?, date = ? where idcmd = ?",(self.client_entry.get(),"{}".format(self.date_entry.get()),self.numcmd_entry.get(),))
				tk.messagebox.showinfo('info',"Le nom du client a été modifié")
				self.database.commit()
		except sqlite3.Error:
			self.database.rollback()
			tk.messagebox.showwarning('avertissement', "un erreur s'est produit", parent=self.master)
	def showSearchWin(self):
		SearchCmd(self,self.numcmd_entry)
	def clearFields(self):
		self.style.configure('Q.TEntry', fieldbackground='white')		
		for w in self.lstEnt :
			w.configure(state='normal')
		self.desc_entry.configure(state='normal')
		self.ref_entry.delete('0', 'end')
		self.desc_entry.delete('1.0', 'end')
		self.prix_entry.delete('0', 'end')
		self.quantity_entry.delete('0', 'end')
		self.qtd_entry.delete('0', 'end')
		self.remise_entry.delete('0', 'end')
		self.remise_entry.insert('0','10')
		for w in self.lstEnt :
			w.configure(state='readonly')
		self.desc_entry.configure(state='disabled')
	def calculTotal(self):
		lst = self.treeview.get_children()
		if len(lst):
			s=0.0
			for r in lst : 
				s += float(tl.reconvert(self.treeview.item(r)['values'][5]))
			self.total_entry.delete('0','end')
			self.total_entry.insert('0',tl.convert(round(s,3)))
	def onValidate(self,event):
			if event.keysym == 'Tab':
				return 'Tab'
			qs = self.quantity_entry.get()
			S = self.qtd_entry.get()
			if qs != '':
				if event.char.isnumeric() :
					S += event.char
					if float(S) > float(qs):
						return "break"
				elif event.char != "" and event.char!="\x08":
					return "break"
			else:
				return "break"
	def onValidateRms(self,event):
		if event.keysym == 'Tab':
			return 'Tab'
		S = self.remise_entry.get()
	
		if event.char.isnumeric() or event.char =='.' :
			S += event.char
			if float(S) > 100:
				return "break"
		elif event.char != "" and event.char!="\x08":
			return "break"
	
	def printFact(self):
		import webbrowser
		if self.validee :
			cmd = 'FACTURE'
		else:
			cmd='DEVIS'
		html_str = """
		 <!DOCTYPE html>
		<html
		<head>
		<title>Bon d'entrée</title>
		</head>
		<style>
		body {
		margin:0;
		padding:0;
		height:100%;
		}
		body {
		padding:10px;
		padding-bottom:60px;­ /* Height of the footer */
		}
		footer {
		bottom:0;
		width:100%;
		height:60px; /* Height of the footer */
		background:#6cf;
		}

		table {
			width:90%;
		}
		table, th, td {
			border: 0px solid black;
			border-collapse: collapse;
		}
		.border {
			border: 1px solid black;
			border-collapse: collapse;
		}
		.border1 {
			border: 1px solid black;
			border-collapse: collapse;
			font-weight:bold
			}
		th, td {
			padding: 15px;
			text-align: center;
		}
		.tr1 {
			background-color: white;
		}
		
		table tr:nth-child(even) {
			background-color: #eee;
		}
		table tr:nth-child(odd) {
		   background-color: #fff;
		}
		table th {
			background-color: #797979;
			color: white;
		}
		.fixed {
                position: fixed;
                bottom: 0;
                right: 0;
                width: 300px;
                border: 3px solid #73AD21;
}
		</style>
		<body>
		<div style="padding:5px; width:45%; margin:30px 0 0 0;margin-left:5%; border:2px solid #b1b1ce; background-color:#efeff5;
		-moz-border-radius:20px; -khtml-border-radius:20px; -webkit-border-radius:20px; border-radius:20px;">
		
		<h2 align="center" > Quincaillerie Générale </h2>
		<h2 align="center" > Ramy Mlawah </h2>
		<h3 align="center" >DATE & HEURE : """ + str(self.date_entry.get()) + """</h3>
                </div>
                <div style="padding:5px; width:45%; margin:0 0 0 49%; border:2px solid #b1b1ce; background-color:#d0d0e1;
		-moz-border-radius:20px; -khtml-border-radius:20px; -webkit-border-radius:20px; border-radius:20px;">
                <h2 align="center" >"""+ cmd + """ N° """ + self.numcmd_entry.get() + """</h2>
                <h3 align="center" >CLIENT : """ + str(self.client_entry.get()) + """</h3>
                </div>
		<table border=1 align="center">
			 <tr>
			   <th class="border"> N° </th>
			   <th class="border">Référence</th>
			   <th class="border">Désignation</th>
			   <th class="border">Quantité</th>
			   <th class="border">Prix</th>
			   <th class="border">Remise</th>
			   <th class="border">Montant (DT)</th>
			 </tr>
			 <indent>
		"""
		listPrd = self.treeview.get_children()
		sum=0
		for r in listPrd:
			row = [self.treeview.item(r)['text'],self.treeview.item(r)['values'][0],self.treeview.item(r)['values'][1],
                               self.treeview.item(r)['values'][2],self.treeview.item(r)['values'][3],self.treeview.item(r)['values'][4],
                               self.treeview.item(r)['values'][5]]
			mnt = tl.reconvert(self.treeview.item(r)['values'][5])
			sum+=float(mnt)
			html_str += "<tr >"
			for i in row :
				html_str += "<td class='border'>" + str(i) + "</td>"
			html_str += "</tr>"
		html_str += """<tr class=tr1><td></td><td></td><td></td><td></td><td></td><td class="border1"> TOTAL </td><td class="border1">""" + tl.convert(round(sum,3)) + """</td></tr>
		</table>
		
		<footer>
		<div style="padding:3px; padding-left:6px; border-left:4px solid #d0d0d0; background-color:#f1f1f1; margin-left:5%;width:89%;bottom:5px;",class="footer">
		QUINCAILLERIE RAMI MLAWAH <br>
		Rue Farhat Hached <br>
		Bir Mcherga - Zaghouan <br>
                Mobile: 23 898 013<br>
                </div>
        </footer>
        </body>
		</html>
		
		"""

		Html_file= open("filename.html","w")
		Html_file.write(html_str)
		Html_file.close()
		webbrowser.open("filename.html");

class ItemIn(tk.Toplevel):

	def __init__(self,root,type="achat"):
	
		tk.Toplevel.__init__(self)
		self.root=root
		self.type= type
		self.validee=False
		self.state('zoomed')
		if self.type=="achat" :
			self.prix = "pachat"
			self.table = "achat"
			self.title('Achat')
		else : 
			self.prix = "pvente"
			self.table = "retour"
			self.title('Retour')
		# This protocol is used to call the method self.quitApp
		# for exiting the application in proper way and to make
		# sure that the database has been closed.
		self.protocol('WM_DELETE_WINDOW', self.quitApp)
		self.style = ttk.Style()
		self.style.layout("TEntry",
                   [(
					   'Entry.field', {'sticky': 'nswe', 'border': '1', 'children': [(
					   'Entry.highlight', {'sticky': 'nswe', 'children': [(
					   'Entry.backgroud', {'sticky': 'nswe','border': '1', 'children': [(
					   'Entry.padding', {'sticky': 'nswe', 'children': [(
					   'Entry.textarea', {'sticky': 'nswe'})]})]})]})]})])
		self.style.configure("TEntry",
                 fieldbackground="white")
		self.style.layout("Q.TEntry",
                   [('Entry.plain.field', {'children': [(
                     'Entry.background', {'children': [(
                     'Entry.padding', {'children': [(
                     'Entry.textarea', {'sticky': 'nswe'})],
					 'sticky': 'nswe'})], 'sticky': 'nswe'})],
					 'border':'1', 'sticky': 'nswe'})])
		self.style.configure("Q.TEntry",
                 fieldbackground="white")
		# Set the window icon.
		self.iconlocation = os.getcwd() + "/tsicon.ico"
		try:
			self.iconbitmap(self.iconlocation)
		except:
			pass

		# Initialize the database and the cursor.
		self.database = sqlite3.connect('quinc.db')
		self.cur = self.database.cursor()

		# Create menu bar of the main window.
		self.menubar = tk.Menu(self)
		self.config(menu=self.menubar)
		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.aboutmenu = tk.Menu(self.menubar, tearoff=0)
		self.optionmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='Fichier', menu=self.filemenu)
		self.menubar.add_cascade(label='Options', menu=self.optionmenu)
		self.filemenu.add_command(label='Quit', command=self.quitApp)

		
		# Add to labelframe for select item and insert item.
		self.selectframe = ttk.LabelFrame(self, text="Liste d'articles",width=200)
		self.selectframe.propagate(False)
		self.selectframe.grid(row=0, column=0, sticky='wens',rowspan=2)
		self.insertframe = ttk.LabelFrame(self, text='Entrée stock')
		self.insertframe.grid(row=0, column=1, sticky='wens')
		self.displayframe = ttk.LabelFrame(self, text='Details')
		self.displayframe.grid(row=1, column=1, sticky='wens')
		# Add a ttk treeview for the display of transaction.
		self.treeview = ttk.Treeview(self.displayframe)
		self.treeview.grid(row=0, column=0, sticky='wens',rowspan=10)
		self.treeview.bind('<ButtonRelease-1>', self.selectTree)
		self.disyscroll = tk.Scrollbar(self.displayframe,
									   command=self.treeview.yview)
		self.disyscroll.grid(row=0, column=1, sticky='wns',rowspan=10)
		self.treeview.config(yscrollcommand=self.disyscroll.set)
		if self.type == "achat":
			self.column = ('Ref',
						   'Designation',
						   'Quantité', 'prix',
						   'Montant')
			self.heading = ('Réf',
						   'Designation',
						   'Quantité', 'prix',
						   'Montant (DT)')
		else: 
			self.column = ('Ref',
						   'Designation',
						   'Quantité', 'prix','remise',
						   'Montant')
			self.heading = ('Réf',
						   'Designation',
						   'Quantité', 'prix','remise',
						   'Montant (DT)')
		self.treeview['columns'] = self.column
		for elem in self.column:
			if elem == 'Ref':
				col_width = 100
			elif elem == 'Designation':
				col_width = 250
			elif elem == 'prix':
				col_width = 100			
			elif elem == 'Quantité':
				col_width = 100
			else:
				col_width = 100

			if elem == 'Montant':
				self.treeview.column(elem,anchor="c", width=col_width)
			else:
				self.treeview.column(elem,anchor="c", width=col_width, stretch=False)

		counter = 0
		self.treeview.heading('#0', text='S. No.')
		self.treeview.column('#0', width=50, stretch=False)
		for elem in self.column:
			self.treeview.heading(elem, text=self.heading[counter])
			counter += 1
		# Create tags for treeview.
		self.treeview.tag_configure('evenrow', background='#d5d5d5')
		self.treeview.tag_configure('oddrow', background='#f7f7f7')

		

		# Create and add a list box and a entry inside selectframe.
		dataquery = self.cur.execute("select distinct fournisseur from produit")
		self.dt = dataquery.fetchall()
		lstSupp = ['tout',*[i[0] for i in self.dt]]
		self.suppCbx = ttk.Combobox(self.selectframe, values=lstSupp,state='readonly')
		self.suppCbx.set("tout")
		self.suppCbx.bind("<<ComboboxSelected>>", self.refreshListBySupp)
		self.suppCbx.grid(row=0, column=0, sticky='we',rowspan=1)
		self.searchCbx = ttk.Combobox(self.selectframe, values=['Référence','Designation'],state='readonly')
		self.searchCbx.set("Designation")
		self.searchCbx.grid(row=1, column=0, sticky='we',rowspan=1)
		self.searchCbx.bind("<<ComboboxSelected>>", self.searchList)
		self.searchby = {'Référence':'ref','Designation':'Designation'}
		self.dt = None
		self.searchentry = ttk.Entry(self.selectframe)
		self.searchentry.grid(row=2, column=0, sticky='we',rowspan=1)
		self.searchentry.bind('<KeyPress>', self.searchList)
		self.itemlistbox = tk.Listbox(self.selectframe, width = 60)
		self.itemlistbox.grid(row=3, column=0, sticky='wens',rowspan=18)
		self.yscroll = tk.Scrollbar(self.selectframe,
									command=self.itemlistbox.yview)
		self.yscroll.grid(row=3, column=1, sticky='ns',rowspan=18)
		self.itemlistbox.config(yscrollcommand=self.yscroll.set)
		self.itemlistbox.bind('<<ListboxSelect>>', self.selectList)


		# Create labels inside the insert frame.
		self.date_label = ttk.Label(self.insertframe, text='Date:')
		self.date_label.grid(row=0, column=0, sticky='w',columnspan=3)		
		self.itemcode_label = ttk.Label(self.insertframe, text='Référence:')
		self.itemcode_label.grid(row=1, column=0, sticky='w')
		self.descp_label = ttk.Label(self.insertframe, text='Description:')
		self.descp_label.grid(row=2, column=0, sticky='wns')
		self.prix_label = ttk.Label(self.insertframe, text='prix:')
		self.prix_label.grid(row=5, column=0, sticky='w')
		self.quantity_label = ttk.Label(self.insertframe, text='Quantité en stock:')
		self.quantity_label.grid(row=1, column=10, sticky='w')
		
		self.qtd_label = ttk.Label(self.insertframe, text='Quantité achetée:')
		self.qtd_label.grid(row=2, column=10, sticky='w')
		
		# Create entries inside the insert frame.
		self.date_entry = ttk.Entry(self.insertframe,state='readonly',justify="center")
		self.date_entry.grid(row=0, column=1, sticky='w',pady=5)		

		self.ref_entry = ttk.Entry(self.insertframe,state='readonly',justify="center")
		self.ref_entry.grid(row=1, column=1, sticky='w',pady=5)
		self.desc_entry = tk.Text(self.insertframe,height =2,width=30,state='disabled',wrap='word')
		self.desc_entry.grid(row=2, column=1, sticky='wns',pady=5,rowspan=3,columnspan=8)
		self.prix_entry = ttk.Entry(self.insertframe, width=20,state='readonly',justify="center")
		self.prix_entry.grid(row=5, column=1, sticky='w',pady=5)
		self.quantity_entry = ttk.Entry(self.insertframe, width=20,state='readonly',justify="center",style="Q.TEntry" )
		self.quantity_entry.grid(row=1, column=11, sticky='w',pady=5)
		
				
		vcmd = (self.insertframe.register(self.onValidate),'%d', '%i', '%P', '%s', '%S')
		self.qta_entry = ttk.Entry(self.insertframe, width=20,justify="center")
		self.qta_entry.bind("<Key>", self.onValidate)
		self.qta_entry.grid(row=2, column=11, sticky='w',pady=5)
		self.qta_entry.bind('<Return>',self.addtoTreeView)
		self.lstEnt = [self.ref_entry,self.prix_entry,self.quantity_entry]
		# Create cancel save button
				# Add a delete and edit button for under tree view for
		# database manipulation and editing.
		self.nouv_btn = ttk.Button(self.displayframe,text='Nouveau',command=self.newCmd)
		self.nouv_btn.grid(row=4, column=2, sticky='we',padx=20,pady=5)
		self.delete_btn = ttk.Button(self.displayframe, text='Supprimer',command=self.deleteItemTreeView)
		self.delete_btn.grid(row=5, column=2,sticky='we',padx=20,pady=5)
		self.edit_btn = ttk.Button(self.displayframe, text='Ajout/Mod',command= self.addtoTreeView)
		self.edit_btn.grid(row=6, column=2,sticky='we',padx=20,pady=5)
		self.val_btn = tk.Button(self.displayframe,text='Valider',command=self.validateCmd,bg='#15d900')
		self.val_btn.grid(row=3, column=2, sticky='we',padx=20,pady=5)		
		if self.type == "achat":
			self.print_btn = tk.Button(self.insertframe,text='Imprimer',command=self.printFact,bg='#158aff')
			self.print_btn.grid(row=6, column=12, sticky='we',padx=20,pady=5)
		else : 
			self.qtd_label.configure(text="Quantité retournée:")
			self.quantity_label.configure(text="Quantité vendue:")
			self.numcmd_label = ttk.Label(self.insertframe, text='N° Commande:')
			self.numcmd_label.grid(row=0, column=10, sticky='w')
			self.numcmd_entry = ttk.Entry(self.insertframe,justify='center')
			self.numcmd_entry.grid(row=0, column=11, sticky='w')
			self.total_label = ttk.Label(self.insertframe, text='TOTAL (DT):')
			self.total_label.grid(row=3, column=10, sticky='w')
			self.total_entry = ttk.Entry(self.insertframe,justify='center')
			self.total_entry.grid(row=3, column=11, sticky='w')
			self.getcmd_btn = tk.Button(self.insertframe, text='LISTE',command=self.getNumCmd)
			self.getcmd_btn.grid(row=0, column=12, sticky='w',pady=5)
		# Insert today's date.
		now = datetime.strftime(datetime.now(),'%y-%m-%d %H:%M')
		self.date_entry.configure(state='normal')
		self.date_entry.insert(0, now)
		self.date_entry.configure(state='readonly')
		self.ref_entry.focus_set()
		
		# Insert item list into the listbox.
		self.refreshList()

		
		for x in range(2):
			self.grid_rowconfigure(x, weight=1)
		self.grid_columnconfigure(1, weight=1)
		for x in range(20):
			self.selectframe.grid_rowconfigure(x, weight=1)
		for x in range(1):
			self.selectframe.grid_columnconfigure(x, weight=1)
		for x in range(8):
			self.insertframe.grid_rowconfigure(x, weight=1)
		for x in range(20):
			self.insertframe.grid_columnconfigure(x, weight=1)
		for x in range(10):
			self.displayframe.grid_rowconfigure(x, weight=1)
		for x in range(1):
			self.displayframe.grid_columnconfigure(x, weight=1)
	def selectTree(self,event):
		curItem = self.treeview.focus()
		row = self.treeview.item(curItem)['values']
		if row !='':
			if self.type == "achat" :
				code,_,qta,_,_ = row
			else :	
				code,_,qta,_,_,_ = row
				
			for w in self.lstEnt :
				w.configure(state='normal')
			self.desc_entry.configure(state='normal')
			
			for d in self.dt:
				if d[0] == str(code) :
					row = d
					break

			self.desc_entry.configure(state='normal')
			self.ref_entry.delete('0', 'end')
			self.desc_entry.delete('1.0', 'end')
			self.prix_entry.delete('0', 'end')
			self.quantity_entry.delete('0', 'end')
			self.qta_entry.delete('0', 'end')
			
			self.ref_entry.insert('end', str(row[0]))
			self.desc_entry.insert('end', str(row[1]))
			self.prix_entry.insert('end', str(row[2]))
			self.quantity_entry.insert('end', str(row[3]))
			self.qta_entry.insert('end',str(qta))
			for w in self.lstEnt :
				w.configure(state='readonly')
			self.desc_entry.configure(state='disabled')
	def selectList(self, event):
		try : 
			crt = self.itemlistbox.curselection()[0]
		except :
			return False
			
		for w in self.lstEnt :
			w.configure(state='normal')
		self.desc_entry.configure(state='normal')
		self.ref_entry.delete("0", 'end')
		self.desc_entry.delete('1.0',tk.END)
		self.prix_entry.delete("0", 'end')
		self.quantity_entry.delete("0", 'end')
		self.qta_entry.delete('0', 'end')
		self.ref_entry.insert('end', str(self.dt[crt][0]))
		self.desc_entry.insert('end', str(self.dt[crt][1]))
		self.prix_entry.insert('end', str(self.dt[crt][2]))
		self.quantity_entry.insert('end', str(self.dt[crt][3]))
		if str(self.dt[crt][3])=='0':
			self.style.configure('Q.TEntry', fieldbackground='yellow')
		else:
			self.style.configure('Q.TEntry', fieldbackground='white')		
		for w in self.lstEnt :
			w.configure(state='readonly')
		self.desc_entry.configure(state='disabled')


	def deleteItemTreeView(self):
		curItem = self.treeview.focus()
		if curItem !='':
			self.treeview.delete(curItem)
			self.clearFields()
			self.redrawTree()
	def redrawTree(self):
		listPrd = self.treeview.get_children()
		cnt=1
		for r in listPrd:
			if cnt % 2 == 0:
				self.treeview.item(str(r),text=cnt,tag=("oddrow",))
			else:
				self.treeview.item(str(r),text=cnt,tag=("evenrow",))
			cnt+=1
	def addtoTreeView(self,event=None):
		if self.qta_entry.get()== '':
			return False
		row =[self.ref_entry.get(),self.desc_entry.get('1.0','end'),self.qta_entry.get(),self.prix_entry.get()]
		listPrd = self.treeview.get_children()
		rms = 0.0
		
		if self.type == "retour" :
		
			req = self.cur.execute("select v.remise from vente v,commande c where v.idcmd = ?",(self.numcmd_entry.get(),))
			data = req.fetchall()
			if len(data) : 
				rms = data[0][0]
			else: 
				rms = 0.0
				
		mnt = ((float(row[2]) * float(row[3]))  * (100.0 - float(rms))/100.0) / 1000.0
		rowid=None
		for r in listPrd:
			if str(self.treeview.item(r)['values'][0]) == self.ref_entry.get() :
				rowid=self.treeview.item(r)['text']
				break
		if rowid == None : 
			if len(listPrd) != 0:
				child = self.treeview.get_children()
				rowid = int(self.treeview.item(child[-1])['text'])+1
			else:
				rowid = 1
			if rowid % 2 == 0 :
				tg = 'evenrow'
			else:
				tg = 'oddrow'
			self.treeview.insert('', 'end', str(rowid), text=str(rowid), tag=(tg,))

		self.treeview.set(str(rowid), self.column[0], str(row[0]))
		self.treeview.set(str(rowid), self.column[1], str(row[1]))
		self.treeview.set(str(rowid), self.column[2], str(row[2]))
		self.treeview.set(str(rowid), self.column[3], str(row[3]))
		if self.type=="achat" :
			self.treeview.set(str(rowid), self.column[4], tl.convert(str(mnt)))
		else:
			self.treeview.set(str(rowid), self.column[4], str(rms))
			self.treeview.set(str(rowid), self.column[5], tl.convert(str(mnt)))
			self.calculTotal()
		self.clearFields()

		
	def validateCmd(self):
		if self.validee : 
			tk.messagebox.showwarning('info', "Cette transaction est déjà validée", parent=self.master)
			return False
		
		if not len(self.treeview.get_children()) : 
			tk.messagebox.showinfo('info', "Liste d'achat vide !", parent=self.master)
			return False
		
		if messagebox.askyesno("Confirmation", "Valider ?"):
			try:
				listPrd = self.treeview.get_children()
				if self.type == "achat" : 
					for r in listPrd:
						q = int(self.treeview.item(r)['values'][2])
						ref = str(self.treeview.item(r)['values'][0])
						
						self.cur.execute("insert into achat values (null,?,?,?)",(q,self.date_entry.get(),ref,))
						self.cur.execute("update produit set quantite = quantite + ? where ref = ?",(q,ref,))
				else: 
					for r in listPrd:
						q = int(self.treeview.item(r)['values'][2])
						ref = str(self.treeview.item(r)['values'][0])
						rms =  str(self.treeview.item(r)['values'][4])
						self.cur.execute("insert into retour values (null,?,?,?,?)",(q,rms,self.date_entry.get(),ref,))
						self.cur.execute("update produit set quantite = quantite + ? where ref = ?",(q,ref,))

				self.database.commit()
				tk.messagebox.showinfo('info', "La base de données a été mise à jour", parent=self.master)
				self.refreshList()
				self.validee=True
			except sqlite3.Error:
				print(sqlite3.Error)
				self.database.rollback()
				tk.messagebox.showwarning('avertissement', "un erreur s'est produit", parent=self.master)
	def searchList(self, event):
	
		frn = self.suppCbx.get()
		item = self.searchentry.get()
		if event.char.isalpha() or event.char.isnumeric():
			item +=  str(event.char)
		if event.keysym == 'BackSpace':
			item = item[:-1]
		self.dt = None
		self.itemlistbox.delete('0', 'end')
		self.dt = self.reqProduct(item,frn)
		for data in self.dt:
			self.itemlistbox.insert('end', data[self.searchCbx.current()])
	def reqProduct(self,item='',frn='tout',event=None):
	
		model = "SELECT ref,designation,"+ self.prix +",quantite FROM produit"
		if item != '' :
			model += " WHERE " + self.searchby[self.searchCbx.get()]+ " like ?"
			if frn != 'tout':
				model += " and fournisseur = ?"
				dataquery = self.cur.execute(model, ('{}%'.format(item),frn,))
			else:
				dataquery = self.cur.execute(model, ('{}%'.format(item),))
		else:
			if frn != 'tout':
				model += " where fournisseur = ?"
				dataquery = self.cur.execute(model, ('{}'.format(frn),))
			else:	
				dataquery = self.cur.execute(model)
		dt = dataquery.fetchall()
		result = []
		if self.type =="retour" : 
			for r in dt :
				result.append([*r[:3],""])
			return result
		else :
			return dt
	def refreshList(self):
		# Insert item list into the listbox.
		self.itemlistbox.delete('0', 'end')
		self.dt = self.reqProduct()
		for row in self.dt:
			self.itemlistbox.insert('end', row[self.searchCbx.current()])	
	def refreshListBySupp(self,event):
		# Insert item list into the listbox.
		self.itemlistbox.delete('0', 'end')
		f = self.suppCbx.get()
		self.dt = self.reqProduct(frn=f)
		for row in self.dt:
			self.itemlistbox.insert('end', row[self.searchCbx.current()])
	def getNumCmd(self):
		SearchCmd(self,self.numcmd_entry,validOnly=True) 

	def quitApp(self):
		# Check first if the database is open, if so close it.
		if self.database:
			try: 
				self.database.commit()
			except sqlite3.Error:
				self.database.rollback()
			self.cur.close()
			self.database.close()
		self.root.update()
		self.root.deiconify()
		self.root.state("zoomed")
		self.destroy()


	def newCmd(self):
		if self.type == "retour":
			self.total_entry.delete('0','end')
			self.total_entry.insert('0','0')
		ncmd = datetime.strftime(datetime.now(),'%y-%m-%d %H:%M')
		self.date_entry.configure(state='normal')
		self.date_entry.delete('0', 'end')
		self.date_entry.insert('0', ncmd)
		self.date_entry.configure(state='readonly')
		self.validee=False
		self.clearFields()
		if len(self.treeview.get_children()) != 0:
			child = self.treeview.get_children()
			for item in child:
				self.treeview.delete(item)
	def getCmdList(self) :
		self.itemlistbox.delete('0', 'end')
		rq= self.cur.execute("select p.ref,p.designation,p.pvente,v.quantite from produit p,vente v where v.idprod = p.ref and v.idcmd = ?",(self.numcmd_entry.get(),))
		self.dt = rq.fetchall()
		for row in self.dt:
			self.itemlistbox.insert('end', row[self.searchCbx.current()])
	def calculTotal(self):
		lst = self.treeview.get_children()
		if len(lst):
			s=0.0
			for r in lst : 
				s += float(tl.reconvert(self.treeview.item(r)['values'][5]))
			self.total_entry.delete('0','end')
			self.total_entry.insert('0',tl.convert(round(s,3)))
	def clearFields(self):
		for w in self.lstEnt :
			w.configure(state='normal')
		self.desc_entry.configure(state='normal')
		self.ref_entry.delete('0', 'end')
		self.desc_entry.delete('1.0', 'end')
		self.prix_entry.delete('0', 'end')
		self.quantity_entry.delete('0', 'end')
		self.qta_entry.delete('0', 'end')
		for w in self.lstEnt :
			w.configure(state='readonly')
		self.desc_entry.configure(state='disabled')
	def onValidate(self,event):
			if event.keysym == 'Tab':
				return 'Tab'
			qs = self.quantity_entry.get()
			S = self.qta_entry.get()
			if qs != '':
				if event.char.isnumeric() :
					S += event.char
				elif event.char != "" and event.char!="\x08":
					return "break"
			else:
				return "break"

	def printFact(self):
		import webbrowser
		
		html_str = """
		 <!DOCTYPE html>
		<html
		<head>
		<title>Bon d'entrée</title>
		</head>
		<style>
		table {
			width:60%;
		}
		table, th, td {
			border: 0px solid black;
			border-collapse: collapse;
		}
		.border {
			border: 1px solid black;
			border-collapse: collapse;
		}
		.border1 {
			border: 1px solid black;
			border-collapse: collapse;
			font-weight:bold
			}
		th, td {
			padding: 15px;
			text-align: center;
		}
		.tr1 {
			background-color: white;
		}
		table tr:nth-child(even) {
			background-color: #eee;
		}
		table tr:nth-child(odd) {
		   background-color: #fff;
		}
		table th {
			background-color: #797979;
			color: white;
		}
		</style>
		<body>
		<h1 align="center" > QUINCAILLERIE RAMI MLAWAH </h1>
		<h2 align="center" >BON D'ENTREE</h2>
		<h3 align="center" >DATE & HEURE : """ + str(self.date_entry.get()) + """</h3>
		<br><br>
		<table border=1 align="center">
			 <tr>
			   <th class="border"> N° </th>
			   <th class="border">Référence</th>
			   <th class="border">Désignation</th>
			   <th class="border">Quantité</th>
			   <th class="border">Prix</th>
			   <th class="border">Montant (DT)</th>
			 </tr>
			 <indent>
		"""
		listPrd = self.treeview.get_children()
		sum=0
		for r in listPrd:
			row = [self.treeview.item(r)['text'],self.treeview.item(r)['values'][0],self.treeview.item(r)['values'][1],self.treeview.item(r)['values'][2],self.treeview.item(r)['values'][3],self.treeview.item(r)['values'][4]]
			mnt = tl.reconvert(self.treeview.item(r)['values'][4])
			sum+=float(mnt)
			html_str += "<tr >"
			for i in row :
				html_str += "<td class='border'>" + str(i) + "</td>"
			html_str += "</tr>"
		html_str += """<tr class=tr1><td></td><td></td><td></td><td></td><td class="border1"> TOTAL </td><td class="border1">""" + tl.convert(round(sum,3)) + """</td></tr>
		</table>
		</body>
		</html> 
		"""

		Html_file= open("filename.html","w")
		Html_file.write(html_str)
		Html_file.close()
		webbrowser.open("filename.html");

class ItemMaster(tk.Toplevel):

	def __init__(self, master):
		self.root = master
		tk.Toplevel.__init__(self, master)
		self.title('Gestion des produits')
		self.protocol('WM_DELETE_WINDOW', self.quitApp)
		self.grab_set()
		self.state('zoomed')
		# Set the icon of the window.
		self.iconlocation = os.getcwd() + "/tsicon.ico"
		try:
			self.iconbitmap(self.iconlocation)
		except:
			pass

		# Initialize the database.
		self.database = sqlite3.connect('quinc.db')
		# self.database.set_trace_callback(print)
		self.cur = self.database.cursor()

		# Create 3 main container of the window.
		self.titleframe = ttk.LabelFrame(self)
		self.titleframe.pack(fill='both', padx=5, pady=5, expand=False)
		self.upperframe = ttk.LabelFrame(self, text='Details')
		self.upperframe.pack(fill='both', padx=5, pady=5)
		self.searchframe = ttk.LabelFrame(self, text='Recherche')
		self.searchframe.pack(fill='both', expand=False, padx=5, pady=5)
		self.lowerframe = ttk.LabelFrame(self, text='Liste des produits')
		self.lowerframe.pack(fill='both', expand=True, padx=5, pady=5)
		self.buttonframe = tk.Frame(self)
		self.buttonframe.pack(fill='both', padx=5, pady=5)

		# Add labels for self.upperframe.
		self.ttl = ttk.Label(self.titleframe, text='Gestion de stock',font='Helvetica 12 bold')
		self.ttl.grid(row=0, column=10, padx=5, pady=5,sticky='we')
		self.labelcode = ttk.Label(self.upperframe, text='Référence:')
		self.labelcode.grid(row=1, column=0, padx=5, pady=5)
		self.labeldesc = ttk.Label(self.upperframe, text='Description:')
		self.labeldesc.grid(row=2, column=0, padx=5, pady=5)
		self.labelunit = ttk.Label(self.upperframe, text='Unité:')
		self.labelunit.grid(row=3, column=0, padx=5, pady=5)
		self.labelrmk = ttk.Label(self.upperframe, text='Remarque:')
		self.labelrmk.grid(row=4, column=0, padx=5, pady=5)
		self.labelpachat = ttk.Label(self.upperframe, text='Prix achat:')
		self.labelpachat.grid(row=1, column=12, padx=5, pady=5)
		self.labelpvente = ttk.Label(self.upperframe, text='Prix vente:')
		self.labelpvente.grid(row=2, column=12, padx=5, pady=5)
		self.labelquantity = ttk.Label(self.upperframe, text='Quantité:')
		self.labelquantity.grid(row=3, column=12, padx=5, pady=5)
		self.labelfourn = ttk.Label(self.upperframe, text='fournisseur:')
		self.labelfourn.grid(row=4, column=12, padx=5, pady=5)

		# Add entries for self.upframe2
		self.code_entry = ttk.Entry(self.upperframe, width=25,justify="center")
		self.code_entry.grid(row=1, column=1, padx=5, pady=5,sticky='w')
		self.desc_entry = tk.Text(self.upperframe, width=20,height=2)
		self.desc_entry.grid(row=2, column=1, padx=5, pady=5,columnspan=10,sticky='w')
		self.unit_entry = ttk.Entry(self.upperframe, width=25,justify="center")
		self.unit_entry.grid(row=3, column=1, padx=5, pady=5,sticky='w')
		self.rmk_entry = tk.Text(self.upperframe, width=20,height=2)
		self.rmk_entry.grid(row=4, column=1, padx=5, pady=5,sticky='w')
		self.pachat_entry = ttk.Entry(self.upperframe, width=20,justify="center")
		self.pachat_entry.grid(row=1, column=13, padx=5, pady=5,sticky='w')
		self.pachat_entry.bind("<Key>",self.onValidate)
		self.pvente_entry = ttk.Entry(self.upperframe, width=20,justify="center")
		self.pvente_entry.grid(row=2, column=13, padx=5, pady=5,sticky='w')
		self.pvente_entry.bind("<Key>",self.onValidate)
		self.quantity_entry = ttk.Entry(self.upperframe, width=20,justify="center")
		self.quantity_entry.grid(row=3, column=13, padx=5, pady=5,sticky='w')
		self.quantity_entry.bind("<Key>",self.onValidate)
		self.fourn_entry = ttk.Entry(self.upperframe, width=20,justify="center")
		self.fourn_entry.grid(row=4, column=13, padx=5, pady=5,sticky='w')
		
		# Add search items to self.searchframe
		self.labelsearch = ttk.Label(self.searchframe, text='Recherche :')
		self.labelsearch.grid(row=0, column=0, padx=5, pady=5)
		self.searchCbx  = ttk.Combobox(self.searchframe, width=17,values = ['Désignation','Référence'])
		self.searchCbx.grid(row=0, column=1, padx=5, pady=5,sticky='w')
		self.searchCbx.set("Désignation")
		self.search_entry = ttk.Entry(self.searchframe, width=20,justify="center")
		self.search_entry.grid(row=0, column=2, padx=5, pady=5,sticky='w')
		self.search_entry.bind("<Key>",self.searchitem)
		self.afftout_btn = ttk.Button(self.searchframe, text='Afficher tout',command=self.showAll)
		self.afftout_btn.grid(row=0, column=3, padx=5, pady=5,sticky='w')
		
		self.lstEnt = [[self.code_entry	,self.unit_entry,self.pachat_entry	,self.pvente_entry	,self.quantity_entry	,self.fourn_entry	],[self.desc_entry,self.rmk_entry]]	
		# Add buttons to self.upframe3
		self.add_btn = ttk.Button(self.upperframe, text='Ajouter')
		self.add_btn.grid(row=1, column=15, padx=5, pady=5)
		self.add_btn.config(command=self.additem)
		self.delete_btn = ttk.Button(self.upperframe, text='Supprimer')
		self.delete_btn.grid(row=2, column=15, padx=5, pady=5)
		self.delete_btn.config(command=self.deleteitem)
		self.update_btn = ttk.Button(self.upperframe, text='Mettre à jour')
		self.update_btn.grid(row=3, column=15, padx=5, pady=5)
		self.update_btn.config(command=self.updateitem)		
		self.clear_btn = ttk.Button(self.upperframe, text='Effacer tout')
		self.clear_btn.grid(row=4, column=15, padx=5, pady=5)
		self.clear_btn.config(command=self.clearFields)

		# Add the tree inside self.lowerframe.
		self.treeview = ttk.Treeview(self.lowerframe)
		self.treeview.pack(side='left',
							   expand=True,
							   fill='both'
							   )
		self.tyscroll = tk.Scrollbar(self.lowerframe,
									 orient='vertical',
									 command=self.treeview.yview)
		self.tyscroll.pack(side='left', fill='both')
		self.treeview.config(yscrollcommand=self.tyscroll.set)
		self.treeview.bind('<ButtonRelease-1>', self.selectItem)
		
		
		# Add close button to the self.buttonframe
		self.close_btn = ttk.Button(self.buttonframe,
									text='Close',
									command=self.quitApp
									)
		self.close_btn.pack(anchor='e', pady=5)

		# Create the heading of the treeview.
		column = ('itemcode', 'designation', 'unit', 'quantite', 'pachat', 'pvente', 'fournisseur', 'remarque')
		heading = ('Référence', 'Désignation', 'Unité', 'quantité', 'P.U Achat', 'P.U Vente', 'Fournisseur', 'Remarque')
		self.treeview['columns'] = column
		self.treeview.heading('#0', text='S. No.')
		self.treeview.column('#0', width=35)
		counter = 0
		for hlabel in heading:
			if counter == 0:
				self.treeview.column(column[counter],anchor="c", width=60)
			elif counter == 1:
				self.treeview.column(column[counter],anchor="c", width=250)
			else:
				self.treeview.column(column[counter],anchor="c", width=60)
			self.treeview.heading(column[counter], text=hlabel)
			counter += 1

		# Create tags for the treeview.
		self.treeview.tag_configure('evenrow', background='#d5d5d5')
		self.treeview.tag_configure('oddrow', background='#f7f7f7')
		self.treeview.tag_configure('emptystock', background='#ffca73')

		# treeview the items in the treeview.
		self.displayitem()
		for x in range(8):
			self.upperframe.grid_rowconfigure(x, weight=1)
		for x in range(20):
			self.upperframe.grid_columnconfigure(x, weight=1)
		for x in range(1):
			self.searchframe.grid_rowconfigure(x, weight=1)
		for x in range(20):
			self.searchframe.grid_columnconfigure(x, weight=1)		
		for x in range(20):
			self.titleframe.grid_columnconfigure(x, weight=1)
		
	def additem(self):
		qt = self.quantity_entry.get()
		if qt == '':
			qt = 0
		listPrd = self.treeview.get_children()
		for r in listPrd:
			if str(self.treeview.item(r)['values'][0]) == self.code_entry.get() :
				tk.messagebox.showwarning('avertissement', "Un produit de même référence existe déjà !", parent=self.master)
				return False
		field_full,price_val = self.checkFiels()
		if not(field_full) :
			tk.messagebox.showwarning('avertissement', "Veuillez vérifier tous les champs !", parent=self.master)
		elif not(price_val):
			tk.messagebox.showwarning('avertissement', "Veuillez vérifier les prix !", parent=self.master)

		elif messagebox.askyesno("Confirmation", "Ajouter ce produit?"):
			self.cur.execute("INSERT INTO produit VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
								 (self.code_entry.get(),
								  self.desc_entry.get("1.0",'end'),
								  self.unit_entry.get(),
								  qt,
								  self.pachat_entry.get(),
								  self.pvente_entry.get(),
								  self.fourn_entry.get(),
								  self.rmk_entry.get('1.0','end'))
								 )
			now = datetime.strftime(datetime.now(),'%y-%m-%d %H:%M')
			self.cur.execute("insert into achat values (null,?,?,?)",(qt,now,self.code_entry.get(),))
			try:
				self.database.commit()
				tk.messagebox.showinfo("info","Produit ajouté avec succès", parent=self.master)
			except sqlite3.Error:
				self.database.rollback()
				tk.messagebox.showwarning('avertissement', "un erreur s'est produit", parent=self.master)

			# Clear the entries.
			self.clearFields()
		
			# Refresh the list of items.
			self.displayitem()
			self.code_entry.focus_set()





	def deleteitem(self):
		try:
			
			# Ask if you really want to delete the item.
			askifsure = tk.messagebox.askokcancel('Confirmation',
												  "supprimer cet élément?",
												  parent=self.master
												  )

			# If answer from askifsure variable is True, delete the item.
			if askifsure is True:
				ref = self.treeview.item(self.treeview.selection()[0])['values'][0]
				self.cur.execute("DELETE FROM produit WHERE ref = ?",
								 (ref,))
				try:
					self.database.commit()
				except sqlite3.Error:
					self.database.rollback()
				# Show if the item has been remove from the database.
				tk.messagebox.showinfo('Information',
									   "Produit supprimé de la base de donnée.",
									   parent=self.master
									   )
			# Else do nothing and prompt an info that no item was deleted.
			else:
				tk.messagebox.showinfo('Information',
									   "Aucun changement n'a été appliqué",
									   parent=self.master
									   )
		# If there nothing is selected from the table prompt a warning.
		except IndexError:
			tk.messagebox.showwarning('Erreur',
									  "Veuillez sélectionner l'élément à supprimer",
									  parent=self.master
									  )

		# Refresh the table and set the focus to item code entry.
		self.displayitem()
		self.code_entry.focus_set()
	def updateitem(self):
		curItem = self.treeview.focus()
		field_full,price_val = self.checkFiels()
		if not(field_full) :
			tk.messagebox.showwarning('avertissement', "Veuillez vérifier tous les champs !", parent=self.master)
			return False
		elif not(price_val):
			tk.messagebox.showwarning('avertissement', "Veuillez vérifier les prix !", parent=self.master)
			return False
		if curItem == '':
			tk.messagebox.showwarning('Erreur',"Veuillez sélectionner l'élément à supprimer",parent=self.master)
			return None

		try:
			vals  = [self.code_entry.get(),self.desc_entry.get('1.0','end'),self.unit_entry.get(),self.quantity_entry.get(),self.pachat_entry.get(),self.pvente_entry.get(),self.fourn_entry.get(),self.rmk_entry.get('1.0','end')]
			askifsure = tk.messagebox.askokcancel('Confirmation',
												  "Mettre à jour les données?",
												  parent=self.master
												  )

			if askifsure is True:
				self.cur.execute("UPDATE produit SET designation= ? ,unite= ?, quantite= ?, pachat= ?, pvente= ?, fournisseur= ?, remarque= ? WHERE ref = ?;",
								 (vals[1],vals[2],int(vals[3]),int(vals[4]),int(vals[5]),vals[6],vals[7],vals[0]))
				try:
					self.database.commit()
					tk.messagebox.showinfo('Information',
									   "Les données ont été mises à jour",
									   parent=self.master
									   )
				except sqlite3.Error:
					self.database.rollback()
					tk.messagebox.showerror(sqlite3.Error,
									   parent=self.master
									   )

		# If there nothing is selected from the table prompt a warning.
		except : 
			tk.messagebox.showwarning('Erreur',"Veuillez sélectionner l'élément à supprimer",parent=self.master)

		# Refresh the table and set the focus to item code entry.
		self.displayitem()
		self.clearFields()

	def searchitem(self,event):
		v  = self.search_entry.get()
		if event.keysym == 'BackSpace':
			v = v[:-1]
		else:
			v+= event.char
		if v != "":
			if self.searchCbx.get()	== "Désignation":
				self.displayitem(designation = v)
			else:
				self.displayitem(code = v)
		else:
			self.displayitem()

	def displayitem(self,designation = None,code = None):
		# Check if there is any data in the treeview
		# if so delete and load the list again.
		if len(self.treeview.get_children()) != 0:
			child = self.treeview.get_children()
			for item in child:
				self.treeview.delete(item)
		if designation != None :
			req = "SELECT * FROM produit WHERE designation like ?"
			data = self.cur.execute(req, ('{}%'.format(designation),))
		elif code != None :
			req = "SELECT * FROM produit WHERE ref like ?"
			data = self.cur.execute(req, ('{}%'.format(code),))
		else:
			data = self.cur.execute("SELECT * FROM produit")
		# Initialize the database.
		
		data_list = data.fetchall()
		column = ('rowid','itemcode', 'designation', 'unit', 'quantite', 'pachat', 'pvente', 'fournisseur', 'remarque')
		counter = 1
		if len(data_list) > 0:
			for num in data_list:
				if int(num[3])==0 :
					self.treeview.insert('','end',str(counter),text=str(counter),tag='emptystock')
				else:
					if counter % 2 == 0:
						self.treeview.insert('','end',str(counter),text=str(counter),tag='evenrow')
					else:
						self.treeview.insert('','end',str(counter),text=str(counter),tag='oddrow')
				self.treeview.set(str(counter), column[1], str(num[0]))
				self.treeview.set(str(counter), column[2], str(num[1]))
				self.treeview.set(str(counter), column[3], str(num[2]))
				self.treeview.set(str(counter), column[4], int(num[3]))
				self.treeview.set(str(counter), column[5], int(num[4]))
				self.treeview.set(str(counter), column[6], int(num[5]))
				self.treeview.set(str(counter), column[7], str(num[6]))
				self.treeview.set(str(counter), column[8], str(num[7]))
				
				counter += 1
	def selectItem(self,event):
		
		curItem = self.treeview.focus()
		row = self.treeview.item(curItem)['values']
		
		if row !='':
			self.clearFields()
			
			self.code_entry.insert('0',row[0])
			self.desc_entry.insert('1.0',row[1])
			self.unit_entry.insert('0',row[2])
			self.quantity_entry.insert('0',row[3])
			self.pachat_entry.insert('0',row[4])
			self.pvente_entry.insert('0',row[5])
			self.fourn_entry.insert('0',row[6])
			self.rmk_entry.insert('1.0',row[7])
			
	def checkFiels(self):
		field_full = True
		price_val = True
		if self.code_entry.get()=='' or self.desc_entry.get("1.0")=='' or self.unit_entry.get()=='' or self.pachat_entry.get()=='' or self.pvente_entry.get()=='':
			field_full = False
				
		elif float(self.pvente_entry.get()) < float(self.pachat_entry.get()) :
			price_val = False
			
		return field_full,price_val
		
	def onValidate(self,event):
		if event.keysym == 'Tab':
			return 'Tab'
		c = event.char
		if c.isnumeric()==False and c!="" and c!= "\x08" :
			return "break"
	def showAll(self):
		self.search_entry.delete('0','end')
		self.displayitem()
	def clearFields(self):
		for w in self.lstEnt[0]:
			w.delete('0', 'end')
			w.insert('0', '')
		self.desc_entry.delete("1.0", 'end')
		self.rmk_entry.delete("1.0", 'end')
		
	def quitApp(self):
		# Check whether the database is open, if so close it.
		if self.database:
			self.cur.close()
			self.database.close()
			print('Database successfully closed.')
		self.root.update()
		self.root.deiconify()
		self.root.state("zoomed")
		self.grab_release()
		self.destroy()



class Reports(tk.Toplevel):

	def __init__(self, master):
		"""
		Initialize the graphics user interface for stock reporting.
		"""
		tk.Toplevel.__init__(self, master)
		self.root = master
		self.title('Rapport')
		self.protocol('WM_DELETE_WINDOW', self.quitApp)
		self.state("zoomed")
		# Set the window icon.
		self.iconlocation = os.getcwd() + "/tsicon.ico"
		try:
			self.iconbitmap(self.iconlocation)
		except:
			pass

		# Initialize the database.
		self.database = sqlite3.connect('quinc.db')
		self.cur = self.database.cursor()
	
		# Create container for the treeview and scrollbar.
		display_frame = tk.Frame(self)
		display_frame.grid(row=0, column=0,sticky='wens')		
		display_frame1 = tk.Frame(self)
		display_frame1.grid(row=1, column=0,sticky='wens')
		
		report_label = ttk.Label(display_frame, text='RAPPORT')
		report_label.grid(row=0, column=0,columnspan = 7)
		report_label.config(font=('Helvetica', 15, 'bold'))
		lb1 = ttk.Label(display_frame, text='TOTAL VENTE (DT)')
		lb1.grid(row=1, column=1,sticky='e')
		self.e1 = ttk.Entry(display_frame,justify ='center')
		self.e1.grid(row=1, column=2,sticky='w')
		lb2 = ttk.Label(display_frame, text='TOTAL ACHAT (DT)')
		lb2.grid(row=1, column=3,sticky='e')
		self.e2 = ttk.Entry(display_frame,justify ='center')
		self.e2.grid(row=1, column=4,sticky='w')
		lb3 = ttk.Label(display_frame, text='TOTAL RETOUR (DT)')
		lb3.grid(row=1, column=5,sticky='e')
		self.e3 = ttk.Entry(display_frame,justify ='center')
		self.e3.grid(row=1, column=6,sticky='w')
		lb4 = ttk.Label(display_frame, text='GAIN NET (DT)')
		lb4.grid(row=1, column=7,sticky='e')
		self.e4 = ttk.Entry(display_frame,justify ='center')
		self.e4.grid(row=1, column=8,sticky='w')
		self.periodCbx  = ttk.Combobox(display_frame, width=17,values = ["JOURNALIER",'MENSUEL','ANNUEL'])
		self.periodCbx.grid(row=1, column=0, padx=10, pady=10,sticky='w')
		self.periodCbx.set("JOURNALIER")
		self.periodCbx.bind('<<ComboboxSelected>>',self.insertDetails)
		# Create a tkinter.ttk treeview.
		self.treeview = ttk.Treeview(display_frame1)
		self.treeview.grid(row=0, column=0,sticky='wens')

		# Create a scrollbar for the treeview.
		yscrollbar = tk.Scrollbar(display_frame1)
		yscrollbar.grid(row=0, column=1,sticky="ns")
		yscrollbar.config(command=self.treeview.yview)
		self.treeview.config(yscrollcommand=yscrollbar.set)

		# Initialize column and heading variable.
		self.headers = ('Référence','Designation','Unité','P.V (millime)','P.A (millime)','Sortie','Entree','retour','Vente (DT)','Achat (DT)','Retour (DT)')
		self.column = ('ref','designation','Unite','pr.vente','pr.achat','Sortie','Entree','retour','Vente','Achat','Retour')
		# Set the column of the tree.
		self.treeview['columns'] = self.column

		# Set the heading of the tree and the width of each column.
		counter = 0
		self.treeview.heading('#0', text='S. No.')
		self.treeview.column('#0', width=40)
		for head in self.column:
			if head == 'ref':
				setwidth = 85
			elif head == 'designation':
				setwidth = 180
			else:
				setwidth = 50
			self.treeview.heading(head, text=self.headers[counter])
			self.treeview.column(head,anchor="c", width=setwidth)
			counter += 1
		# Create tags for treeview.
		self.treeview.tag_configure('evenrow', background='#d5d5d5')
		self.treeview.tag_configure('oddrow', background='#f7f7f7')

		# Insert the details to the tree.
		self.insertDetails()

		# Create a button below the treeview for exporting
		# the report to a csv file.
		self.export_btn = ttk.Button(display_frame1, text='Imprimer',command=self.exportFile)
		self.export_btn.grid(row=1, column=0,padx=10,pady=10)
		
		self.grid_rowconfigure(1, weight=1)
		for x in range(1):
			self.grid_columnconfigure(x, weight=1)		
			
		for x in range(9):
			display_frame.grid_columnconfigure(x, weight=1)
			
		display_frame1.grid_rowconfigure(0, weight=1)
		display_frame1.grid_columnconfigure(0, weight=1)
	def insertDetails(self,event=None):

		for c in self.treeview.get_children() :
			self.treeview.delete(c)
		today = datetime.strftime(datetime.now(),'%y-%m-%d')
		if self.periodCbx.get() == "JOURNALIER" :
			dt = today [:8]
		elif self.periodCbx.get() == "MENSUEL":
			dt = today[:5]
		else :
			dt = today[:2]
		# Combine incoming and outgoing material

		table = self.cur.execute("SELECT a.idprod,p.designation,p.unite,p.pvente,p.pachat,sum(a.quantite),sum(a.quantite * p.pachat) from achat a,produit p  where a.idprod = p.ref and a.date like ? group by a.idprod ",('{}%'.format(dt),))
		data_achat = table.fetchall()
		table = self.cur.execute("SELECT r.idprod,p.designation,p.unite,p.pvente,p.pachat,sum(r.quantite),sum((r.quantite * p.pvente)*(100.0 - r.remise)/100.0) from retour r,produit p  where r.idprod = p.ref and r.date like ? group by r.idprod ",('{}%'.format(dt),))
		data_retour = table.fetchall()
		table = self.cur.execute("SELECT v.idprod,p.designation,p.unite,p.pvente,p.pachat,sum(v.quantite),sum((v.quantite * p.pvente)*(100.0 - v.remise)/100.0) from vente v,commande c,produit p  where c.validee = 1 and c.idcmd = v.idcmd and p.ref = v.idprod and c.date like ? group by v.idprod",('{}%'.format(dt),))
		data_vente = table.fetchall()
		table = self.cur.execute("SELECT sum(v.quantite * (p.pvente*(100.0 - v.remise)/100.0 - p.pachat)) from vente v,commande c,produit p  where c.validee = 1 and c.idcmd = v.idcmd and p.ref = v.idprod and c.date like ?",('{}%'.format(dt),))
		gain = table.fetchall()[0][0] / 1000.0
		data =[]
		for r in data_vente :
			data.append([*r[:6],0,0,r[6],0,0])
		for ra in data_achat :
			ex =False
			for i in range(len(data)) :
				if data[i][0] == ra[0] :
					data[i][6] = ra[5]
					data[i][9] = ra[6]
					ex=True
			if ex==False :
				data.append([ra[0],ra[1],ra[2],ra[3],ra[4],0,ra[5],0,0,ra[6],0])
		for ra in data_retour :
			ex =False
			for i in range(len(data)) :
				if data[i][0] == ra[0] :
					data[i][7] = ra[5]
					data[i][10] = ra[6]
					ex=True
			if ex==False :
				data.append([ra[0],ra[1],ra[2],ra[3],ra[4],0,0,ra[5],0,0,ra[6]])

		counter = 1
		sum_achat=0
		sum_vente=0
		sum_retour=0
		if len(data) > 0:
			for num in data:
				if counter % 2 == 0:
					self.treeview.insert('','end',str(counter),text=str(counter),tag='evenrow')
				else:
					self.treeview.insert('','end',str(counter),text=str(counter),tag='oddrow')
				self.treeview.set(str(counter), self.column[0], str(num[0]))
				self.treeview.set(str(counter), self.column[1], str(num[1]))
				self.treeview.set(str(counter), self.column[2], str(num[2]))
				self.treeview.set(str(counter), self.column[3], str(num[3]))
				self.treeview.set(str(counter), self.column[4], str(num[4]))
				self.treeview.set(str(counter), self.column[5], str(num[5]))
				self.treeview.set(str(counter), self.column[6], str(num[6]))
				self.treeview.set(str(counter), self.column[7], str(num[7]))
				self.treeview.set(str(counter), self.column[8], tl.convert(float(num[8])/1000.0))
				self.treeview.set(str(counter), self.column[9], tl.convert(float(num[9])/1000.0))
				self.treeview.set(str(counter), self.column[10], tl.convert(float(num[10])/1000.0))
				sum_vente+= float(num[8])/1000.0
				sum_achat+= float(num[9])/1000.0
				sum_retour+= float(num[10])/1000.0
				counter+=1
		self.e1.delete("0","end")
		self.e2.delete("0","end")
		self.e3.delete("0","end")
		self.e4.delete("0","end")
		self.e1.insert("0",tl.convert(sum_vente))
		self.e2.insert("0",tl.convert(sum_achat))
		self.e3.insert("0",tl.convert(sum_retour))
		self.e4.insert("0",tl.convert(gain-sum_retour))
	def exportFile(self):
		import webbrowser
		html_str = """
		 <!DOCTYPE html>
		<html
		<head>
		<title>Bon d'entrée</title>
		</head>
		<style>
		table {
			width:60%;
		}
		table, th, td {
			border: 0px solid black;
			border-collapse: collapse;
		}
		.border {
			border: 1px solid black;
			border-collapse: collapse;
		}
		.border1 {
			border: 1px solid black;
			border-collapse: collapse;
			font-weight:bold
			}
		th, td {
			padding: 15px;
			text-align: center;
		}
		.tr1 {
			background-color: white;
		}
		table tr:nth-child(even) {
			background-color: #eee;
		}
		table tr:nth-child(odd) {
		   background-color: #fff;
		}
		table th {
			background-color: #797979;
			color: white;
		}
		</style>
		<body>
		<h1 align="center" > QUINCAILLERIE RAMI MLAWAH </h1>
		<h2 align="center" > RAPPORT """ + self.periodCbx.get() + """</h2>
		<h3 align="center" >DATE & HEURE : """ + str(datetime.strftime(datetime.now(),'%y-%m-%d %H:%M')) + """</h3>
		<table border=1 align="center">
			 <tr>
			   <th class="border"> N° </th>
			   <th class="border">Référence</th>
			   <th class="border">Désignation</th>
			   <th class="border">Unité</th>
			   <th class="border">P.V (millime) </th>
			   <th class="border">P.A (millime)</th>
			   <th class="border">Sortie</th>
			   <th class="border">Entree</th>
			   <th class="border">Retour</th>
			   <th class="border">Total Vente (DT)</th>
			   <th class="border">Total Achat (DT)</th>
			   <th class="border">Total Retour (DT)</th>
			 </tr>
			 <indent>
		"""
		listPrd = self.treeview.get_children()
		for r in listPrd:
			row = [self.treeview.item(r)['text'],
					self.treeview.item(r)['values'][0],
					self.treeview.item(r)['values'][1],
					self.treeview.item(r)['values'][2],
					self.treeview.item(r)['values'][3],
					self.treeview.item(r)['values'][4],
					self.treeview.item(r)['values'][5],
					self.treeview.item(r)['values'][6],
					self.treeview.item(r)['values'][7],
					self.treeview.item(r)['values'][8],
					self.treeview.item(r)['values'][9],
					self.treeview.item(r)['values'][10]]
			html_str += "<tr >"
			for i in row :
				html_str += "<td class='border'>" + str(i) + "</td>"
			html_str += "</tr>"
		html_str += """<tr class=tr1><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td class="border1"> TOTAL </td><td class="border1">""" + self.e1.get() + """</td><td class="border1">""" + self.e2.get() + """</td><td class="border1">""" + self.e3.get() + """</td></tr>
		</table>
		</body>
		</html> 
		"""

		Html_file= open("rapp.html","w")
		Html_file.write(html_str)
		Html_file.close()
		webbrowser.open("rapp.html");

	def quitApp(self):
		"""
		This method was created for properly shutting down
		the application. And for the database to close properly.
		"""
		if self.database:
			self.cur.close()
			self.database.close()
			print('Database has been closed.')
		self.root.update()
		self.root.deiconify()
		self.root.state("zoomed")
		self.destroy()
class tool():
	def __init__(self):
		pass
	def convert(self,st):
		s = str(st)
		p = int(s.find('.'))
		if p == -1 :
			return s + ',000'
		else: 
			sv= s[:p] + ',' + s[p+1:]
		if p < len(sv)-3 :
			return sv[0:p+4]
		else :
			sv+='0' * (3 -( len(sv)-1-p))
			return sv
	def reconvert(self,s):
		p = int(s.find(','))
		if p == -1 :
			return s
		else :
			sf = s[:p] + '.' + s[p+1:]
			return sf
tl=tool()
class SearchCmd(tk.Toplevel):

	def __init__(self, master,field,validOnly=False):
		"""
		Initialize the graphics user interface for stock reporting.
		"""
		tk.Toplevel.__init__(self, master)
		self.root = master
		self.field =field
		self.validOnly = validOnly
		self.title('Recherche Commande')
		# Set the window icon.
		self.iconlocation = os.getcwd() + "/tsicon.ico"
		try:
			self.iconbitmap(self.iconlocation)
		except:
			pass

		# Initialize the database.
		self.database = sqlite3.connect('quinc.db')
		self.cur = self.database.cursor()
	
		# Create container for the treeview and scrollbar.
		display_frame = tk.Frame(self)
		display_frame.grid(row=0, column=0,sticky='wens',padx=10,pady=10)		
		display_frame1 = tk.Frame(self)
		display_frame1.grid(row=1, column=0,sticky='wens',padx=10,pady=10)
		
		lb1 = ttk.Label(display_frame, text='Client: ')
		lb1.grid(row=1, column=1,sticky='e')
		self.e1 = ttk.Entry(display_frame,justify ='center')
		self.e1.grid(row=1, column=2,sticky='w')
		self.e1.bind('<KeyPress>',self.searchByClient)
		self.periodCbx  = ttk.Combobox(display_frame, width=17,values = ["Aujourd'hui",'Ce mois','Tout'])
		self.periodCbx.grid(row=1, column=0, padx=10, pady=10,sticky='w')
		self.periodCbx.set("Aujourd'hui")
		self.periodCbx.bind('<<ComboboxSelected>>',self.insertDetails)
		self.periodCbx.bind('<KeyPress>',self.searchByDate)
		# Create a tkinter.ttk treeview.
		self.treeview = ttk.Treeview(display_frame1)
		self.treeview.grid(row=0, column=0,sticky='wens')
		self.treeview.bind('<ButtonRelease-1>', self.selectCmd)
		# Create a scrollbar for the treeview.
		yscrollbar = tk.Scrollbar(display_frame1)
		yscrollbar.grid(row=0, column=1,sticky="ns")
		yscrollbar.config(command=self.treeview.yview)
		self.treeview.config(yscrollcommand=yscrollbar.set)

		# Initialize column and heading variable.
		self.headers = ('N° commande','Client','date','validée')
		self.column = ('NumCmd','Client','date','validee')
		# Set the column of the tree.
		self.treeview['columns'] = self.column

		# Set the heading of the tree and the width of each column.
		counter = 0
		self.treeview.heading('#0', text='S. No.')
		self.treeview.column('#0', width=40)
		for head in self.column:
			self.treeview.heading(head, text=self.headers[counter])
			self.treeview.column(head,anchor="c", width=180)
			counter += 1
			
		# Create tags for treeview.
		self.treeview.tag_configure('evenrow', background='#d5d5d5')
		self.treeview.tag_configure('oddrow', background='#f7f7f7')

		# Insert the details to the tree.
		self.insertDetails()
		
		self.grid_rowconfigure(1, weight=1)
		for x in range(1):
			self.grid_columnconfigure(x, weight=1)		
			
		for x in range(5):
			display_frame.grid_columnconfigure(x, weight=1)
			
		display_frame1.grid_rowconfigure(0, weight=1)
		display_frame1.grid_columnconfigure(0, weight=1)
	def searchByClient(self,event):
		item = self.e1.get()
		if event.char.isalpha() or event.char.isnumeric():
			item +=  str(event.char)
		if event.keysym == 'BackSpace':
			item = item[:-1]
		self.insertDetails(client=item)	
	def searchByDate(self,event):
		item = self.periodCbx.get()
		if event.char.isalpha() or event.char.isnumeric():
			item +=  str(event.char)
		if event.keysym == 'BackSpace':
			item = item[:-1]
		self.insertDetails(date=item)
	def insertDetails(self,event=None,client="",date=""):

		for c in self.treeview.get_children() :
			self.treeview.delete(c)
		today = datetime.strftime(datetime.now(),'%y-%m-%d')
		if self.periodCbx.get() == "Aujourd'hui" :
			dt = today [:8]
		elif self.periodCbx.get() == "Ce mois":
			dt = today[:5]
		elif self.periodCbx.get() == "Tout":
			dt = ""
		elif self.periodCbx.get() !="":
			if date !="":
				dt = date
			else:
				dt =self.periodCbx.get()
		# Combine incoming and outgoing material
		req = "SELECT c.idcmd,c.client,c.date,c.validee from commande c where c.date like ? and c.client like ?"
		if self.validOnly :
			req += " and c.validee = 1 "
		table = self.cur.execute(req,('{}%'.format(dt),'{}%'.format(client),))
		data= table.fetchall()

		counter = 0
		if len(data) > 0:
			for num in data:
				if counter % 2 == 0:
					self.treeview.insert('','end',str(counter),text=str(counter),tag='evenrow')
				else:
					self.treeview.insert('','end',str(counter),text=str(counter),tag='oddrow')
				self.treeview.set(str(counter), self.column[0], str(num[0]))
				self.treeview.set(str(counter), self.column[1], str(num[1]))
				self.treeview.set(str(counter), self.column[2], str(num[2]))
				if num[3]==1 :
					v = 'oui'
				else : 
					v= 'non'
				self.treeview.set(str(counter), self.column[3], str(v))
				counter+=1
	def selectCmd(self,event):
		curItem = self.treeview.focus()
		row = self.treeview.item(curItem)['values']
		if row !='':
			self.field.delete('0','end')
			self.field.insert('0',row[0])
			self.master.getCmdList()
			self.destroy()
class MainWindow(tk.Frame):

	def __init__(self, master):
		"""
		Initialize the graphics user interface for the main window of
		the application. It consist of menubar and 4 buttons for item
		master, incoming and outgoing transaction, and stock report.
		"""

		tk.Frame.__init__(self, master)
		self.master.state('zoomed')
		# Set the title and position of the window.
		self.master.title(" ".join([__appname__, __version__]))
		# self.master.protocol('WM_DELETE_WINDOW', self.quitApp)
		self.grid(row=0,column=0, padx=5, pady=5,sticky='wens')
		self.iconlocation = os.getcwd() + "/tsicon.ico"
		try:
			self.master.iconbitmap(self.iconlocation)
		except:
			pass
		upperfrm = ttk.LabelFrame(self)
		upperfrm.grid(row=0, column=0,sticky="we")
		bottomfrm = tk.Frame(self)
		bottomfrm.grid(row=1, column=0,sticky="wens")
		self.ttl = tk.Label(upperfrm, text='QUINCAILLERIE RAMI MLAWAH',font='Helvetica 20 bold')
		self.ttl.grid(row = 0,column = 0,sticky='wens',columnspan=4)
		# Create menu bar of the main window.
		self.menubar = tk.Menu(self)
		self.master.config(menu=self.menubar)
		self.filemenu = tk.Menu(self.menubar, tearoff=0)
		self.helpmenu = tk.Menu(self.menubar, tearoff=0)
		self.optionmenu = tk.Menu(self.menubar, tearoff=0)
		self.menubar.add_cascade(label='File', menu=self.filemenu)
		self.menubar.add_cascade(label='Option', menu=self.optionmenu)
		self.menubar.add_cascade(label='Help', menu=self.helpmenu)
		self.filemenu.add_command(label='Quit', command=self.quitApp)
		self.helpmenu.add_separator()
		self.helpmenu.add_command(label='About', command=self.aboutDialog)
		self.optionmenu.add_command(label='Changer mot de passe',command=self.changePass)
		# Create 4 buttons for item master, incoming, outgoing, and reports.
		# helv36 = tk.Font(family='Helvetica', size=36, weight='bold')
		self.master_btn = tk.Button(bottomfrm, text='Produits',
										  command=self.itemMaster,font='Helvetica 16 bold'
										  )
		self.master_btn.grid(row=0, column=0,sticky="we",padx=40,pady=40)
		self.incoming_btn = tk.Button(bottomfrm, text='Achat',
									   command=self.incoming,font='Helvetica 16 bold')
		self.incoming_btn.grid(row=0, column=1,sticky="we",padx=40,pady=40)
		self.outgoing_btn = tk.Button(bottomfrm, text='Vente',
									   command=self.outgoing,font='Helvetica 16 bold')
		self.outgoing_btn.grid(row=0, column=2,sticky="we",padx=40,pady=40)
		self.ret_btn = tk.Button(bottomfrm, text='Retour',
									   command=self.retour,font='Helvetica 16 bold')
		self.ret_btn.grid(row=0, column=3,sticky="we",padx=40,pady=40)
		self.report_btn = tk.Button(bottomfrm, text='Rapports',
									 command=self.showReport,font='Helvetica 16 bold')
		self.report_btn.grid(row=0, column=4,sticky="we",padx=40,pady=40)

		# Check whether database is available
		# if not create database and tables.
		self.cur =None
		if not os.path.isfile('quinc.db'):
			self.createDB()
			self.psw = "0000"
		else:
			self.database = sqlite3.connect('quinc.db')
			self.cur = self.database.cursor()
			try :
				rq=self.cur.execute("select password from admin where id = 1")
				d=rq.fetchall()
				self.psw = d[0][0]
			except :
				tk.messagebox.showwarning('avertissement',"un erreur s'est produit")
		self.master.grid_columnconfigure(0, weight=1)
		self.master.grid_rowconfigure(0, weight=1)
		self.grid_rowconfigure(1, weight=1)
		for x in range(1):
			self.grid_columnconfigure(x, weight=1)
		for x in range(1):
			upperfrm.grid_columnconfigure(1, weight=1)
		for x in range(1):
			bottomfrm.grid_rowconfigure(x, weight=1)
		for x in range(5):
			bottomfrm.grid_columnconfigure(x, weight=1)
			
		# if askstring('Authentification','Entrer le mot de passe') != self.psw :
			# self.quitApp()
	def createDB(self):
			# Initialize the database.
		self.database = sqlite3.connect('quinc.db')
		# self.database.set_trace_callback(print)
		self.cur = self.database.cursor()
		# Create item table.
		self.cur.execute("""
						CREATE TABLE 'produit' (
							'ref'	TEXT,
							'designation'	TEXT,
							'unite'	TEXT,
							'quantite'	INTEGER DEFAULT 0,
							'pachat'	INTEGER,
							'pvente'	INTEGER,
							'fournisseur'	TEXT,
							'remarque'	TEXT,
							PRIMARY KEY('ref')
						);
			""")
		self.cur.execute("""
						CREATE TABLE `retour` (
							`rowid`	INTEGER PRIMARY KEY AUTOINCREMENT,
							`quantite`	INTEGER,
							`remise`	INTEGER DEFAULT 0,
							`date`	TEXT,
							`idprod`	TEXT,
							FOREIGN KEY(`idprod`) REFERENCES `produit`(`ref`)
						);
			""")
		# Create incoming transaction table.
		self.cur.execute("""
						CREATE TABLE 'commande' (
							'idcmd'	TEXT,
							'date'	TEXT,
							'validee'	INTEGER DEFAULT 0,
							'client' TEXT,
							PRIMARY KEY('idcmd')
						);
			""")		
		self.cur.execute("""
						CREATE TABLE 'admin' (
							'id' INTEGER,
							'password'	TEXT,
							PRIMARY KEY('id')
						);
			""")
		# Create outgoing transaction table.
		self.cur.execute("""
						CREATE TABLE 'vente' (
							'rowid'	INTEGER PRIMARY KEY AUTOINCREMENT,
							'quantite'	INTEGER,
							'remise'	INTEGER,
							'idprod'	TEXT,
							'idcmd'	TEXT,
							FOREIGN KEY('idprod') REFERENCES 'produit'('ref'),
							FOREIGN KEY('idcmd') REFERENCES 'commande'('idcmd')
						);
			""")
		self.cur.execute("""CREATE TABLE `achat` (
							`rowid`	INTEGER PRIMARY KEY AUTOINCREMENT,
							`quantite`	INTEGER,
							`date`	TEXT,
							`idprod`	TEXT,
							FOREIGN KEY(`idprod`) REFERENCES `produit`(`ref`)
						);""")
		self.cur.execute("""
						INSERT INTO admin VALUES (1,'0000');
			""")
		# Apply the changes.
		try:
			self.database.commit()
		except sqlite3.Error:
			self.database.rollback()
	


	def aboutDialog(self):
		"""
		This is where you can find the details of the application
		including the name of the app, version, author, email of
		the author, website and license.
		"""
		AboutDialog(self)

	def itemMaster(self):
		"""
		This method is for adding new items into the database to use
		in the application.
		"""
		if askstring('Authentification','Entrer le mot de passe') == self.psw :
			self.master.withdraw()
			ItemMaster(self.master)

	def incoming(self):
		"""
		This method is for incoming transactions like deliveries or even
		stock adjustments.
		"""
		if askstring('Authentification','Entrer le mot de passe') == self.psw :
			self.master.withdraw()
			ItemIn(self.master)


	def outgoing(self):
		"""
		This method is for outgoing transactions like issues/sales or even
		stock adjustments.
		"""

		self.master.withdraw()
		ItemOut(self.master)
			
	def retour(self):
		"""
		This method is for outgoing transactions like issues/sales or even
		stock adjustments.
		"""

		self.master.withdraw()
		ItemIn(self.master,type="retour")
		


	def showReport(self):
		"""
		This method is for showing the user the stock reports for monitoring
		purposes.
		"""
		if askstring('Authentification','Entrer le mot de passe') == self.psw :
			self.master.withdraw()
			Reports(self.master)
	def changePass(self):
		if askstring('Authentification','Entrer le mot de passe') == self.psw :
			newpass= askstring('Changement de mot de passe','Nouveau mot de passe')
			if newpass is not None :
				self.cur.execute("update admin set password=? where id=1",(newpass,))
				try:
					self.database.commit()
					self.psw = newpass
					tk.messagebox.showinfo('Information',"Mot de passe modifié avec succès")
					
				except sqlite3.Error:
					self.database.rollback()
					tk.messagebox.showerror(sqlite3.Error)
					
	def quitApp(self):
	
		if self.database:
			self.cur.close()
			self.database.close()
			print('Database has been closed.')
		self.master.destroy()


def main():
	app = tk.Tk()
	a   = MainWindow(app)
	app.mainloop()

if __name__ == '__main__':
	main()
