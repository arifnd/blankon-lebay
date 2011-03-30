#!/usr/bin/python

#prototype lebay
#edit terakhir 300311
#zerosix06 at gmail dot com

import pygtk
pygtk.require('2.0')
import gtk
import os
import gconf
#import sys
#from PIL import Image

HOME = os.path.expanduser('~')
DAEMONFILE = HOME+"/.config/autostart/blankon-contextual-desktop-daemon.desktop"
#DAEMONFILE = "blankon-contextual-desktop-daemon.desktop"
THEMEDIR = "/usr/share/blankon-contextual-desktop/theme/"
ACTIVEITEM = None
COL_PATH = 0
COL_PIXBUF = 1
COL_IS_DIRECTORY = 2


class LebayApp:
	def auto_start(self, widget):
		status = widget.get_active()
		
		if status:
			before = "X-GNOME-Autostart-enabled=false"
			after = "X-GNOME-Autostart-enabled=true"
		else:
			before = "X-GNOME-Autostart-enabled=true"
			after = "X-GNOME-Autostart-enabled=false"
		
		file = open(DAEMONFILE, "r")
		text = file.read()
		file.close()
		file = open(DAEMONFILE, "w")
		file.write(text.replace(before,after))
		file.close()
	
	def auto_status(self):
		lastLine = file(DAEMONFILE, "r").readlines()[-1]
		textValue = lastLine.split("=")
		if textValue[1] == 'true\n':
			return True
		else:
			return False
	
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
		filter.add_mime_type("image/jpeg")
		filter.add_mime_type("image/gif")
		filter.add_pattern("*.png")
		filter.add_pattern("*.jpg")
		filter.add_pattern("*.gif")
		filter.add_pattern("*.tif")
		filter.add_pattern("*.xpm")
		dialog.add_filter(filter)

		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			self.teks.set_text(dialog.get_filename())
			self.preview.set_from_file(dialog.get_filename())
		dialog.destroy()
		
	def change_pos(self, widget, data):
		widget.set_sensitive(False)
		self.activePos.set_sensitive(True)
		self.activePos = widget
		parm = data.split(".")
		wall = self.client.get_string ("/apps/blankon-desktop/context/"+parm[0]+"/themes/"+self.theme+"/"+parm[1])
		thum = gtk.gdk.pixbuf_new_from_file_at_size(wall,320,-1)
		self.preview.set_from_pixbuf(thum)
		self.teks.set_text(wall)
	
	def create_store(self):
		store = gtk.ListStore(str, gtk.gdk.Pixbuf, bool)
		store.set_sort_column_id(COL_PATH, gtk.SORT_ASCENDING)
		return store
		
	def change_theme(self, widget, item):
		model = widget.get_model()
		path = model[item][COL_PATH]
		print path
		
	def fill_store(self):
		self.store.clear()
		if THEMEDIR == None:
			return
		
		for fl in os.listdir(THEMEDIR):
			if not fl[0] == '.':
				if os.path.isdir(os.path.join(THEMEDIR, fl)):
					self.store.append([fl, gtk.gdk.pixbuf_new_from_file_at_size(THEMEDIR+fl+"/time/dawn.png",180,-1), True])
					
	def __init__(self):
		window = gtk.Window(gtk.WINDOW_TOPLEVEL)
		window.connect("delete_event", gtk.main_quit) #error variabel
		window.set_size_request(480,500) #ukuran window
		window.set_border_width(10) #padding
		window.set_position(gtk.WIN_POS_CENTER) #posisi window
		window.set_title("Lebay") #judul
		
		try:
			window.set_icon_from_file("lebay.png") #icon
		except Exception, e:
			print e.message
			sys.exit(1)
		
		self.client = gconf.client_get_default()
		self.theme = self.client.get_string ("/apps/blankon-desktop/context/time/theme")
		themeFirst = self.client.get_string ("/apps/blankon-desktop/context/time/themes/"+self.theme+"/dawn")
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
		themeView.set_selection_mode(gtk.SELECTION_SINGLE)
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
		test = gtk.gdk.pixbuf_new_from_file_at_size(themeFirst,320,-1)
		self.preview.set_from_pixbuf(test)
		wallTable.attach(self.preview,1,3,0,13)
		
		self.teks = gtk.Entry()
		wallTable.attach(self.teks,1,2,15,16)
		
		browseButton = gtk.Button("Atur")
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
		
		aktif = gtk.CheckButton("Activate BlankOn Contextual Desktop")
		aktif.set_active(self.auto_status())
		aktif.connect("toggled", self.auto_status)
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
		
def main():
	gtk.main()
	return 0
	
if __name__ == "__main__":
	LebayApp()
	main()
