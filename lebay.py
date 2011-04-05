#!/usr/bin/python

#prototype lebay
#edit terakhir 050411
#zerosix06 at gmail dot com

import pygtk
pygtk.require('2.0')
import gtk
import os
import gconf
import sys
import commands
import signal

HOME = os.path.expanduser('~')
APP = "blankon-contextual-desktop-daemon"
DAEMONMASTER = "/etc/xdg/autostart/"+APP+".desktop"
DAEMONFILE = HOME+"/.config/autostart/"+APP+".desktop"
THEMEDIR = "/usr/share/blankon-contextual-desktop/theme/"
COL_PATH = 0
COL_PIXBUF = 1

class LebayApp(object):
	def app_kill(self):
		output = commands.getoutput("ps -A -o pid,cmd | grep "+APP)
		out = output.split('\n')[0]
		pid = out.split(' ')[1]
		os.kill(int(pid.strip()),signal.SIGHUP)
	
	def app_run(self):
		os.system(APP+" 1>/dev/null &")
		
	def app_status(self):
		output = commands.getoutput("ps -A -o cmd | grep -x "+APP)
		return output == APP
	
	def auto_start(self, widget):
		status = widget.get_active()
		
		if status:
			before = "X-GNOME-Autostart-enabled=false"
			after = "X-GNOME-Autostart-enabled=true"
			if not self.app_status():
				self.app_run()
		else:
			before = "X-GNOME-Autostart-enabled=true"
			after = "X-GNOME-Autostart-enabled=false"
			if not self.exists(DAEMONFILE):
				os.system("cp %s %s" % (DAEMONMASTER, DAEMONFILE))
				fout = open(DAEMONFILE, "a")
				fout.write(after)
				fout.close()
			
			if self.app_status():
				self.app_kill()
		
		if self.exists(DAEMONFILE):
			file = open(DAEMONFILE, "r")
			text = file.read()
			file.close()
			file = open(DAEMONFILE, "w")
			file.write(text.replace(before,after))
			file.close()
	
	def auto_status(self):
		if self.exists(DAEMONFILE):
			lastLine = file(DAEMONFILE, "r").readlines()[-1]
			textValue = lastLine.split("=")
			if textValue[1].strip() == 'true':
				if not self.app_status():
					self.app_run()
				return True
			else:
				if self.app_status():
					self.app_kill()
				return False
		else:
			if not self.app_status():
				self.app_run()
			return True
	
	def browse_image(self, widget):
		if gtk.pygtk_version < (2,3,90):
			print "PyGtk 2.3.90 or later required for this example"
			raise SystemExit

		dialog = gtk.FileChooserDialog("Open..",
                               None,
                               gtk.FILE_CHOOSER_ACTION_OPEN,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		dialog.set_default_response(gtk.RESPONSE_OK)

		filter = gtk.FileFilter()
		filter.set_name("Images")
		filter.add_mime_type("image/png")
		filter.add_pattern("*.png")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.teks.set_text(dialog.get_filename())
			self.preview.set_from_pixbuf(self.thum_image(dialog.get_filename(),320))
			parm = self.activeWall.split(".")
			self.client.set_string("/apps/blankon-desktop/context/"+parm[0]+"/themes/"+self.theme+"/"+parm[1], dialog.get_filename())
		dialog.destroy()
		
	def change_pos(self, widget, data):
		widget.set_sensitive(False)
		self.activePos.set_sensitive(True)
		self.activePos = widget
		parm = data.split(".")
		wall = self.client.get_string("/apps/blankon-desktop/context/"+parm[0]+"/themes/"+self.theme+"/"+parm[1])
		self.preview.set_from_pixbuf(self.thum_image(wall,320))
		self.teks.set_text(wall)
		self.activeWall = data
		print self.app_status()
	
	def create_store(self):
		store = gtk.ListStore(str, gtk.gdk.Pixbuf, bool)
		store.set_sort_column_id(COL_PATH, gtk.SORT_ASCENDING)
		return store
		
	def change_theme(self, widget):
		item = widget.get_cursor()
		model = widget.get_model()
		path = model[item[0]][COL_PATH]
		self.theme = path
		parm = self.activeWall.split(".")
		wall = self.client.get_string("/apps/blankon-desktop/context/"+parm[0]+"/themes/"+self.theme+"/"+parm[1])
		self.teks.set_text(wall)
		self.preview.set_from_pixbuf(self.thum_image(wall,320))
		#self.client.set_string("/apps/blankon-desktop/context/time/theme", path)
		
	def exists(self, filename):
		try:
			f = open(filename)
			f.close()
			return True
		except:
			return False
	
	def fill_store(self):
		self.store.clear()
		if THEMEDIR is None:
			return
		
		for fl in os.listdir(THEMEDIR):
			if not fl[0] == '.':
				if os.path.isdir(os.path.join(THEMEDIR, fl)):
					self.store.append([fl, self.thum_image(THEMEDIR+fl+"/time/dawn.png",180), True])
	
	def default_key(self, widget):
		parm = self.activeWall.split(".")
		defaultWall = THEMEDIR+self.theme+"/"+parm[0]+"/"+parm[1]+".png"
		self.client.set_string("/apps/blankon-desktop/context/"+parm[0]+"/themes/"+self.theme+"/"+parm[1], defaultWall)
		self.preview.set_from_pixbuf(self.thum_image(defaultWall,320))
		self.teks.set_text(defaultWall)
	
	def thum_image(self, dir, width):
		return gtk.gdk.pixbuf_new_from_file_at_size(dir,width,-1)
		
	def __init__(self):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.set_size_request(480,500) #ukuran window
		window.set_border_width(10) #padding
		window.set_position(gtk.WIN_POS_CENTER) #posisi window
		window.set_title("Lebay") #judul
		window.connect("delete_event", gtk.main_quit)
		
		try:
			window.set_icon_from_file("lebay.png") #icon
		except Exception, e:
			print e.message
			sys.exit(1)
		
		self.client = gconf.client_get_default()
		self.theme = self.client.get_string("/apps/blankon-desktop/context/time/theme")
		themeFirst = self.client.get_string("/apps/blankon-desktop/context/time/themes/"+self.theme+"/dawn")
		self.store = self.create_store()
		self.fill_store()
		
		mainTable = gtk.Table(3,2,False)
		mainTable.set_row_spacings(5)
		tab = gtk.Notebook()
		tab.set_tab_pos(gtk.POS_TOP)
		mainTable.attach(tab,0,2,0,1)
		
		#halaman tema
		themeView = gtk.IconView(self.store)
		themeView.set_size_request(430,400)
		themeView.set_selection_mode(gtk.SELECTION_MULTIPLE)
		themeView.set_text_column(COL_PATH)
		themeView.set_pixbuf_column(COL_PIXBUF)
		themeView.connect("selection-changed", self.change_theme)
		
		themeScroll = gtk.ScrolledWindow()
		themeScroll.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		themeScroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		themeScroll.add(themeView)
		
		themeTable = gtk.Table()
		themeTable = gtk.Table(1,1,False)
		themeTable.set_border_width(10)
		themeTable.attach(themeScroll,0,1,0,1)
		
		label = gtk.Label("Theme") #judul tab
		tab.append_page(themeTable, label)
		
		#halaman latar
		wallTable = gtk.Table(16,3,False)
		wallTable.set_border_width(10)
		wallTable.set_col_spacings(10)
		
		self.preview = gtk.Image()
		self.preview.set_size_request(320,-1)
		self.preview.set_from_pixbuf(self.thum_image(themeFirst,320))
		wallTable.attach(self.preview,1,3,0,14)
		
		self.teks = gtk.Entry()
		self.teks.set_text(themeFirst)
		wallTable.attach(self.teks,1,3,14,15)
		
		defaultButton = gtk.Button("_Default")
		defaultButton.connect("clicked", self.default_key)
		wallTable.attach(defaultButton,1,2,15,16)
		
		browseButton = gtk.Button("_Browse")
		browseButton.connect("clicked", self.browse_image)
		wallTable.attach(browseButton,2,3,15,16)
		
		waktu = gtk.Label("Time")
		wallTable.attach(waktu,0,1,0,1)
		
		dawn = gtk.Button("Dawn")
		dawn.set_sensitive(False)
		dawn.connect("clicked", self.change_pos, "time.dawn")
		wallTable.attach(dawn,0,1,1,2)
		
		morning = gtk.Button("Morning")
		morning.connect("clicked", self.change_pos, "time.morning")
		wallTable.attach(morning,0,1,2,3)
		
		noon = gtk.Button("Noon")
		noon.connect("clicked", self.change_pos, "time.noon")
		wallTable.attach(noon,0,1,3,4)
		
		afternoon = gtk.Button("Afternoon")
		afternoon.connect("clicked", self.change_pos, "time.afternoon")
		wallTable.attach(afternoon,0,1,4,5)
		
		evening = gtk.Button("Evening")
		evening.connect("clicked", self.change_pos, "time.evening")
		wallTable.attach(evening,0,1,5,6)
		
		midnight = gtk.Button("Midnight")
		midnight.connect("clicked", self.change_pos, "time.midnight")
		wallTable.attach(midnight,0,1,6,7)
		
		waktu = gtk.Label()
		wallTable.attach(waktu,0,1,7,8)
		
		waktu = gtk.Label("Weather")
		wallTable.attach(waktu,0,1,8,9)
		
		cloud = gtk.Button("Cloud")
		cloud.connect("clicked", self.change_pos, "weather.cloud")
		wallTable.attach(cloud,0,1,9,10)
		
		fog = gtk.Button("Fog")
		fog.connect("clicked", self.change_pos, "weather.fog")
		wallTable.attach(fog,0,1,10,11)
		
		rain = gtk.Button("Rain")
		rain.connect("clicked", self.change_pos, "weather.rain")
		wallTable.attach(rain,0,1,11,12)
		
		snow = gtk.Button("Snow")
		snow.connect("clicked", self.change_pos, "weather.snow")
		wallTable.attach(snow,0,1,12,13)
		
		strom = gtk.Button("Strom")
		strom.connect("clicked", self.change_pos, "weather.storm")
		wallTable.attach(strom,0,1,13,14)
		
		sun = gtk.Button("Sun")
		sun.connect("clicked", self.change_pos, "weather.sun")
		wallTable.attach(sun,0,1,14,15)
		
		suncloud = gtk.Button("Suncloud")
		suncloud.connect("clicked", self.change_pos, "weather.suncloud")
		wallTable.attach(suncloud,0,1,15,16)
		
		label = gtk.Label("Wallpaper")
		tab.insert_page(wallTable,label)	
		
		aktif = gtk.CheckButton("_Activate BlankOn Contextual Desktop")
		aktif.set_active(self.auto_status())
		aktif.connect("toggled", self.auto_start)
		mainTable.attach(aktif,0,1,1,2)
		
		halign = gtk.Alignment(1, 0, 0, 0)
		tutup = gtk.Button(stock='gtk-close')
		tutup.set_size_request(70, 30)
		tutup.connect("clicked", gtk.main_quit)
		halign.add(tutup)
		mainTable.attach(halign,1,2,1,2)
		
		window.add(mainTable)
		window.show_all()
		
		self.activePos = dawn
		self.activeWall = "time.dawn"
		
def main():
	gtk.main()
	return 0
	
if __name__ == "__main__":
	LebayApp()
	main()
